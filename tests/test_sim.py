import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sim import TransitionConfig, TransitionParams, StochasticProductionSimulation
import numpy as np

def create_base_config():
    return TransitionConfig(
        produce=TransitionParams(40.0, 5.0),
        work=TransitionParams(20.0, 10.0),
        process1=TransitionParams(30.0, 10.0),
        process2=TransitionParams(30.0, 10.0),
        tool_occupy=TransitionParams(5.0, 0.0),
        tool_release=TransitionParams(50.0, 20.0),
        tool_occupied_ratio=0.15,
        tool_occupied_ratio_decay_rate=0.8
    )

def test_tool_availability_impact():
    """Test that lower tool occupation leads to higher work rate"""
    base_config = create_base_config()
    
    # Run simulation with high tool occupation
    high_occupation_config = TransitionConfig(
        **{**base_config.__dict__, 
           'tool_occupied_ratio': 0.8,
           'tool_occupied_ratio_decay_rate': 0.1}
    )
    sim_high = StochasticProductionSimulation(
        transition_config=high_occupation_config,
        simulation_duration=3600.0
    )
    results_high = sim_high.run_monte_carlo(num_simulations=50)
    
    # Run simulation with low tool occupation
    low_occupation_config = TransitionConfig(
        **{**base_config.__dict__,
           'tool_occupied_ratio': 0.2,
           'tool_occupied_ratio_decay_rate': 0.9}
    )
    sim_low = StochasticProductionSimulation(
        transition_config=low_occupation_config,
        simulation_duration=3600.0
    )
    results_low = sim_low.run_monte_carlo(num_simulations=50)
    
    # Assert work rate is higher with lower tool occupation
    assert results_low.tool_work_rate > results_high.tool_work_rate

def test_processing_speed_impact():
    """Test that faster processing reduces buffer levels"""
    base_config = create_base_config()
    
    # Run simulation with slow processing
    slow_config = TransitionConfig(
        **{**base_config.__dict__,
           'process1': TransitionParams(60.0, 10.0),
           'process2': TransitionParams(60.0, 10.0)}
    )
    sim_slow = StochasticProductionSimulation(
        transition_config=slow_config,
        simulation_duration=3600.0
    )
    results_slow = sim_slow.run_monte_carlo(num_simulations=50)
    
    # Run simulation with fast processing
    fast_config = TransitionConfig(
        **{**base_config.__dict__,
           'process1': TransitionParams(15.0, 5.0),
           'process2': TransitionParams(15.0, 5.0)}
    )
    sim_fast = StochasticProductionSimulation(
        transition_config=fast_config,
        simulation_duration=3600.0
    )
    results_fast = sim_fast.run_monte_carlo(num_simulations=50)
    
    # Assert buffer sizes are smaller with faster processing
    assert max(results_fast.buffer_sizes.values()) < max(results_slow.buffer_sizes.values())


def test_production_rate_consistency():
    """Test that production rate stays within expected bounds"""
    config = create_base_config()
    sim = StochasticProductionSimulation(
        transition_config=config,
        simulation_duration=3600.0 * 8  # 8 hours
    )
    
    # Run multiple simulations
    results = []
    for _ in range(10):
        result = sim.run_monte_carlo(num_simulations=20)
        results.append(result.production_rate)
    
    # Calculate statistics
    mean_rate = np.mean(results)
    std_rate = np.std(results)
    
    # Assert production rate is within expected bounds
    # Based on configured mean times, should be roughly 60-100 items/hour
    assert 60 <= mean_rate <= 100
    # Standard deviation should be relatively small
    assert std_rate < mean_rate * 0.2  # Within 20% of mean