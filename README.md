# NeutralAttractors

**Dynamical System Analysis for Super Smash Bros. Melee**

A comprehensive framework for analyzing competitive SSBM gameplay through the lens of chaos theory, dynamical systems, and stochastic analysis. This implementation brings rigorous mathematical modeling to the analysis of the neutral game, treating player interactions as a continuous physical system rather than discrete state transitions.

## Overview

Traditional fighting game analysis relies on discrete computational models, viewing interactions through game theory or Markovian state transitions. However, Super Smash Bros. Melee's physics-heavy engine, sub-frame collision detection, and continuous analog control mechanisms demand a fundamentally different approach.

This project implements the theoretical framework described in *"Dynamical System Modeling of Super Smash Bros. Melee: Attractor Manifolds, Biomechanical Telemetry, and Stochastic Analysis"*, which models the neutral game as:

- **Strange Attractors**: Optimal spacing relationships maintained through continuous kinetic input
- **Stochastic Differential Equations**: The Langevin equation models spacing as a potential well with noise
- **Lyapunov Exponents**: Quantifies the chaotic nature of neutral vs. deterministic punish states
- **Bifurcation Analysis**: Identifies transitions from neutral to advantage states

## Key Features

### 1. Telemetry Extraction (`telemetry.py`)
- Parses `.slp` replay files using `py-slippi`
- Extracts Root Bone coordinates, velocities, and action states
- Filters for neutral game frames (Action State IDs 0-21, 24-33)
- Computes Euclidean distances and relative closing velocities

### 2. Relative Manifold Projection (`manifold.py`)
- Projects 8D state space to relative manifold **M**
- Primary state variable: distance **D(t)** between Root Bones
- Secondary variable: closing velocity **V_rel(t)**
- Computes acceleration, jerk, and correlation dimension **D_2**

### 3. Langevin Potential Analysis (`potential.py`)
- Reconstructs potential well **U(D)** from empirical probability density
- Uses Boltzmann distribution: **U(D) = -ln(ρ(D))**
- Identifies equilibrium distance **D_opt**
- Computes diffusion coefficient **σ** (movement volatility)
- Detects multi-modal basins (defensive vs. offensive spacing)

### 4. Lyapunov Exponent Calculation (`lyapunov.py`)
- Computes maximum Lyapunov exponent **λ**
- **λ > 0**: Bounded chaos (neutral game)
- **λ ≤ 0**: Deterministic (punish state)
- Detects topological bifurcations
- Estimates predictability horizon

### 5. Visualization Tools (`visualization.py`)
- Phase portraits **(D, V_rel)**
- Potential well plots **U(D)**
- Distance time series with bifurcation markers
- Multi-modal basin visualization
- Comprehensive analysis dashboards

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/NeutralAttractors.git
cd NeutralAttractors

# Install dependencies
pip install -r requirements.txt
```

### Requirements
- Python 3.7+
- `py-slippi >= 1.5.1`
- `numpy >= 1.21.0`
- `scipy >= 1.7.0`
- `matplotlib >= 3.4.0`
- `pandas >= 1.3.0`

## Usage

### Basic Analysis

```python
from telemetry import extract_neutral_distances, extract_full_telemetry
from manifold import RelativeManifold
from potential import LangevinPotential
from lyapunov import LyapunovAnalyzer

# Extract telemetry
distances = extract_neutral_distances("./replays")
p1_data, p2_data = extract_full_telemetry("./replays")

# Project to manifold
manifold = RelativeManifold(p1_data, p2_data)
distances, velocities = manifold.get_phase_portrait()

# Compute potential well
langevin = LangevinPotential(distances)
bins, potential = langevin.compute_potential_well()
equilibrium = langevin.find_equilibrium_distance()

# Compute Lyapunov exponent
import numpy as np
state_vectors = np.array([manifold.get_state_vector(i)
                         for i in range(len(p1_data))])
lyapunov = LyapunovAnalyzer(state_vectors)
max_lambda = lyapunov.compute_max_lyapunov_exponent()
```

### Command-Line Analysis

```bash
python example_analysis.py ./replays ./results
```

This will:
1. Extract telemetry from all `.slp` files in `./replays`
2. Compute all dynamical system metrics
3. Generate visualizations in `./results`
4. Print comprehensive analysis summary

## Example Output

```
================================================================================
NEUTRAL ATTRACTORS: Dynamical System Analysis of SSBM
================================================================================

