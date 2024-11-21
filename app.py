import streamlit as st
from petrinet import *
from sim import TransitionConfig, TransitionParams, StochasticProductionSimulation
from visualize import visualize_results

def main():
    st.set_page_config(layout="wide")
    
    st.markdown("""
        <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.title("Simulation Parameters")
        
        with st.expander("Production Parameters", expanded=True):
            prod_mean = st.number_input("Production Mean Time", value=40.0, min_value=1.0)
            prod_sd = st.number_input("Production Time SD", value=5.0, min_value=0.0)
        
        with st.expander("Work Parameters", expanded=True):
            work_mean = st.number_input("Work Mean Time", value=20.0, min_value=1.0)
            work_sd = st.number_input("Work Time SD", value=10.0, min_value=0.0)
        
        with st.expander("Processing Parameters", expanded=True):
            process_mean = st.number_input("Processing Mean Time", value=30.0, min_value=1.0)
            process_sd = st.number_input("Processing Time SD", value=10.0, min_value=0.0)
        
        with st.expander("Tool Parameters", expanded=True):
            tool_occupy_mean = st.number_input("Tool Occupy Mean Time", value=0.0, min_value=0.0)
            tool_release_mean = st.number_input("Tool Release Mean Time", value=50.0, min_value=1.0)
            tool_release_sd = st.number_input("Tool Release Time SD", value=20.0, min_value=0.0)
            tool_ratio = st.slider("Tool Occupied Ratio", 0.0, 1.0, 0.15)
            tool_decay = st.slider("Tool Occupied Decay Rate", 0.0, 2.0, 0.8)
        
        with st.expander("Simulation Parameters", expanded=True):
            sim_duration = st.number_input("Simulation Duration (hours)", value=8.0, min_value=1.0)
            num_sims = st.number_input("Number of Simulations", value=100, min_value=1)
    
    if st.sidebar.button("Run Simulation", type="primary"):
        with st.spinner("Running simulation..."):

            config = TransitionConfig(
                produce=TransitionParams(prod_mean, prod_sd),
                work=TransitionParams(work_mean, work_sd),
                process1=TransitionParams(process_mean, process_sd),
                process2=TransitionParams(process_mean, process_sd),
                tool_occupy=TransitionParams(tool_occupy_mean, 0.0),
                tool_release=TransitionParams(tool_release_mean, tool_release_sd),
                tool_occupied_ratio=tool_ratio,
                tool_occupied_ratio_decay_rate=tool_decay
            )
            
            sim = StochasticProductionSimulation(
                transition_config=config, 
                simulation_duration=3600.0 * sim_duration
            )
            
            results = sim.run_monte_carlo(num_simulations=num_sims)
            
            visualize_results(results)
    
    else:
        st.title("Wood Production Line Simulator")
        st.write("""
        Welcome to the Wood Production Line Simulator! This tool helps you:
        - Simulate production line behavior
        - Analyze buffer requirements
        - Optimize tool utilization
        - Visualize system dynamics
        
        To begin:
        1. Adjust parameters in the sidebar
        2. Select a preset or customize your own
        3. Click 'Run Simulation'
        """)

if __name__ == "__main__":
    main()