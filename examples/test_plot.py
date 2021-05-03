#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 16:16:44 2021

@author: markw
"""

from flightanalysis import Section, FlightLine
from flightanalysis.flightline import Box
from flightdata import Flight
import numpy as np
from flightplotting.traces import tiptrace, meshes, ribbon, boxtrace, boxfrustum, boxfrustumEdges, create_3d_plot
from flightplotting.model import OBJ
from geometry import Transformation, Point, Quaternion, Points, GPSPosition
import plotly.graph_objects as go

obj = OBJ.from_obj_file('/home/markw/linux_git/kd0aij/PyFlightCoach/data/models/ColdDraftF3APlane.obj').transform(
    Transformation(
        Point(0.75, 0, 0),
        Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
    )
)

# AAM East Field: FlightLine.from_covariance heading is off by 180 degrees
#binfile = "P21_032521"
binfile = "M21_032521"
heading = np.radians(16)

bin = Flight.from_log('/home/markw/linux_git/kd0aij/PyFlightCoach/data/logs/' + binfile + ".BIN")
flightline = FlightLine.from_heading(bin, heading)
flightline.to_json("AAMeast_flightline.json")

box = Box(
        'heading',
        GPSPosition(
            bin.data.iloc[0].global_position_latitude,
            bin.data.iloc[0].global_position_longitude
        ),
        heading
    )
box.to_json("AAMeast_box.json")

sec = Section.from_flight(bin, flightline)

# examples
#binfile = "00000100"
#binfile = "00000130"

# bin = Flight.from_log('../../data/logs/' + binfile + ".BIN")
# sec = Section.from_flight(bin, FlightLine.from_covariance(bin))

start = 60
end = 82
subSec = sec.subset(start, end)

span = 1.85
scale = 5
dt = end - start
# draw models 1 second apart
numModels = int(dt)

# use orthographic projection for rendering to canvas
fig = go.Figure(
        #boxfrustum() +
        boxfrustumEdges() +
        tiptrace(subSec, scale * span, flightline.transform_to) +
        ribbon(scale * span * .9, subSec, flightline.transform_to) +
        meshes(obj.scale(scale), numModels, subSec, 'orange', flightline.transform_to),
        layout=go.Layout(
            margin=dict(autoexpand=True),
            scene=dict(aspectmode='data', camera_projection_type="orthographic")
        ))
camera = dict(
    eye=dict(x=0, y=-2.5, z=0)
)
fig.update_layout(scene_camera=camera, title=binfile)
#fig.update_layout(showlegend=False)

# save interactive figure
from pathlib import Path
basepath = str(Path.home()) + "/temp/"
fname = "%s_%s-%s.html" % (binfile, start, end)
fig.write_html(basepath + fname)
fig.show()

# # create and save 3-views
# import plotly.io as pio
# pio.renderers.default = 'svg'

# name = 'X view'
# camera = dict(
#     eye=dict(x=2.5, y=0, z=0)
# )
# fig.update_layout(scene_camera=camera, title_text=name)
# fig.write_image(basepath + "Xview.svg")
# #fig.show()

# name = 'Y view'
# camera = dict(
#     eye=dict(x=0, y=2.5, z=0)
# )
# fig.update_layout(scene_camera=camera, title=name)
# fig.write_image(basepath + "Yview.svg")
# #fig.show()

# name = 'Z View'
# camera = dict(
#     eye=dict(x=0, y=0, z=2.5)
# )
# fig.update_layout(scene_camera=camera, title=name)
# fig.write_image(basepath + "Zview.svg")
# #fig.show()
