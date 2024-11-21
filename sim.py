from petrinet import *
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

@dataclass
class TransitionParams:
    mean_time: float
    time_sd: float

@dataclass
class TransitionConfig:
    produce: TransitionParams
    work: TransitionParams
    process1: TransitionParams
    process2: TransitionParams
    tool_occupy: TransitionParams
    tool_release: TransitionParams
    tool_occupied_ratio: float
    tool_occupied_ratio_decay_rate: float

@dataclass
class SimulationEvent:
    time: float
    type: str  

@dataclass
class SimulationState:
    events: List[SimulationEvent]
    buffer_levels: Dict[str, List[int]]
    tool_state: List[bool]  # True if available
    work_when_tool_available: List[bool]

@dataclass
class SimulationResults:
    production_rate: float
    tool_work_rate: float
    tool_unavailable_stats: Tuple[float, float]
    post_processing_rate: float
    buffer_sizes: Dict[str, int]
    buffer_levels: Dict[str, List[int]]

class StochasticProductionSimulation:
    def __init__(self, transition_config: TransitionConfig, simulation_duration: float = 3600.0):
        self.production = Place("production", 1)
        self.buffer1 = Place("buffer1", 0)
        self.tool = Place("tool", 1)
        self.tool_occupied = Place("tool_occupied", 0)
        self.buffer2 = Place("buffer2", 0)
        self.buffer3 = Place("buffer3", 0)
        self.robot1 = Place("robot1", 1)
        self.robot2 = Place("robot2", 1)
        
        self.produce = Transition("produce", 
            [Arc(self.production, 1)],
            [Arc(self.production, 1), Arc(self.buffer1, 1)])

        self.work = Transition("work", 
            [Arc(self.buffer1, 1), Arc(self.tool, 1)],
            [Arc(self.tool, 1), Arc(self.buffer2, 1), Arc(self.buffer3, 1)])

        self.process1 = Transition("process1",
            [Arc(self.buffer2, 1), Arc(self.robot1, 1)],
            [Arc(self.robot1, 1)])

        self.process2 = Transition("process2", 
            [Arc(self.buffer3, 1), Arc(self.robot2, 1)],
            [Arc(self.robot2, 1)])

        self.tool_occupy = Transition("tool_occupy",
            [Arc(self.tool, 1)],
            [Arc(self.tool_occupied, 1)])

        self.tool_release = Transition("tool_release",
            [Arc(self.tool_occupied, 1)],
            [Arc(self.tool, 1)])
        
        self.petri_net = PetriNet(
            name="Production",
            places=[self.production, self.buffer1, self.buffer2, self.buffer3, 
                   self.tool, self.tool_occupied, self.robot1, self.robot2],
            transitions=[self.produce, self.work, self.process1, self.process2, 
                        self.tool_occupy, self.tool_release],
            arcs=[arc for t in [self.produce, self.work, self.process1, self.process2, 
                               self.tool_occupy, self.tool_release] 
                  for arc in t.input_arcs + t.output_arcs]
        )
        
        self.transition_params = {
            "produce": transition_config.produce,
            "work": transition_config.work,
            "process1": transition_config.process1,
            "process2": transition_config.process2,
            "tool_occupy": transition_config.tool_occupy,
            "tool_release": transition_config.tool_release
        }
        self.tool_occupied_ratio = transition_config.tool_occupied_ratio
        self.tool_occupied_decay_rate = transition_config.tool_occupied_ratio_decay_rate
        self.simulation_duration = simulation_duration

    def run_single_simulation(self) -> SimulationState:
        """Run a single simulation and track events and states"""
        events = []
        buffer_levels = {"buffer1": [], "buffer2": [], "buffer3": []}
        tool_state = []
        work_when_tool_available = []
        
        # Track when transitions can next fire
        next_fire_times = {name: 0.0 for name in self.transition_params}
        current_time = 0.0
        
        while current_time <= self.simulation_duration:
            # Record current state
            buffer_levels["buffer1"].append(self.buffer1.tokens)
            buffer_levels["buffer2"].append(self.buffer2.tokens)
            buffer_levels["buffer3"].append(self.buffer3.tokens)
            tool_available = self.tool.tokens == 1
            tool_state.append(tool_available)

            # Handle tool occupation
            prob = self.tool_occupied_ratio * (1 / (1 + self.tool_occupied_decay_rate*np.log(1 + current_time/3600)))
            if (self.tool.tokens > 0 and 
                current_time >= next_fire_times["tool_occupy"] and
                np.random.random() < prob):
                if self.tool_occupy.fire():
                    events.append(SimulationEvent(current_time, "tool_occupied"))
                    params = self.transition_params["tool_occupy"]
                    next_fire_times["tool_occupy"] = current_time + max(1.0, np.random.normal(params.mean_time, params.time_sd))
                    work_when_tool_available.append(False)
            
            # Process transitions
            for name, transition in [
                ("tool_release", self.tool_release),
                ("produce", self.produce),
                ("work", self.work),
                ("process1", self.process1),
                ("process2", self.process2)
            ]:
                if current_time >= next_fire_times[name]:
                    if transition.is_enabled():
                        if transition.fire():
                            events.append(SimulationEvent(current_time, name))
                            params = self.transition_params[name]
                            next_fire_time = current_time + max(1.0, np.random.normal(params.mean_time, params.time_sd))
                            next_fire_times[name] = next_fire_time

                            if name == "work" and tool_available:
                                work_when_tool_available.append(True)



            current_time += 1.0
        
        return SimulationState(events, buffer_levels, tool_state, work_when_tool_available)

    def analyze_simulation_state(self, state: SimulationState) -> SimulationResults:
        """Analyze a simulation state to produce results"""
        # print(state)
        # Count events
        production_events = [e for e in state.events if e.type == "produce"]
        work_events = [e for e in state.events if e.type == "work"]
        process1_events = [e for e in state.events if e.type == "process1"]
        process2_events = [e for e in state.events if e.type == "process2"]
        tool_occupied_events = [e for e in state.events if e.type == "tool_occupied"]
        
        # Calculate tool unavailability periods
        tool_available_time = sum(1 for x in state.tool_state if x)
        tool_unavailable_time = len(state.tool_state) - tool_available_time
        
        # Calculate rates
        hours = self.simulation_duration / 3600

        # Production Rate
        production_rate = len(production_events) / hours

        # Work rate if tool is available
        work_rate = sum(1 for x in state.work_when_tool_available if x) / hours

        # Post processing rate
        post_processing_rate = (len(process1_events) + len(process2_events)) / hours
        
        # Calculate tool unavailability stats
        tool_unavail_freq = len(tool_occupied_events) / hours
        avg_unavail_duration = tool_unavailable_time / len(tool_occupied_events) if tool_occupied_events else 0
        
        # Calculate buffer sizes
        buffer_sizes = {
            name: int(np.ceil(max(levels)))
            for name, levels in state.buffer_levels.items()
        }

        # Get buffer levels
        buffer_levels=state.buffer_levels
        
        return SimulationResults(
            production_rate=production_rate,
            tool_work_rate=work_rate,
            tool_unavailable_stats=(tool_unavail_freq, avg_unavail_duration),
            post_processing_rate=post_processing_rate,
            buffer_sizes=buffer_sizes,
            buffer_levels=buffer_levels
        )

    def run_monte_carlo(self, num_simulations: int = 100) -> SimulationResults:
        """Run multiple simulations and average results"""
        results = []
        for _ in range(num_simulations):
            # Reset state
            for place in self.petri_net.places:
                place.tokens = 1 if place in [self.production, self.robot1, self.robot2] else 0
                if place == self.tool:
                    place.tokens = 1
            
            state = self.run_single_simulation()
            results.append(self.analyze_simulation_state(state))

        re_bl = {'buffer1': [], 'buffer2': [], 'buffer3': []}
        for r in results:
            buffer_level = r.buffer_levels
            for k, v in buffer_level.items():
                re_bl[k].append(np.array(v))
        for k, v in re_bl.items():
            re_bl[k] = np.mean(v, axis=0)

        # Average results
        return SimulationResults(
            production_rate=np.mean([r.production_rate for r in results]),
            tool_work_rate=np.mean([r.tool_work_rate for r in results]),
            tool_unavailable_stats=(
                np.mean([r.tool_unavailable_stats[0] for r in results]),
                np.mean([r.tool_unavailable_stats[1] for r in results])
            ),
            post_processing_rate=np.mean([r.post_processing_rate for r in results]),
            buffer_sizes={
                name: int(np.ceil(np.percentile([r.buffer_sizes[name] for r in results], 95)))
                for name in ['buffer1', 'buffer2', 'buffer3']
            },
            buffer_levels=re_bl
        )

    def plot_buffer_levels(self, results: SimulationResults):
        """Plot buffer levels over time"""
        plt.figure(figsize=(10, 6))
        for buffer_name, levels in results.buffer_levels.items():
            plt.plot(levels, label=buffer_name)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Buffer Level')
        plt.title('Buffer Levels Over Time')
        plt.legend()
        plt.savefig('graphs/buffer_levels.png')
        plt.close()

