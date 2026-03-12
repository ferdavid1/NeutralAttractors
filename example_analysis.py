"""
Example Analysis Script

This script demonstrates a complete analysis workflow using the NeutralAttractors
framework to analyze Super Smash Bros. Melee replay files.

Usage:
    python example_analysis.py <replay_directory>
"""

import sys
import os
import numpy as np
from telemetry import extract_neutral_distances, extract_full_telemetry
from manifold import RelativeManifold, compute_correlation_dimension
from potential import LangevinPotential
from lyapunov import LyapunovAnalyzer, estimate_predictability_horizon
from visualization import (plot_phase_portrait, plot_potential_well,
                          plot_distance_timeseries, plot_multimodal_basins,
                          plot_analysis_dashboard)


def analyze_replays(replay_dir: str, output_dir: str = "results"):
    """
    Performs complete dynamical system analysis on a directory of replay files.

    Args:
        replay_dir: Path to directory containing .slp files
        output_dir: Directory to save results and visualizations
    """
    print("=" * 80)
    print("NEUTRAL ATTRACTORS: Dynamical System Analysis of SSBM")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract telemetry
    print("[1/6] Extracting telemetry from replay files...")
    neutral_distances = extract_neutral_distances(replay_dir)
    player1_data, player2_data = extract_full_telemetry(replay_dir)

    if len(neutral_distances) == 0:
        print("ERROR: No neutral game frames found in replay files.")
        return

    print(f"      Extracted {len(neutral_distances)} neutral game frames")
    print()

    # Step 2: Project to relative manifold
    print("[2/6] Projecting to relative manifold M...")
    manifold = RelativeManifold(player1_data, player2_data)
    distances, velocities = manifold.get_phase_portrait()

    stats = manifold.compute_trajectory_statistics()
    print(f"      Mean distance: {stats['mean_distance']:.2f} ± {stats['std_distance']:.2f}")
    print(f"      Distance range: [{stats['min_distance']:.2f}, {stats['max_distance']:.2f}]")
    print(f"      Mean velocity: {stats['mean_velocity']:.2f} ± {stats['std_velocity']:.2f}")
    print()

    # Step 3: Compute Langevin potential
    print("[3/6] Computing Langevin spacing potential U(D)...")
    langevin = LangevinPotential(distances)
    distance_bins, potential = langevin.compute_potential_well(n_bins=50)
    equilibrium = langevin.find_equilibrium_distance()
    diffusion = langevin.compute_diffusion_coefficient()
    spacing_style = langevin.classify_spacing_style()

    print(f"      Equilibrium distance D_opt: {equilibrium:.2f} engine units")
    print(f"      Diffusion coefficient σ: {diffusion:.4f}")
    print(f"      Spacing style: {spacing_style}")

    # Detect multi-modal basins
    basins = langevin.detect_multimodal_basins(prominence=0.5)
    if len(basins) > 1:
        print(f"      Detected {len(basins)} potential basins:")
        for i, basin in enumerate(basins):
            print(f"        Basin {i+1}: D = {basin['distance']:.2f}")
    print()

    # Step 4: Compute Lyapunov exponents
    print("[4/6] Computing maximum Lyapunov exponent λ...")
    state_vectors = np.array([manifold.get_state_vector(i)
                             for i in range(len(player1_data))])
    lyapunov_analyzer = LyapunovAnalyzer(state_vectors)
    max_lambda = lyapunov_analyzer.compute_max_lyapunov_exponent()
    system_state = lyapunov_analyzer.classify_system_state()

    print(f"      Maximum Lyapunov exponent λ: {max_lambda:.4f}")
    print(f"      System state: {system_state}")

    if max_lambda > 0:
        horizon = estimate_predictability_horizon(max_lambda)
        print(f"      Predictability horizon: {horizon:.1f} frames ({horizon/59.94:.2f} seconds)")

    # Detect bifurcations
    bifurcations = lyapunov_analyzer.detect_bifurcation_points(window_size=60)
    if bifurcations:
        print(f"      Detected {len(bifurcations)} bifurcation points")
    print()

    # Step 5: Compute fractal dimension
    print("[5/6] Computing correlation dimension D_2...")
    correlation_dim = compute_correlation_dimension(distances)
    print(f"      Correlation dimension D_2: {correlation_dim:.4f}")

    if correlation_dim < 1.5:
        print(f"      Interpretation: Rigid, repetitive movement patterns")
    elif correlation_dim > 2.0:
        print(f"      Interpretation: Complex, unpredictable mix-ups")
    else:
        print(f"      Interpretation: Moderate complexity movement")
    print()

    # Step 6: Generate visualizations
    print("[6/6] Generating visualizations...")

    # Phase portrait
    plot_phase_portrait(distances, velocities,
                       save_path=os.path.join(output_dir, "phase_portrait.png"))
    print("      ✓ Phase portrait saved")

    # Potential well
    plot_potential_well(distance_bins, potential, equilibrium,
                       save_path=os.path.join(output_dir, "potential_well.png"))
    print("      ✓ Potential well saved")

    # Distance time series
    plot_distance_timeseries(distances, bifurcation_points=bifurcations,
                            save_path=os.path.join(output_dir, "distance_timeseries.png"))
    print("      ✓ Distance time series saved")

    # Multi-modal basins (if detected)
    if len(basins) > 1:
        plot_multimodal_basins(distance_bins, potential, basins,
                              save_path=os.path.join(output_dir, "multimodal_basins.png"))
        print("      ✓ Multi-modal basins plot saved")

    # Comprehensive dashboard
    plot_analysis_dashboard(distances, velocities, distance_bins, potential,
                           save_path=os.path.join(output_dir, "analysis_dashboard.png"))
    print("      ✓ Analysis dashboard saved")
    print()

    # Summary report
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total neutral frames analyzed: {len(distances)}")
    print(f"Duration: {len(distances)/59.94:.2f} seconds")
    print()
    print("SPACING DYNAMICS:")
    print(f"  • Equilibrium distance: {equilibrium:.2f} engine units")
    print(f"  • Movement volatility (σ): {diffusion:.4f}")
    print(f"  • Style classification: {spacing_style}")
    print()
    print("CHAOS THEORY METRICS:")
    print(f"  • Max Lyapunov exponent (λ): {max_lambda:.4f}")
    print(f"  • System classification: {system_state}")
    print(f"  • Correlation dimension (D_2): {correlation_dim:.4f}")
    print()
    print(f"Results saved to: {output_dir}/")
    print("=" * 80)


def main():
    """Main entry point for the example analysis script."""
    if len(sys.argv) < 2:
        print("Usage: python example_analysis.py <replay_directory> [output_directory]")
        print()
        print("Example:")
        print("  python example_analysis.py ./replays ./results")
        sys.exit(1)

    replay_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results"

    if not os.path.exists(replay_dir):
        print(f"ERROR: Replay directory '{replay_dir}' does not exist.")
        sys.exit(1)

    # Check if directory contains .slp files
    slp_files = [f for f in os.listdir(replay_dir) if f.endswith('.slp')]
    if not slp_files:
        print(f"ERROR: No .slp files found in '{replay_dir}'")
        sys.exit(1)

    print(f"Found {len(slp_files)} replay file(s)")
    print()

    try:
        analyze_replays(replay_dir, output_dir)
    except Exception as e:
        print(f"ERROR: Analysis failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
