"""
Relative Manifold Projection Module

This module implements the mathematical formulation of the relative state space
as described in Section 9 of "Dynamical System Modeling of Super Smash Bros. Melee".

Reference: Section 9 - Mathematical Formulation of the Relative State Space
"""

import numpy as np
from typing import List, Tuple, Dict


class RelativeManifold:
    """
    Projects high-dimensional game state into a reduced-order relative manifold.

    The primary state variable D(t) represents the Euclidean distance between
    Root Bones. The secondary variable V_rel(t) represents the relative closing velocity.
    """

    def __init__(self, player1_data: List[Dict], player2_data: List[Dict]):
        """
        Initialize the relative manifold from player telemetry data.

        Args:
            player1_data: List of telemetry dictionaries for player 1
            player2_data: List of telemetry dictionaries for player 2
        """
        self.player1_data = player1_data
        self.player2_data = player2_data
        self.distances = []
        self.closing_velocities = []
        self.timestamps = []

        self._project_to_manifold()

    def _project_to_manifold(self):
        """
        Projects the 8-dimensional state space onto the relative manifold M.
        """
        for p1, p2 in zip(self.player1_data, self.player2_data):
            # Calculate D(t) - Euclidean distance
            dx = p1['position_x'] - p2['position_x']
            dy = p1['position_y'] - p2['position_y']
            distance = np.sqrt(dx**2 + dy**2)

            # Calculate V_rel(t) - relative closing velocity
            dvx = p1['velocity_x'] - p2['velocity_x']
            dvy = p1['velocity_y'] - p2['velocity_y']

            if distance > 0:
                # Projection of velocity difference onto position difference
                v_rel = -(dx * dvx + dy * dvy) / distance
            else:
                v_rel = 0.0

            self.distances.append(distance)
            self.closing_velocities.append(v_rel)
            self.timestamps.append(p1['frame'])

    def get_phase_portrait(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the phase portrait coordinates (D, V_rel).

        Returns:
            Tuple of numpy arrays: (distances, closing_velocities)
        """
        return np.array(self.distances), np.array(self.closing_velocities)

    def get_state_vector(self, index: int) -> np.ndarray:
        """
        Returns the state vector at a specific time index.

        Args:
            index: Frame index

        Returns:
            numpy array: [x1, y1, vx1, vy1, x2, y2, vx2, vy2]
        """
        p1 = self.player1_data[index]
        p2 = self.player2_data[index]

        return np.array([
            p1['position_x'], p1['position_y'],
            p1['velocity_x'], p1['velocity_y'],
            p2['position_x'], p2['position_y'],
            p2['velocity_x'], p2['velocity_y']
        ])

    def compute_trajectory_statistics(self) -> Dict[str, float]:
        """
        Computes statistical measures of the trajectory on the manifold.

        Returns:
            Dictionary containing mean, std, min, max for distances and velocities
        """
        distances = np.array(self.distances)
        velocities = np.array(self.closing_velocities)

        return {
            'mean_distance': np.mean(distances),
            'std_distance': np.std(distances),
            'min_distance': np.min(distances),
            'max_distance': np.max(distances),
            'mean_velocity': np.mean(velocities),
            'std_velocity': np.std(velocities),
            'min_velocity': np.min(velocities),
            'max_velocity': np.max(velocities)
        }

    def compute_acceleration(self) -> np.ndarray:
        """
        Computes the acceleration by taking the derivative of closing velocity.

        Returns:
            numpy array: Acceleration values
        """
        velocities = np.array(self.closing_velocities)
        # Use finite differences to compute acceleration
        acceleration = np.gradient(velocities)
        return acceleration

    def compute_jerk(self) -> np.ndarray:
        """
        Computes the jerk (derivative of acceleration).

        As mentioned in Section 2.1, these higher-order derivatives are necessary
        for identifying "invisible forces" acting on the player-character particle.

        Returns:
            numpy array: Jerk values
        """
        acceleration = self.compute_acceleration()
        jerk = np.gradient(acceleration)
        return jerk

    def extract_oscillation_frequency(self) -> float:
        """
        Estimates the dominant oscillation frequency in the distance signal.

        This can indicate dash-dancing frequency or other periodic behaviors.

        Returns:
            float: Dominant frequency in Hz (assuming 59.94 fps)
        """
        distances = np.array(self.distances)
        # Remove mean
        distances_centered = distances - np.mean(distances)

        # Compute FFT
        fft = np.fft.fft(distances_centered)
        freqs = np.fft.fftfreq(len(distances), d=1.0/59.94)

        # Find dominant frequency (ignore DC component)
        positive_freqs = freqs[1:len(freqs)//2]
        positive_fft = np.abs(fft[1:len(fft)//2])

        if len(positive_fft) > 0:
            dominant_idx = np.argmax(positive_fft)
            return positive_freqs[dominant_idx]
        return 0.0


def compute_correlation_dimension(distances: np.ndarray,
                                  r_min: float = 1.0,
                                  r_max: float = 100.0,
                                  n_points: int = 20) -> float:
    """
    Computes the correlation dimension D_2 of the distance time series.

    As described in Section 13.2, this quantifies the fractal complexity
    of player movement. Low values (~1) indicate rigid, repetitive patterns.
    High values (>2) indicate complex, unpredictable mix-ups.

    Args:
        distances: Array of distance measurements
        r_min: Minimum radius for correlation sum
        r_max: Maximum radius for correlation sum
        n_points: Number of points to sample

    Returns:
        float: Correlation dimension estimate
    """
    n = len(distances)
    radii = np.logspace(np.log10(r_min), np.log10(r_max), n_points)
    correlations = []

    for r in radii:
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(distances[i] - distances[j]) < r:
                    count += 1
        correlation = 2 * count / (n * (n - 1))
        correlations.append(correlation + 1e-10)  # Avoid log(0)

    # Fit log(C) vs log(r) to get slope (correlation dimension)
    log_r = np.log(radii)
    log_c = np.log(correlations)

    # Linear regression on the linear portion
    coeffs = np.polyfit(log_r, log_c, 1)
    return coeffs[0]
