"""
NeutralAttractors: Dynamical System Analysis for Super Smash Bros. Melee

A comprehensive framework for analyzing competitive SSBM gameplay through
the lens of chaos theory, dynamical systems, and stochastic analysis.

Based on the research paper:
"Dynamical System Modeling of Super Smash Bros. Melee: Attractor Manifolds,
Biomechanical Telemetry, and Stochastic Analysis"
"""

__version__ = "1.0.0"
__author__ = "NeutralAttractors Research Team"

from .telemetry import (
    extract_neutral_distances,
    extract_full_telemetry,
    calculate_euclidean_distance,
    calculate_relative_velocity,
    is_neutral,
    NEUTRAL_STATES
)

from .manifold import (
    RelativeManifold,
    compute_correlation_dimension
)

from .potential import (
    LangevinPotential,
    simulate_langevin_dynamics
)

from .lyapunov import (
    LyapunovAnalyzer,
    compute_trajectory_divergence,
    estimate_predictability_horizon,
    compute_entropy_rate
)

from .visualization import (
    plot_phase_portrait,
    plot_potential_well,
    plot_distance_timeseries,
    plot_multimodal_basins,
    plot_lyapunov_spectrum,
    plot_analysis_dashboard
)

__all__ = [
    # Telemetry
    'extract_neutral_distances',
    'extract_full_telemetry',
    'calculate_euclidean_distance',
    'calculate_relative_velocity',
    'is_neutral',
    'NEUTRAL_STATES',
    # Manifold
    'RelativeManifold',
    'compute_correlation_dimension',
    # Potential
    'LangevinPotential',
    'simulate_langevin_dynamics',
    # Lyapunov
    'LyapunovAnalyzer',
    'compute_trajectory_divergence',
    'estimate_predictability_horizon',
    'compute_entropy_rate',
    # Visualization
    'plot_phase_portrait',
    'plot_potential_well',
    'plot_distance_timeseries',
    'plot_multimodal_basins',
    'plot_lyapunov_spectrum',
    'plot_analysis_dashboard',
]
