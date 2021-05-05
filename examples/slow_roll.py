from logging import log
from flightdata.fields import Field

import numpy as np
import pandas as pd

import plotly.graph_objects as go
import plotly.io as pio
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

flightline = FlightLine.from_box(Box.from_json("AAMeast_box.json"))

# Y center of aerobatic box is 150 meters from pilot box, 135 meters from runway centerline
# far edge is 160 meters from runway centerline for a 50m total depth
initPos = Point(-300, 160, 150)
initQ = Quaternion.from_euler(Point(np.pi, 0, 0)) # noninverted
initVel = Point(600/32, 0, 0)
initRates = Point(np.radians(360/duration), 0, 0)

initState = State(initPos, initQ, initVel, initRates)

interval = .1
t = np.arange(0, duration + interval, .1)
sec = Section.from_line(initState, t)

traces = []

# modelx = m.vertices.data[:, 0]
#         x, y, z = self.vertices.data[:, :3].T
#         I, J, K = self.faces.T

# concatenation of model x coords
#np.concatenate([obj.transform(state[i].transform).vertices.data[:,0] for i in range(2)],axis=None)

traces += [mesh for mesh in meshes(scaled_obj, 8, sec, 'orange', flightline.transform_to)]
traces += ribbon(scale * 1.8, sec, flightline.transform_to)
traces += tiptrace(sec, scale * 1.85, flightline.transform_to)
traces += boxfrustumEdges()


pio.templates["mw_flight3d"] = go.layout.Template(layout=go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    scene=dict(
        aspectmode='data',
        xaxis=dict(showticklabels=True),
        yaxis=dict(showticklabels=True),
        zaxis=dict(showticklabels=True)
    ),
    legend=dict(
        font=dict(size=20),
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
))

pio.templates["mw_view"] = go.layout.Template(layout=go.Layout(
    scene_camera=dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=0.0, y=-1.0, z=0),
        projection=dict(type='orthographic')
    )
))

fig = go.Figure(
    traces,
    layout=go.Layout(template="mw_flight3d+mw_view")
)

# save interactive figure
from pathlib import Path
basepath = str(Path.home()) + "/temp/"
fname = "slowroll.html"
fig.write_html(basepath + fname)
fig.show()
