ARCHITECTURE.md# Bio-Adaptive QEC Simulation - Architecture

## Project Overview

Bio-Adaptive Quantum Error Correction (BA-QEC) implements an immune-inspired approach to quantum error correction. This document describes the architecture and organization of the codebase.

## Directory Structure

```
bio-adaptive-qec-simulation/
├── src/                          # Core library code
│   ├── __init__.py
│   ├── decoder.py                # BA-QEC decoder implementation
│   ├── matching.py               # MWPM matching wrapper
│   ├── biological_priors.py      # CDR3-inspired weighting strategies
│   ├── noise_models.py           # Hardware noise characterization
│   └── visualization.py          # Common plotting utilities
│
├── simulations/                  # Simulation scripts and benchmarks
│   ├── benchmarks/
│   │   ├── clonal_expansion.py
│   │   └── hamming_distance.py
│   ├── hardware_tests/
│   │   └── realqtest_1121.py
│   └── surface_code/
│
├── notebooks/                    # Jupyter notebooks for analysis
│   ├── 01_real_hardware_execution.ipynb
│   ├── 02_bio_adaptive_decoder_analysis.ipynb
│   ├── 03_cross_domain_isomorphism_analysis.ipynb
│   └── 04_clonal_expansion_dynamics.ipynb
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_decoder.py
│   └── test_matching.py
│
├── data/                         # Data files
│   ├── hardware_data/            # Real quantum hardware results
│   │   ├── FIRST_REAL_BIO_ADAPTIVE_QEC_ON_IBM_TORINO_NOV_21_2025_30K_SHOTS.pkl
│   │   └── IBM_TORINO_NOV21_2025_D3_R50_30K_REAL.pkl
│   └── sample_cdr3.csv          # CDR3 sequence dataset
│
├── results/                      # Generated outputs
│   ├── plots/                    # Output plots and visualizations
│   └── analyses/                 # Analysis results
│
├── docs/                         # Documentation
│   ├── index.md
│   ├── architecture.md           # This file
│   ├── hardware_results.md
│   └── contributing.md
│
├── .github/workflows/            # CI/CD configuration
├── setup.py                      # Package setup
├── pyproject.toml                # Modern Python packaging
├── pytest.ini                    # Test configuration
├── .gitignore                    # Git ignore rules
└── README.md                     # Project overview
```

## Core Modules

### src/decoder.py
The main BA-QEC decoder implementation. Provides the `BAQECDecoder` class that:
- Implements immune-inspired weight modifications
- Integrates with PyMatching for MWPM
- Supports CDR3-length prior weighting

### src/biological_priors.py
Implements biological inspiration functions:
- CDR3 length distribution modeling
- Clonal expansion weight amplification
- Immune memory cached corrections

### src/noise_models.py
Characterizes hardware noise:
- Device-specific error rate estimation
- Asymmetric noise modeling
- Qubit-level noise characterization

### src/visualization.py
Plotting utilities for:
- Threshold plots
- Fidelity maps
- Error rate comparisons

## Simulation Pipeline

1. **Circuit Generation** (Stim)
   - Generate surface code circuits with specified parameters
   - Configure error rates and depolarization

2. **Error Simulation**
   - Run circuits on Stim simulator or real hardware
   - Collect syndrome and measurement data

3. **Decoding**
   - Standard MWPM decoder
   - Bio-adaptive decoder with modified weights

4. **Analysis**
   - Compare logical error rates
   - Threshold calculation
   - Performance benchmarking

## Data Flow

```
Circuit → Stim Simulation → Error Data → Decoding → Results
                ↓                                        ↓
          Syndrome Extraction                    Logical Error Rate
                ↓                                        ↓
          MWPM Graph Building ←→ Bio-Adaptive Weighting
                ↓                                        ↓
          Matching Solution ←───────────────────────────┘
```

## Testing Strategy

- **Unit Tests**: Individual module testing in `tests/`
- **Integration Tests**: Full pipeline validation
- **Hardware Tests**: Real device execution and validation
- **Benchmarking**: Performance comparison simulations

Run tests with: `pytest`

## Development Workflow

1. Install development dependencies: `pip install -e ".[dev]"`
2. Make changes in feature branch
3. Run tests: `pytest --cov=src`
4. Format code: `black src/ tests/`
5. Lint: `flake8 src/ tests/`
6. Submit PR for review

## Dependencies

### Core
- `numpy`: Numerical computations
- `stim`: Stabilizer circuit simulation
- `pymatching`: MWPM decoder
- `matplotlib`: Visualization

### Optional
- `qiskit`: IBM Quantum integration
- `pytest`: Testing framework

See `requirements.txt` and `pyproject.toml` for full list.

## Performance Considerations

- Stim provides O(1) sampling for large circuits
- PyMatching uses efficient graph algorithms
- Bio-adaptive weights add minimal computational overhead
- Hardware execution time dominates real device runs

## Future Extensions

- Extended B-cell dynamics modeling
- Cytokine signaling integration
- Surface code hardware implementation
- Alternative decoder architectures
- Visualization improvements
