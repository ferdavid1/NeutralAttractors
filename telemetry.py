"""
Telemetry Extraction Module

This module implements the telemetry extraction framework described in Section 4
of "Dynamical System Modeling of Super Smash Bros. Melee". It extracts neutral
game spacing distances from .slp replay files using the py-slippi library.

Reference: Section 4.2 - Python Implementation for Telemetry Extraction
"""

import os
import math
from typing import List, Tuple, Optional
from slippi import Game


# Define the acceptable internal Action State IDs for neutral gameplay
# Ranges 0-21 and 24-33 capture all standard locomotion, jumps, and idle states
NEUTRAL_STATES = set(list(range(0, 22)) + list(range(24, 34)))


def is_neutral(post_frame_1, post_frame_2) -> bool:
    """
    Evaluates whether a specific frame qualifies as a neutral interaction.
    Both agents must simultaneously occupy a neutral state to qualify the frame.

    Args:
        post_frame_1: Post-frame data for player 1
        post_frame_2: Post-frame data for player 2

    Returns:
        bool: True if both players are in neutral states
    """
    return (post_frame_1.state in NEUTRAL_STATES and
            post_frame_2.state in NEUTRAL_STATES)


def calculate_euclidean_distance(p1_x: float, p1_y: float,
                                 p2_x: float, p2_y: float) -> float:
    """
    Calculates the 2D spatial magnitude between the two Root Bones.
    This serves as the primary state variable D(t) on the relative manifold.

    Args:
        p1_x: Player 1 x-coordinate (Root Bone)
        p1_y: Player 1 y-coordinate (Root Bone)
        p2_x: Player 2 x-coordinate (Root Bone)
        p2_y: Player 2 y-coordinate (Root Bone)

    Returns:
        float: Euclidean distance between the two Root Bones
    """
    return math.sqrt((p1_x - p2_x)**2 + (p1_y - p2_y)**2)


def extract_neutral_distances(replay_dir: str) -> List[float]:
    """
    Parses a directory of .slp files and extracts a continuous array
    of neutral spacing distances for stochastic modeling.

    Args:
        replay_dir: Path to directory containing .slp replay files

    Returns:
        List[float]: Array of neutral spacing distances
    """
    neutral_distances = []

    # Iterate through all replay files in the target directory
    for filename in os.listdir(replay_dir):
        if not filename.endswith('.slp'):
            continue

        try:
            # Initialize the parser for the specific game file
            game = Game(os.path.join(replay_dir, filename))

            # Iterate over the parsed frames sequentially
            for frame in game.frames:
                # Filter valid ports containing active player data
                ports = [p for p in frame.ports if p is not None]
                if len(ports) < 2:
                    continue

                # Extract post-frame telemetry for the primary characters
                p1, p2 = ports[0].leader.post, ports[1].leader.post

                # If the frame satisfies the neutral boundary conditions
                if is_neutral(p1, p2):
                    dist = calculate_euclidean_distance(
                        p1.position.x, p1.position.y,
                        p2.position.x, p2.position.y
                    )
                    neutral_distances.append(dist)

        except Exception as e:
            # Silently pass malformed, incomplete, or corrupted replay files
            pass

    return neutral_distances


def extract_full_telemetry(replay_dir: str) -> Tuple[List[dict], List[dict]]:
    """
    Extracts complete telemetry data including positions, velocities, and states
    for both players across all frames in neutral game.

    Args:
        replay_dir: Path to directory containing .slp replay files

    Returns:
        Tuple containing lists of telemetry dictionaries for player 1 and player 2
    """
    player1_data = []
    player2_data = []

    for filename in os.listdir(replay_dir):
        if not filename.endswith('.slp'):
            continue

        try:
            game = Game(os.path.join(replay_dir, filename))

            # Store previous positions for velocity calculation
            prev_p1_pos = None
            prev_p2_pos = None

            for frame_idx, frame in enumerate(game.frames):
                ports = [p for p in frame.ports if p is not None]
                if len(ports) < 2:
                    continue

                # Check if both ports have leader data
                if not (hasattr(ports[0], 'leader') and hasattr(ports[1], 'leader')):
                    continue
                if not (ports[0].leader and ports[1].leader):
                    continue
                if not (hasattr(ports[0].leader, 'post') and hasattr(ports[1].leader, 'post')):
                    continue

                p1, p2 = ports[0].leader.post, ports[1].leader.post

                # Calculate velocities from position differences
                if prev_p1_pos is not None:
                    velocity_x_p1 = p1.position.x - prev_p1_pos[0]
                    velocity_y_p1 = p1.position.y - prev_p1_pos[1]
                else:
                    velocity_x_p1 = 0.0
                    velocity_y_p1 = 0.0

                if prev_p2_pos is not None:
                    velocity_x_p2 = p2.position.x - prev_p2_pos[0]
                    velocity_y_p2 = p2.position.y - prev_p2_pos[1]
                else:
                    velocity_x_p2 = 0.0
                    velocity_y_p2 = 0.0

                prev_p1_pos = (p1.position.x, p1.position.y)
                prev_p2_pos = (p2.position.x, p2.position.y)

                if is_neutral(p1, p2):
                    # Extract player 1 data
                    player1_data.append({
                        'frame': frame_idx,
                        'position_x': p1.position.x,
                        'position_y': p1.position.y,
                        'velocity_x': velocity_x_p1,
                        'velocity_y': velocity_y_p1,
                        'state': p1.state,
                        'state_age': p1.state_age,
                        'direction': p1.direction,
                        'airborne': p1.airborne,
                        'hit_stun': p1.hit_stun if hasattr(p1, 'hit_stun') else 0
                    })

                    # Extract player 2 data
                    player2_data.append({
                        'frame': frame_idx,
                        'position_x': p2.position.x,
                        'position_y': p2.position.y,
                        'velocity_x': velocity_x_p2,
                        'velocity_y': velocity_y_p2,
                        'state': p2.state,
                        'state_age': p2.state_age,
                        'direction': p2.direction,
                        'airborne': p2.airborne,
                        'hit_stun': p2.hit_stun if hasattr(p2, 'hit_stun') else 0
                    })

        except Exception as e:
            # Print first exception for debugging
            if len(player1_data) == 0 and len(player2_data) == 0:
                print(f"Warning: Error parsing {filename}: {e}")
            pass

    return player1_data, player2_data


def calculate_relative_velocity(p1_data: dict, p2_data: dict) -> float:
    """
    Calculates the relative closing velocity V_rel(t) between two players.

    Args:
        p1_data: Player 1 telemetry dictionary
        p2_data: Player 2 telemetry dictionary

    Returns:
        float: Relative closing velocity (positive = approaching)
    """
    dx = p1_data['position_x'] - p2_data['position_x']
    dy = p1_data['position_y'] - p2_data['position_y']
    dvx = p1_data['velocity_x'] - p2_data['velocity_x']
    dvy = p1_data['velocity_y'] - p2_data['velocity_y']

    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        return 0.0

    # Projection of velocity difference onto position difference
    v_rel = -(dx * dvx + dy * dvy) / distance

    return v_rel
