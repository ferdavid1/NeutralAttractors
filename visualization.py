"""
Visualization Module

This module provides visualization tools for the dynamical system analysis
of Super Smash Bros. Melee neutral game interactions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional, Tuple


def plot_phase_portrait(distances: np.ndarray,
                       velocities: np.ndarray,
                       title: str = "Phase Portrait (D, V_rel)",
                       save_path: Optional[str] = None) -> Figure:
    """
    Plots the phase portrait of the relative manifold (D, V_rel).

    Args:
        distances: Array of distance values D(t)
        velocities: Array of closing velocities V_rel(t)
        title: Plot title
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot trajectory
    ax.plot(distances, velocities, 'b-', alpha=0.5, linewidth=0.5)
    ax.scatter(distances[::10], velocities[::10], c=range(0, len(distances), 10),
              cmap='viridis', s=10, alpha=0.6)

    ax.set_xlabel('Distance D (engine units)', fontsize=12)
    ax.set_ylabel('Relative Closing Velocity V_rel (units/frame)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.3, label='V_rel = 0')

    cbar = plt.colorbar(ax.collections[0], ax=ax, label='Frame Index')

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_potential_well(distance_bins: np.ndarray,
                       potential: np.ndarray,
                       equilibrium_distance: Optional[float] = None,
                       title: str = "Spacing Potential Well U(D)",
                       save_path: Optional[str] = None) -> Figure:
    """
    Plots the reconstructed potential well U(D).

    Args:
        distance_bins: Array of distance bin centers
        potential: Array of potential values
        equilibrium_distance: Optional equilibrium distance to mark
        title: Plot title
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(distance_bins, potential, 'b-', linewidth=2)
    ax.fill_between(distance_bins, potential, alpha=0.3)

    if equilibrium_distance is not None:
        ax.axvline(x=equilibrium_distance, color='r', linestyle='--',
                  linewidth=2, label=f'Equilibrium: D = {equilibrium_distance:.2f}')
        ax.legend()

    ax.set_xlabel('Distance D (engine units)', fontsize=12)
    ax.set_ylabel('Potential U(D)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_distance_timeseries(distances: np.ndarray,
                            timestamps: Optional[np.ndarray] = None,
                            bifurcation_points: Optional[list] = None,
                            title: str = "Neutral Game Distance D(t)",
                            save_path: Optional[str] = None) -> Figure:
    """
    Plots the distance time series with optional bifurcation markers.

    Args:
        distances: Array of distance values
        timestamps: Optional frame timestamps
        bifurcation_points: Optional list of bifurcation frame indices
        title: Plot title
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    if timestamps is None:
        timestamps = np.arange(len(distances))

    ax.plot(timestamps, distances, 'b-', linewidth=1, alpha=0.7)

    if bifurcation_points:
        for bf in bifurcation_points:
            ax.axvline(x=bf, color='r', linestyle='--', alpha=0.5, linewidth=2)
        ax.axvline(x=bifurcation_points[0], color='r', linestyle='--',
                  alpha=0.5, linewidth=2, label='Bifurcation Points')
        ax.legend()

    ax.set_xlabel('Frame', fontsize=12)
    ax.set_ylabel('Distance D (engine units)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_multimodal_basins(distance_bins: np.ndarray,
                          potential: np.ndarray,
                          basins: list,
                          title: str = "Multi-Modal Potential Landscape",
                          save_path: Optional[str] = None) -> Figure:
    """
    Plots the potential well with multiple basins highlighted.

    Args:
        distance_bins: Array of distance bin centers
        potential: Array of potential values
        basins: List of basin dictionaries from detect_multimodal_basins
        title: Plot title
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(distance_bins, potential, 'b-', linewidth=2, label='U(D)')
    ax.fill_between(distance_bins, potential, alpha=0.2)

    colors = ['red', 'green', 'orange', 'purple']
    labels = ['Defensive Basin', 'Offensive Basin', 'Basin 3', 'Basin 4']

    for i, basin in enumerate(basins):
        color = colors[i % len(colors)]
        label = labels[i % len(labels)]
        ax.axvline(x=basin['distance'], color=color, linestyle='--',
                  linewidth=2, label=f"{label}: D={basin['distance']:.1f}")

    ax.set_xlabel('Distance D (engine units)', fontsize=12)
    ax.set_ylabel('Potential U(D)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_lyapunov_spectrum(distances: np.ndarray,
                          window_size: int = 60,
                          title: str = "Local Lyapunov Exponent Spectrum",
                          save_path: Optional[str] = None) -> Figure:
    """
    Plots the local Lyapunov exponent over time to visualize chaos transitions.

    Args:
        distances: Array of distance values
        window_size: Window size for local λ estimation
        title: Plot title
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    from lyapunov import LyapunovAnalyzer

    # Create dummy state vectors (simplified)
    n = len(distances)
    state_vectors = np.zeros((n, 8))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Plot distance
    ax1.plot(distances, 'b-', linewidth=1, alpha=0.7)
    ax1.set_ylabel('Distance D (engine units)', fontsize=12)
    ax1.set_title('Distance Time Series', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Compute local Lyapunov exponents
    local_lambdas = []
    frame_centers = []

    for i in range(0, n - window_size, window_size // 4):
        window = distances[i:i + window_size]
        # Simplified local estimation
        if len(window) > 10:
            variance = np.var(np.diff(window))
            local_lambda = np.log(variance + 1e-10)
            local_lambdas.append(local_lambda)
            frame_centers.append(i + window_size // 2)

    # Plot local Lyapunov
    ax2.plot(frame_centers, local_lambdas, 'r-', linewidth=2, label='Local λ')
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='λ = 0')
    ax2.fill_between(frame_centers, local_lambdas, 0, where=np.array(local_lambdas) > 0,
                     alpha=0.3, color='red', label='Chaotic (λ > 0)')
    ax2.fill_between(frame_centers, local_lambdas, 0, where=np.array(local_lambdas) <= 0,
                     alpha=0.3, color='blue', label='Stable (λ ≤ 0)')

    ax2.set_xlabel('Frame', fontsize=12)
    ax2.set_ylabel('Local Lyapunov Exponent λ', fontsize=12)
    ax2.set_title('Chaos-Order Transitions', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.suptitle(title, fontsize=14, fontweight='bold')

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_analysis_dashboard(distances: np.ndarray,
                           velocities: np.ndarray,
                           distance_bins: np.ndarray,
                           potential: np.ndarray,
                           save_path: Optional[str] = None) -> Figure:
    """
    Creates a comprehensive dashboard with multiple analysis views.

    Args:
        distances: Array of distance values
        velocities: Array of closing velocities
        distance_bins: Array of distance bin centers
        potential: Array of potential values
        save_path: Optional path to save figure

    Returns:
        matplotlib Figure object
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 1. Distance time series
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(distances, 'b-', linewidth=1, alpha=0.7)
    ax1.set_ylabel('Distance D', fontsize=10)
    ax1.set_title('Distance Time Series', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # 2. Phase portrait
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.scatter(distances[::5], velocities[::5], c=range(0, len(distances), 5),
               cmap='viridis', s=5, alpha=0.5)
    ax2.set_xlabel('Distance D', fontsize=10)
    ax2.set_ylabel('Velocity V_rel', fontsize=10)
    ax2.set_title('Phase Portrait', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # 3. Potential well
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(distance_bins, potential, 'b-', linewidth=2)
    ax3.fill_between(distance_bins, potential, alpha=0.3)
    ax3.set_xlabel('Distance D', fontsize=10)
    ax3.set_ylabel('Potential U(D)', fontsize=10)
    ax3.set_title('Spacing Potential Well', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 4. Distance histogram
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.hist(distances, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')
    ax4.set_xlabel('Distance D', fontsize=10)
    ax4.set_ylabel('Probability Density', fontsize=10)
    ax4.set_title('Distance Distribution ρ(D)', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # 5. Velocity histogram
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.hist(velocities, bins=50, density=True, alpha=0.7, color='red', edgecolor='black')
    ax5.set_xlabel('Velocity V_rel', fontsize=10)
    ax5.set_ylabel('Probability Density', fontsize=10)
    ax5.set_title('Velocity Distribution', fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3)

    fig.suptitle('Neutral Game Dynamical System Analysis Dashboard',
                fontsize=14, fontweight='bold')

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig
