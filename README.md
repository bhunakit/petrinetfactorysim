# Wood Production Line Simulator

A stochastic Petri net simulation of a wood production line, implementing both Petri net concepts and Monte Carlo methods for practical analysis.

## Project Structure

```
├── app.py                 # Streamlit web application
├── gridsearch.py          # Parameter optimization
├── petrinet.py           # Core Petri net implementation
├── pyproject.toml        # Project dependencies and metadata
├── README.md             # This file
├── sim.py               # Stochastic simulation engine
├── visualize.py         # Visualization components
├── graphs/              # Generated visualizations
│   ├── buffer_levels.png
│   ├── Production.png
│   └── grid_search_results.csv
├── tests/               # Test suite
│   └── test_sim.py     # Simulation tests
└── __pycache__/        # Python cache files
```

## Features

- Full Petri net implementation with visualization
- Stochastic simulation of production line dynamics
- Interactive web interface using Streamlit
- Real-time visualization of buffer levels and system states 
- Monte Carlo analysis for robust performance metrics
- Parameter grid search optimization
- Automated test suite

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
```bash
pip install -e .
```

## Running the Application

1. Start the web interface:
```bash
streamlit run app.py
```

2. Run parameter optimization search:
```bash
python gridsearch.py
```

3. Run tests:
```bash
pytest tests/
```

## Usage

### Web Interface
1. Configure simulation parameters in the sidebar
2. Click "Run Simulation" to start
3. View results in the interactive dashboard:
   - Production rates
   - Buffer levels
   - Tool utilization
   - System visualization

### Grid Search
The `gridsearch.py` script performs parameter optimization across:
- Production mean times
- Work mean times
- Process mean times
- Tool occupation ratios

Results are saved to `graphs/grid_search_results.csv`.

## Generated Outputs

- `buffer_levels.png`: Time series of buffer occupancy
- `Production.png`: Petri net visualization
- `grid_search_results.csv`: Parameter optimization results

## Technical Details

### Simulation Parameters

- Production timings: Mean and standard deviation for manufacturing steps
- Tool availability: Occupation ratio and decay rate
- Buffer capacities: Dynamic monitoring and sizing
- Processing rates: Configurable for both parallel processing lines

### Output Metrics

- Production rate per hour
- Tool work rate when available
- Tool unavailability statistics
- Post-processing rates
- Recommended buffer sizes with standard deviations