def main():
    transition_config = TransitionConfig(
        produce=TransitionParams(40.0, 5.0), 
        work=TransitionParams(20.0, 10.0),     
        process1=TransitionParams(30.0, 10.0),
        process2=TransitionParams(30.0, 10.0),
        tool_occupy=TransitionParams(5.0, 0.0),
        tool_release=TransitionParams(50.0, 20.0),  
        tool_occupied_ratio=0.15, 
        tool_occupied_ratio_decay_rate=0.8
    )
    sim = StochasticProductionSimulation(transition_config=transition_config, simulation_duration=3600.0*8.0)
    sim.petri_net.visualize()
    results = sim.run_monte_carlo(num_simulations=100)
    
    print("\nSimulation Results:")
    print(f"\n1. Production Rate: {results.production_rate:.2f} items/hour")
    print(f"2. Tool Work Rate when Available: {results.tool_work_rate:.2f} operations/hour")
    print(f"3. Tool Unavailability:")
    print(f"   - Frequency: {results.tool_unavailable_stats[0]:.2f} times/hour")
    print(f"   - Average Duration: {results.tool_unavailable_stats[1]:.2f} seconds")
    print(f"4. Post-Processing Rate: {results.post_processing_rate:.2f} items/hour")
    
    print("\nRecommended Buffer Sizes:")
    for buffer, size in results.buffer_sizes.items():
        print(f"  {buffer}: {size} items")

    sim.plot_buffer_levels(results)

if __name__ == "__main__":
    main()