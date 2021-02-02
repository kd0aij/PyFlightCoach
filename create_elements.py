from flightdata.fields import Field
import streamlit as st

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from flightanalysis import Section, State, FlightLine
from flightdata import Flight, Fields
from components.plots import meshes, trace, tiptrace
from geometry import Point, Quaternion


st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 90%;
    }}
</style>
""",
        unsafe_allow_html=True,
    )


#initial = State(
#            Point(30, 170, 150),
#            Quaternion.from_euler(Point(0, 0, np.pi)),
#            Point(30, 0, 0),
#            Point(np.pi, 0, 0)
#        )

initial = State(
            Point(0, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(10 * np.pi, 0, 0), # 620 m in 10 seconds
            Point(0, np.pi / 5, 0) # 
        )

seq = Section.from_radius(initial, np.linspace(0, 10, 10))


npoints = st.sidebar.number_input("Number of Models", 0, 50, value=20)
scale = st.sidebar.number_input("Model Scale Factor", 1.0, 50.0, value=10.0)
showmesh = st.sidebar.checkbox("Show Models", False)
cgtrace = st.sidebar.checkbox("Show CG Trace", True)
ttrace = st.sidebar.checkbox("Show Tip Trace", False)


plot_range = st.slider(
    "plot range", 0.0, 10.0, (0.0, 10.0))

def make_plot_data(seq, plot_range, npoints, showmesh, cgtrace, ttrace):
    sec = seq.subset(*plot_range)
    traces = []
    if showmesh:
        traces += [mesh for mesh in meshes(npoints, scale, sec)]
    if cgtrace:
        traces += [trace(sec)]
    if ttrace:
        traces += tiptrace(sec, scale * 1.85)
    return traces




st.plotly_chart(
    go.Figure(
        make_plot_data(seq, plot_range, npoints, showmesh, cgtrace, ttrace),
        layout=go.Layout(
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(aspectmode='data')
        )),
    use_container_width=True
)