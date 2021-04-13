from logging import log
from flightdata.fields import Field
import streamlit as st

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from flightanalysis import Section, State, FlightLine
from flightdata import Flight, Fields
from flightplotting.plots import meshes, trace, tiptrace
from flightplotting.model import OBJ
from geometry import Point, Quaternion, Transformation
import os
import tkinter as tk
import easygui



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

logfile = '/home/tom/Desktop/logs/00000167.csv'

if st.sidebar.button("read log csv"):
    try:
        newlog = easygui.fileopenbox(default="/media/tom/storage/shared/flight_logs/")
        if os.path.splitext(newlog)[1] == '.csv':
            logfile = newlog
    except Exception as ex:
        st.write("error: " + str(ex))

bin = Flight.from_csv(logfile)


@st.cache  # TODO this may not notice changes to submodules
def load_data(bin):
    return bin, Section.from_flight(bin, FlightLine.from_covariance(bin))


flight, seq = load_data(bin)

obj = OBJ.from_obj_file('data/models/ColdDraftF3APlane.obj').transform(Transformation(
    Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
))


npoints = st.sidebar.number_input("Number of Models", 0, 50, value=20)
scale = st.sidebar.number_input("Model Scale Factor", 1.0, 50.0, value=10.0)

scaled_obj = obj.scale(scale)

showmesh = st.sidebar.checkbox("Show Models", False)
cgtrace = st.sidebar.checkbox("Show CG Trace", True)
ttrace = st.sidebar.checkbox("Show Tip Trace", False)


plot_range = st.slider(
    "plot range", 0.0, flight.duration, (0.0, flight.duration))




def make_plot_data(seq, plot_range, npoints, showmesh, cgtrace, ttrace):
    sec = seq.subset(*plot_range)
    traces = []
    if showmesh:
        traces += [mesh for mesh in meshes(scaled_obj, npoints, sec)]
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
            scene=dict(aspectmode='data'),
            height=800,
        )),
    use_container_width=True
)


#initial = State.from_posattvel(
#            Point(30, 170, 150),
#            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
#            Point(30, 0, 0)
#        )
#
#initial.data[State.vars.brvel] = [np.pi, 0, 0]
#
#line = Section.from_line(initial, np.linspace(0, 1, 5))