"""
Lyapunov Exponent Calculation Module

This module implements the bifurcation analysis and Lyapunov exponent calculation
described in Section 11 of "Dynamical System Modeling of Super Smash Bros. Melee".

Reference: Section 11 - Bifurcations and Lyapunov Exponents
"""

import numpy as np
from typing import Tuple, List


class LyapunovAnalyzer:
    """
    Computes maximum Lyapunov exponents to distinguish between chaotic neutral
    game (λ > 0) and deterministic punish state (λ ≤ 0).
    """

    def __init__(self, state_vectors: np.ndarray):
        """
        Initialize the Lyapunov analyzer.

        Args:
            state_vectors: Array of state vectors [x1, y1, vx1, vy1, x2, y2, vx2, vy2]
                          with shape (n_frames, 8)
        """
        self.state_vectors = state_vectors
        self.max_lyapunov = None

    def compute_max_lyapunov_exponent(self, embedding_dim: int = 3,
                                     tau: int = 1,
                                     min_separation: float = 1e-5,
                                     max_separation: float = 10.0,
                                     max_samples: int = 1000) -> float:
        """
        Computes the maximum Lyapunov exponent λ using the average divergence method.

        For an infinitesimally small perturbation δX, the maximum Lyapunov
        exponent is defined as:
        λ = lim(t→∞) lim(||δX(0)||→0) (1/t) ln(||δX(t)|| / ||δX(0)||)

        Positive λ > 0: Bounded chaos (neutral game)
        λ ≤ 0: Deterministic or stable (punish state)

        Args:
            embedding_dim: Embedding dimension for phase space reconstruction
            tau: Time delay for embedding
            min_separation: Minimum initial separation
            max_separation: Maximum initial separation
            max_samples: Maximum number of sample points (for performance)

        Returns:
            float: Maximum Lyapunov exponent
        """
        from tqdm import tqdm

        # Use distance-based approach on the relative manifold
        distances = self._compute_distances()

        n = len(distances)
        if n < 100:
            return 0.0

        # Subsample for performance - use every Nth frame
        if n > max_samples:
            step = n // max_samples
            sample_indices = list(range(0, n - 50, step))
        else:
            sample_indices = list(range(n - 50))

        # Compute divergence rates
        divergence_rates = []

        for i in tqdm(sample_indices, desc="Computing Lyapunov", unit="samples", leave=False):
            # Find nearby trajectories (limited search)
            for j in range(i + 10, min(i + 50, n - 50), 5):  # Skip every 5 frames
                initial_sep = abs(distances[i] - distances[j])

                if min_separation < initial_sep < max_separation:
                    # Track divergence over time (limited horizon)
                    max_time = min(20, n - max(i, j))  # Reduced from 50 to 20

                    for t in range(1, max_time, 2):  # Skip every other frame
                        separation_t = abs(distances[i + t] - distances[j + t])

                        if separation_t > min_separation:
                            # Compute local divergence rate
                            divergence = np.log(separation_t / initial_sep) / t
                            divergence_rates.append(divergence)
                            break

        if len(divergence_rates) > 0:
            self.max_lyapunov = np.mean(divergence_rates)
        else:
            self.max_lyapunov = 0.0

        return self.max_lyapunov

    def _compute_distances(self) -> np.ndarray:
        """
        Computes Euclidean distances from state vectors.

        Returns:
            numpy array: Distance values D(t)
        """
        n_frames = self.state_vectors.shape[0]
        distances = np.zeros(n_frames)

        for i in range(n_frames):
            x1, y1 = self.state_vectors[i, 0], self.state_vectors[i, 1]
            x2, y2 = self.state_vectors[i, 4], self.state_vectors[i, 5]
            distances[i] = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

        return distances

    def detect_bifurcation_points(self, window_size: int = 60,
                                  threshold: float = 0.5) -> List[int]:
        """
        Detects bifurcation points where the system transitions from chaotic
        neutral (λ > 0) to deterministic punish (λ ≤ 0).

        Args:
            window_size: Size of sliding window for local λ estimation
            threshold: Threshold for detecting significant λ change

        Returns:
            List of frame indices where bifurcations occur
        """
        distances = self._compute_distances()
        n = len(distances)

        bifurcation_points = []
        local_lyapunovs = []

        for i in range(0, n - window_size, window_size // 2):
            window = distances[i:i + window_size]
            local_lambda = self._estimate_local_lyapunov(window)
            local_lyapunovs.append((i + window_size // 2, local_lambda))

        # Detect transitions from positive to non-positive
        for i in range(1, len(local_lyapunovs)):
            prev_frame, prev_lambda = local_lyapunovs[i - 1]
            curr_frame, curr_lambda = local_lyapunovs[i]

            # Bifurcation: transition from chaos to determinism
            if prev_lambda > threshold and curr_lambda <= threshold:
                bifurcation_points.append(curr_frame)

        return bifurcation_points

    def _estimate_local_lyapunov(self, distances: np.ndarray) -> float:
        """
        Estimates local Lyapunov exponent for a window of distances.

        Args:
            distances: Window of distance values

        Returns:
            float: Local Lyapunov estimate
        """
        n = len(distances)
        if n < 10:
            return 0.0

        divergences = []

        for i in range(n - 5):
            for j in range(i + 1, min(i + 5, n - 3)):
                initial_sep = abs(distances[i] - distances[j])

                if initial_sep > 1e-5:
                    for t in range(1, min(3, n - max(i, j))):
                        sep_t = abs(distances[i + t] - distances[j + t])

                        if sep_t > 1e-5:
                            divergences.append(np.log(sep_t / initial_sep) / t)
                            break

        if len(divergences) > 0:
            return np.mean(divergences)
        return 0.0

    def classify_system_state(self) -> str:
        """
        Classifies the current system state based on maximum Lyapunov exponent.

        Returns:
            str: Classification of system state
        """
        if self.max_lyapunov is None:
            self.compute_max_lyapunov_exponent()

        if self.max_lyapunov > 0.5:
            return "Bounded Chaos (Neutral Game): λ > 0.5"
        elif self.max_lyapunov > 0:
            return "Weakly Chaotic (Transitional): 0 < λ < 0.5"
        elif self.max_lyapunov < 0:
            return "Deterministic (Punish State): λ < 0"
        else:
            return "Neutral Stability: λ ≈ 0"


def compute_trajectory_divergence(traj1: np.ndarray, traj2: np.ndarray) -> np.ndarray:
    """
    Computes the divergence between two nearby trajectories over time.

    Args:
        traj1: First trajectory (n_frames, n_dims)
        traj2: Second trajectory (n_frames, n_dims)

    Returns:
        numpy array: Divergence at each time step
    """
    divergence = np.linalg.norm(traj1 - traj2, axis=1)
    return divergence


def estimate_predictability_horizon(lyapunov_exponent: float,
                                   initial_uncertainty: float = 0.1,
                                   final_uncertainty: float = 10.0) -> float:
    """
    Estimates the predictability horizon based on Lyapunov exponent.

    The predictability horizon is the time until uncertainty grows from
    initial_uncertainty to final_uncertainty.

    Args:
        lyapunov_exponent: Maximum Lyapunov exponent λ
        initial_uncertainty: Initial state uncertainty
        final_uncertainty: Final uncertainty threshold

    Returns:
        float: Predictability horizon in frames
    """
    if lyapunov_exponent <= 0:
        return float('inf')  # Deterministic system

    # ||δX(t)|| ≈ ||δX(0)|| * e^(λt)
    # Solve for t when ||δX(t)|| = final_uncertainty
    horizon = np.log(final_uncertainty / initial_uncertainty) / lyapunov_exponent

    return horizon


def compute_entropy_rate(distances: np.ndarray, n_bins: int = 20) -> float:
    """
    Computes the Kolmogorov-Sinai entropy rate of the distance time series.

    For chaotic systems, the KS entropy is related to the sum of positive
    Lyapunov exponents.

    Args:
        distances: Array of distance values
        n_bins: Number of bins for discretization

    Returns:
        float: Entropy rate estimate
    """
    # Discretize distances
    bins = np.linspace(np.min(distances), np.max(distances), n_bins)
    digitized = np.digitize(distances, bins)

    # Compute transition probabilities
    n = len(digitized)
    transition_counts = np.zeros((n_bins, n_bins))

    for i in range(n - 1):
        current_bin = min(digitized[i], n_bins - 1)
        next_bin = min(digitized[i + 1], n_bins - 1)
        transition_counts[current_bin, next_bin] += 1

    # Normalize to get probabilities
    transition_probs = transition_counts / (np.sum(transition_counts, axis=1, keepdims=True) + 1e-10)

    # Compute entropy rate: H = -Σ p(i,j) log p(i,j)
    entropy = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if transition_probs[i, j] > 0:
                entropy -= transition_probs[i, j] * np.log(transition_probs[i, j])

    return entropy
