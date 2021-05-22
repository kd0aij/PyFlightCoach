#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 16:16:44 2021

@author: markw
"""

from flightanalysis import Section, FlightLine, State
from flightanalysis.flightline import Box
from flightdata import Flight
import numpy as np
from math import pi
from flightplotting.traces import tiptrace, meshes, ribbon, boxtrace, \
    boxfrustum, boxfrustumEdges, create_3d_plot, genManeuverRPY, wrapPi
from flightplotting.model import OBJ
from geometry import Transformation, Point, Quaternion, Points, GPSPosition
import plotly.graph_objects as go

obj = OBJ.from_obj_file('/home/markw/linux_git/kd0aij/PyFlightCoach/data/models/ColdDraftF3APlane.obj').transform(
    Transformation(
        Point(0.75, 0, 0),
        Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
    )
)

# Thomas David's log
FC_examples = '/mnt/c/Users/markw/GoogleDrive/blackbox_logs/FlightCoach/examples/logs/'
binfile = '00000100'
bin = Flight.from_log(FC_examples + binfile + '.BIN')
origin = [51.4594504400,   -2.7912540674]
# runway heading from Octave (degrees CW from North)
heading = np.radians(-122)
# If pilot north is flightline heading:
# heading = wrapPi(heading + pi/2)
box = Box(
        'heading',
        GPSPosition(
            origin[0],
            origin[1]
        ),
        heading
    )
box.to_json("TD_box.json")

print("Runway heading (CW from North) is {:5.1f} (East) / {:5.1f} (West)".format(
             np.degrees(heading), np.degrees(wrapPi(heading+pi))))

start = 108
end = 154

# AAM East Field: FlightLine.from_covariance heading is off by 180 degrees
#binfile = "P21_032521"
# binfile = "M21_032521"
# bin = Flight.from_log('/home/markw/linux_git/kd0aij/PyFlightCoach/data/logs/' + binfile + ".BIN")
# heading = np.radians(16)
# pilot_box = [39.842288, -105.212928]
# box = Box(
#         'heading',
#         GPSPosition(
#             pilot_box[0],
#             pilot_box[1]
#         ),
#         heading
#     )
# box.to_json("AAMeast_box.json")

flightline = FlightLine.from_box(box)
sec = Section.from_flight(bin, flightline)

# examples
#binfile = "00000100"
#binfile = "00000130"

# bin = Flight.from_log('../../data/logs/' + binfile + ".BIN")
# sec = Section.from_flight(bin, FlightLine.from_covariance(bin))

# start = 275
# end = 286
# start = 60
# end = 82

subSec = sec.subset(start, end)

mingspd = 10
# TODO: lower pitch thresholds seem to be best for reducing errors in calculated maneuver roll
pThresh = np.radians(30)
# TODO: why is flightline.transform_to the same as transform_from?
[roll, pitch, wca, wca_axis] = genManeuverRPY(subSec, heading, mingspd, pThresh, flightline.transform_to)

span = 1.85
scale = 5
dt = end - start
# draw models 1 second apart
numModels = int(dt)

# use orthographic projection for rendering to canvas
fig = go.Figure(
        #boxfrustum() +
        # boxfrustumEdges() +
        tiptrace(subSec, scale * span, roll, pitch, wca) +
        ribbon(scale * span * .9, subSec, roll) +
        meshes(obj.scale(scale), numModels, subSec, 'orange', flightline.transform_to),
        layout=go.Layout(
            margin=dict(l=0, r=0, t=1, b=0, autoexpand=True),
            legend=dict(
                font=dict(size=20),
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
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
