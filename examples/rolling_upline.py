from logging import log
from flightdata.fields import Field

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from flightanalysis import Section, State, FlightLine
from flightanalysis.flightline import Box
from flightdata import Flight, Fields
from flightplotting.traces import meshes, cgtrace, tiptrace, boxfrustumEdges, ribbon

from flightplotting.model import OBJ
from geometry import Point, Quaternion, Transformation
import os
import tkinter as tk

scale = 10
obj = OBJ.from_obj_file('../data/models/ColdDraftF3APlane.obj').transform(Transformation(
    Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
))
scaled_obj = obj.scale(scale * 1.85)
duration = 32

# Y center of aerobatic box is 150 meters from pilot box, 135 meters from runway centerline
# far edge is 160 meters from runway centerline for a 50m total depth
initPos = Point(0, 160, 10)
initQ = Quaternion.from_euler(Point(np.pi, -np.pi/2, 0)) # inverted upline
initVel = Point(600/32, 0, 0)
initRates = Point(np.radians(360/duration), 0, 0)

initState = State(initPos, initQ,
                  initVel, initRates)

interval = .1
t = np.arange(0, duration + interval, .1)
sec = Section.from_line(initState, t)

flightline = FlightLine.from_box(Box.from_json("AAMeast_box.json"))

traces = []
traces += [mesh for mesh in meshes(scaled_obj, 8, sec, 'orange', flightline.transform_to)]
traces += ribbon(scale * 1.8, sec, flightline.transform_to)
traces += tiptrace(sec, scale * 1.85, flightline.transform_to)
traces += boxfrustumEdges()


fig = go.Figure(
    traces,
    layout=go.Layout(template="flight3d+judge_view")
)

# save interactive figure
from pathlib import Path
basepath = str(Path.home()) + "/temp/"
fname = "rolling_upline.html"
fig.write_html(basepath + fname)
fig.show()
