from sim import TransitionConfig, TransitionParams, StochasticProductionSimulation
import pandas as pd
import numpy as np
from itertools import product

def run_grid_search():
    param_grid = {
        'prod_mean': [30.0, 40.0, 50.0],
        'work_mean': [15.0, 20.0, 25.0],
        'process_mean': [25.0, 30.0, 35.0],
        'tool_ratio': [0.1, 0.15, 0.2]
    }
    
    fixed_params = {
        'prod_sd': 5.0,
        'work_sd': 10.0,
        'process_sd': 10.0,
        'tool_occupy_mean': 5.0,
        'tool_release_mean': 50.0,
        'tool_release_sd': 20.0,
        'tool_decay': 0.8
    }

    results = []
    
    keys, values = zip(*param_grid.items())
    for params in product(*values):
        current_params = dict(zip(keys, params))
        
        config = TransitionConfig(
            produce=TransitionParams(current_params['prod_mean'], fixed_params['prod_sd']),
            work=TransitionParams(current_params['work_mean'], fixed_params['work_sd']),
            process1=TransitionParams(current_params['process_mean'], fixed_params['process_sd']),
            process2=TransitionParams(current_params['process_mean'], fixed_params['process_sd']),
            tool_occupy=TransitionParams(fixed_params['tool_occupy_mean'], 0.0),
            tool_release=TransitionParams(fixed_params['tool_release_mean'], fixed_params['tool_release_sd']),
            tool_occupied_ratio=current_params['tool_ratio'],
            tool_occupied_ratio_decay_rate=fixed_params['tool_decay']
        )
        
        buffer_sizes = {'buffer1': [], 'buffer2': [], 'buffer3': []}
        n_runs = 10
        
        sim = StochasticProductionSimulation(config, simulation_duration=3600.0*8.0)
        
        for _ in range(n_runs):
            results_run = sim.run_monte_carlo(num_simulations=10)
            for buffer, size in results_run.buffer_sizes.items():
                buffer_sizes[buffer].append(size)
        
        result_row = {
            'prod_mean': current_params['prod_mean'],
            'work_mean': current_params['work_mean'],
            'process_mean': current_params['process_mean'],
            'tool_ratio': current_params['tool_ratio'],
            'buffer1_mean': np.mean(buffer_sizes['buffer1']),
            'buffer1_std': np.std(buffer_sizes['buffer1']),
            'buffer2_mean': np.mean(buffer_sizes['buffer2']),
            'buffer2_std': np.std(buffer_sizes['buffer2']),
            'buffer3_mean': np.mean(buffer_sizes['buffer3']),
            'buffer3_std': np.std(buffer_sizes['buffer3'])
        }
        
        results.append(result_row)
        print(f"Completed configuration: {current_params}")
    
    df = pd.DataFrame(results)
    
    df.to_csv('graphs/grid_search_results.csv', index=False)
    
    return df

if __name__ == "__main__":
    df = run_grid_search()

    print(df.head())
