import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import graphviz
import numpy as np
import pandas as pd

def plot_buffer_levels(buffer_levels):
    # Convert buffer levels to pandas DataFrame for easier plotting
    df = pd.DataFrame(buffer_levels)
    df['time'] = np.arange(len(df)) # Add time index
    
    # Create figure with plotly
    fig = go.Figure()
    
    # Add traces for each buffer
    for column in ['buffer1', 'buffer2', 'buffer3']:
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df[column],
                name=column,
                mode='lines',
                hovertemplate=
                '<b>Time</b>: %{x:.0f}s<br>' +
                '<b>Level</b>: %{y:.0f}<br>',
            )
        )
    
    # Update layout
    fig.update_layout(
        title='Buffer Levels Over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Buffer Level',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        template='plotly_white'
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def create_petri_net_graph():
    # Create a new directed graph
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')
    
    # Define styles
    dot.attr('node', shape='circle', style='filled', fillcolor='yellow', 
            fontname='Arial', fontsize='12', width='0.8', height='0.8')
    
    # Add places
    places = ['Production', 'Buffer1', 'Buffer2', 'Buffer3', 
             'Tool', 'Tool Occupied', 'Robot1', 'Robot2']
    for place in places:
        dot.node(place, place)
    
    # Style for transitions
    dot.attr('node', shape='rect', style='filled', fillcolor='lightgray',
            width='0.5', height='0.3')
    
    # Add transitions and edges
    dot.node('T1', 'Produce')
    dot.node('T2', 'Work')
    dot.node('T3', 'Process1')
    dot.node('T4', 'Process2')
    dot.node('T5', 'Tool\nOccupy')
    dot.node('T6', 'Tool\nRelease')
    
    # Add edges
    edges = [
        ('Production', 'T1'),
        ('T1', 'Production'),
        ('T1', 'Buffer1'),
        ('Buffer1', 'T2'),
        ('Tool', 'T2'),
        ('T2', 'Tool'),
        ('T2', 'Buffer2'),
        ('T2', 'Buffer3'),
        ('Buffer2', 'T3'),
        ('Robot1', 'T3'),
        ('T3', 'Robot1'),
        ('Buffer3', 'T4'),
        ('Robot2', 'T4'),
        ('T4', 'Robot2'),
        ('Tool', 'T5'),
        ('T5', 'Tool Occupied'),
        ('Tool Occupied', 'T6'),
        ('T6', 'Tool')
    ]
    
    for edge in edges:
        dot.edge(edge[0], edge[1])
    
    # Return the dot object
    return dot

def display_metrics(results):
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Production Rate",
            value=f"{results.production_rate:.2f}/hr",
        )
        
        st.metric(
            label="Tool Work Rate",
            value=f"{results.tool_work_rate:.2f}/hr"
        )
    
    with col2:
        st.metric(
            label="Tool Unavailability Frequency",
            value=f"{results.tool_unavailable_stats[0]:.2f}/hr",
        )
        
        st.metric(
            label="Tool Unavailable Duration",
            value=f"{results.tool_unavailable_stats[1]:.1f}s"
        )
    
    with col3:
        st.metric(
            label="Post-Processing Rate",
            value=f"{results.post_processing_rate:.2f}/hr"
        )
        
        # Display buffer sizes in a more compact way
        st.metric(
            label="Max Buffer Sizes",
            value=f"{max(results.buffer_sizes.values())} units"
        )

def visualize_results(results):
    st.title("Production Line Simulation Results")
    
    # Display metrics
    display_metrics(results)
    
    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Buffer Levels", "Petri Net Model"])
    
    with tab1:
        st.subheader("Buffer Levels Over Time")
        plot_buffer_levels(results.buffer_levels)
        
        # Add buffer statistics
        st.caption("Buffer Statistics")
        stats_cols = st.columns(3)
        for i, (buffer, levels) in enumerate(results.buffer_levels.items()):
            with stats_cols[i]:
                avg_level = np.mean(levels)
                max_level = np.max(levels)
                st.markdown(f"**{buffer}**")
                st.markdown(f"Average: {avg_level:.1f}")
                st.markdown(f"Maximum: {max_level:.1f}")
    
    with tab2:
        st.subheader("Petri Net Model")
        # Create and display Petri net
        dot = create_petri_net_graph()
        st.graphviz_chart(dot)
        
        # Add legend/explanation
        st.caption("Petri Net Components:")
        st.markdown("""
        - **Circles**: Places (buffers, resources)
        - **Rectangles**: Transitions (operations)
        - **Arrows**: Flow of materials/resources
        """)