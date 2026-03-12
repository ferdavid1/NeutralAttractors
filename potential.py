"""
Langevin Spacing Potential Analysis Module

This module implements the attractor dynamics and Langevin spacing potential
framework described in Section 10 of "Dynamical System Modeling of Super Smash Bros. Melee".

Reference: Section 10 - Attractor Dynamics and Langevin Spacing Potentials
"""

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from typing import Tuple, Optional


class LangevinPotential:
    """
    Analyzes spacing dynamics using the Langevin equation framework.

    The Langevin equation models player movement as:
    dD_t = -∇U(D_t)dt + σdW_t

    where U(D) is the potential well and σ is the diffusion coefficient.
    """

    def __init__(self, distances: np.ndarray):
        """
        Initialize the Langevin potential analyzer.

        Args:
            distances: Array of neutral spacing distances D(t)
        """
        self.distances = distances
        self.potential = None
        self.distance_bins = None
        self.pdf = None
        self.diffusion_coefficient = None

    def compute_potential_well(self, n_bins: int = 50,
                               distance_range: Optional[Tuple[float, float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstructs the potential well U(D) from the empirical probability density.

        Using the Boltzmann distribution from statistical mechanics:
        U(D) = -ln(ρ(D))

        where ρ(D) is the probability density function of observed distances.

        Args:
            n_bins: Number of bins for histogram
            distance_range: Optional (min, max) range for binning

        Returns:
            Tuple of (distance_bins, potential_values)
        """
        if distance_range is None:
            distance_range = (np.min(self.distances), np.max(self.distances))

        # Compute probability density function
        counts, bin_edges = np.histogram(self.distances, bins=n_bins,
                                        range=distance_range, density=True)

        # Get bin centers
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        pdf = counts + epsilon

        # Compute potential: U(D) = -ln(ρ(D))
        potential = -np.log(pdf)

        # Normalize so minimum is at zero
        potential = potential - np.min(potential)

        self.distance_bins = bin_centers
        self.pdf = pdf - epsilon  # Remove epsilon for pdf
        self.potential = potential

        return bin_centers, potential

    def find_equilibrium_distance(self) -> float:
        """
        Finds the optimal equilibrium distance D_opt where potential is minimized.

        Returns:
            float: Equilibrium distance
        """
        if self.potential is None:
            self.compute_potential_well()

        min_idx = np.argmin(self.potential)
        return self.distance_bins[min_idx]

    def compute_diffusion_coefficient(self) -> float:
        """
        Computes the diffusion coefficient σ representing movement volatility.

        The diffusion coefficient quantifies the "twitchiness" or kinetic energy
        of micro-adjustments in the neutral game.

        Returns:
            float: Diffusion coefficient estimate
        """
        # Estimate from variance of distance changes
        distance_changes = np.diff(self.distances)
        variance = np.var(distance_changes)

        # σ² ≈ variance / Δt
        # Assuming Δt = 1 frame
        self.diffusion_coefficient = np.sqrt(variance)

        return self.diffusion_coefficient

    def classify_spacing_style(self) -> str:
        """
        Classifies the spacing style based on potential well characteristics.

        Deep, narrow minima → Defensive, precise playstyle
        Broad, shallow wells → Aggressive, high-variance playstyle

        Returns:
            str: Classification of spacing style
        """
        if self.potential is None:
            self.compute_potential_well()

        # Compute well depth
        well_depth = np.max(self.potential) - np.min(self.potential)

        # Compute well width (FWHM - Full Width at Half Maximum)
        half_max = np.min(self.potential) + well_depth / 2
        above_half = self.potential < half_max
        well_width = np.sum(above_half) * (self.distance_bins[1] - self.distance_bins[0])

        # Classify based on depth and width
        if well_depth > 2.0 and well_width < 30:
            return "Defensive-Precise: Deep, narrow potential well"
        elif well_depth < 1.0 and well_width > 50:
            return "Aggressive-Volatile: Shallow, broad potential well"
        elif well_depth > 1.5:
            return "Defensive-Stable: Deep potential well"
        elif well_width > 40:
            return "Aggressive-Mobile: Broad potential well"
        else:
            return "Balanced: Moderate potential well characteristics"

    def detect_multimodal_basins(self, prominence: float = 0.5) -> list:
        """
        Detects multiple basins in the potential landscape.

        As described in Section 13.1, elite players exhibit multi-modal potentials:
        1. Defensive Basin - far from opponent's threat bubble
        2. Offensive Basin - on the edge of opponent's hurtbox range

        Args:
            prominence: Minimum prominence for peak detection

        Returns:
            list: Indices of local minima (basins)
        """
        if self.potential is None:
            self.compute_potential_well()

        from scipy.signal import find_peaks

        # Find local minima (invert for peak finding)
        inverted_potential = -self.potential
        peaks, properties = find_peaks(inverted_potential, prominence=prominence)

        basins = []
        for peak_idx in peaks:
            basins.append({
                'distance': self.distance_bins[peak_idx],
                'depth': -inverted_potential[peak_idx],
                'index': peak_idx
            })

        return basins

    def fit_harmonic_potential(self) -> Tuple[float, float]:
        """
        Fits a harmonic oscillator potential U(D) = k/2 * (D - D_0)² near equilibrium.

        Args:
            None

        Returns:
            Tuple of (spring_constant k, equilibrium_distance D_0)
        """
        if self.potential is None:
            self.compute_potential_well()

        # Find equilibrium
        min_idx = np.argmin(self.potential)
        D_0 = self.distance_bins[min_idx]

        # Fit parabola near minimum (within 20% of range)
        distance_range = np.max(self.distance_bins) - np.min(self.distance_bins)
        fit_range = 0.2 * distance_range

        mask = np.abs(self.distance_bins - D_0) < fit_range
        D_fit = self.distance_bins[mask]
        U_fit = self.potential[mask]

        # Fit U = k/2 * (D - D_0)² + U_0
        def harmonic(D, k, U_0):
            return k / 2 * (D - D_0)**2 + U_0

        try:
            params, _ = curve_fit(harmonic, D_fit, U_fit, p0=[1.0, 0.0])
            k, U_0 = params
            return k, D_0
        except:
            return 0.0, D_0

    def estimate_restoring_force(self, distance: float) -> float:
        """
        Estimates the restoring force F = -∇U(D) at a given distance.

        Args:
            distance: Distance value

        Returns:
            float: Estimated restoring force
        """
        if self.potential is None:
            self.compute_potential_well()

        # Find nearest bin
        idx = np.argmin(np.abs(self.distance_bins - distance))

        # Compute gradient using finite differences
        if idx > 0 and idx < len(self.potential) - 1:
            dU = (self.potential[idx + 1] - self.potential[idx - 1])
            dD = (self.distance_bins[idx + 1] - self.distance_bins[idx - 1])
            force = -dU / dD
        else:
            force = 0.0

        return force


def simulate_langevin_dynamics(U_func, D_0: float, sigma: float,
                               n_steps: int = 1000, dt: float = 1.0) -> np.ndarray:
    """
    Simulates the Langevin equation: dD = -∇U(D)dt + σdW

    Args:
        U_func: Function that computes potential U(D)
        D_0: Initial distance
        sigma: Diffusion coefficient
        n_steps: Number of simulation steps
        dt: Time step size

    Returns:
        numpy array: Simulated distance trajectory
    """
    D = np.zeros(n_steps)
    D[0] = D_0

    for i in range(1, n_steps):
        # Compute force F = -dU/dD numerically
        epsilon = 0.1
        dU_dD = (U_func(D[i-1] + epsilon) - U_func(D[i-1] - epsilon)) / (2 * epsilon)

        # Langevin equation: dD = -dU/dD * dt + σ * dW
        dW = np.random.normal(0, np.sqrt(dt))
        D[i] = D[i-1] - dU_dD * dt + sigma * dW

        # Enforce boundary conditions (non-negative distance)
        D[i] = max(D[i], 0.0)

    return D
