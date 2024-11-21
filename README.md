# Wood Production Line Simulator

A stochastic Petri net simulation of a wood production line, implementing both theoretical Petri net concepts and Monte Carlo methods for practical analysis.

## Features

- Full Petri net implementation with visualization
- Stochastic simulation of production line dynamics
- Interactive web interface using Streamlit
- Real-time visualization of buffer levels and system states 
- Monte Carlo analysis for performance metrics

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
```bash
pip install -e .
```

## Project Structure

- `petrinet.py`: Core Petri net implementation
- `sim.py`: Stochastic simulation engine
- `visualize.py`: Visualization components
- `app.py`: Streamlit web application
- `tests/`: Test suite
  - `test_sim.py`: System behavior validation

## Testing

Run the test:
```bash
python -m pytest tests/test_sim.py -v
```

The tests validate:
- Tool availability impact on work rate
- Processing speed effect on buffer levels  
- Production rate consistency within bounds

For development:
```bash
pip install -e .[dev]
```

## Running

Start the web interface:
```bash
streamlit run app.py
```

## Usage

1. Configure simulation parameters in the sidebar
2. Click "Run Simulation" to start
3. View results in the interactive dashboard:
   - Production rates
   - Buffer levels
   - Tool utilization
   - System visualization

## Technical Details

### Simulation Parameters

- Production timings: Mean and standard deviation for manufacturing steps
- Tool availability: Occupation ratio and decay rate (the tool occupation ratio is logarithmically decayed throughout simulation duration to match reality and add stochastic behavior)
- Buffer capacities: Dynamic monitoring and sizing
- Processing rates: Configurable for both parallel processing lines

### Analysis Methods

- Stochastic event generation based on normal distributions
- Monte Carlo simulations for statistical robustness
- Buffer level tracking and visualization
- Tool availability analysis

### Output Metrics

- Production rate per hour
- Tool work rate when available
- Tool unavailability statistics
- Post-processing rates
- Recommended buffer sizes