[1/6] Extracting telemetry from replay files...
      Extracted 4523 neutral game frames

[2/6] Projecting to relative manifold M...
      Mean distance: 45.32 ± 15.67
      Distance range: [8.42, 98.73]

[3/6] Computing Langevin spacing potential U(D)...
      Equilibrium distance D_opt: 42.18 engine units
      Diffusion coefficient σ: 3.2456
      Spacing style: Defensive-Precise: Deep, narrow potential well
      Detected 2 potential basins:
        Basin 1: D = 28.45 (Offensive)
        Basin 2: D = 52.91 (Defensive)

[4/6] Computing maximum Lyapunov exponent λ...
      Maximum Lyapunov exponent λ: 0.2847
      System state: Bounded Chaos (Neutral Game): λ > 0
      Predictability horizon: 12.4 frames (0.21 seconds)
      Detected 7 bifurcation points

[5/6] Computing correlation dimension D_2...
      Correlation dimension D_2: 2.3451
      Interpretation: Complex, unpredictable mix-ups

[6/6] Generating visualizations...
      ✓ Phase portrait saved
      ✓ Potential well saved
      ✓ Distance time series saved
      ✓ Multi-modal basins plot saved
      ✓ Analysis dashboard saved
```

## Theoretical Background

### The Neutral Game as a Dynamical System

The neutral game is modeled using the **Langevin equation**:

```
dD_t = -∇U(D_t)dt + σdW_t
```

Where:
- **D_t**: Distance between Root Bones
- **U(D)**: Potential well (emergent from threat bubbles and spacing preferences)
- **σ**: Diffusion coefficient (movement volatility)
- **W_t**: Wiener process (Gaussian noise from execution imperfections)

### Lyapunov Exponents and Chaos

The maximum Lyapunov exponent **λ** quantifies sensitivity to initial conditions:

```
λ = lim(t→∞) lim(||δX(0)||→0) (1/t) ln(||δX(t)|| / ||δX(0)||)
```

- **λ > 0**: Exponential divergence → Chaotic neutral game
- **λ ≤ 0**: Convergence → Deterministic punish state

This provides an **objective metric** for "winning neutral"—the moment when λ collapses from positive to non-positive.

### Root Bone Coordinates

The `p.position` coordinates from `py-slippi` represent the **Root Bone** (Bone 0) of the character's skeletal armature, not the visual center or center of mass. This provides the most stable measure of macro-trajectory, unperturbed by animation micro-oscillations.

### Environment Collision Box (ECB)

Stage collision is mediated through the **ECB diamond** (top, bottom, left, right points). The bottom point triggers floor detection and landing mechanics. ECB manipulation enables advanced techniques like:
- **No-Impact Landings (NIL)**
- **Aerial Interrupts**
- **Platform Warping**

## Character Physics Constants

Different characters have vastly different dynamical properties. For example:

| Character | Traction | Interpretation |
|-----------|----------|----------------|
| Luigi | 0.025 | Highly underdamped; wide, flat potential wells |
| Fox/Falco | 0.080 | Overdamped; tight dash-dances, deep wells |
| Peach | 0.100 | Highly overdamped; near-static equilibrium |

## Project Structure

```
NeutralAttractors/
├── __init__.py              # Package initialization
├── telemetry.py             # Telemetry extraction (Section 4.2)
├── manifold.py              # Relative manifold projection (Section 9)
├── potential.py             # Langevin potential analysis (Section 10)
├── lyapunov.py              # Lyapunov exponents (Section 11)
├── visualization.py         # Plotting and visualization
├── example_analysis.py      # Complete analysis workflow
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Citations

If you use this framework in your research, please cite:

```
"Dynamical System Modeling of Super Smash Bros. Melee: Attractor Manifolds,
Biomechanical Telemetry, and Stochastic Analysis" (2026)
```

## Contributing

Contributions are welcome! Areas for expansion:
- Multi-character matchup analysis
- Stage-specific potential wells
- Real-time bifurcation detection
- Machine learning integration for threat bubble prediction

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **py-slippi** library for telemetry extraction
- The competitive Melee community for inspiring rigorous analysis
- Chaos theory and nonlinear dynamics research community
