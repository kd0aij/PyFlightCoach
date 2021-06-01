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
# FC_examples = '/mnt/c/Users/markw/GoogleDrive/blackbox_logs/FlightCoach/examples/logs/'
# flight = Flight.from_log(FC_examples + logfile + '.BIN')
# flight.to_csv('data/logs/flight_csvs/100.csv')

# vertical 8
# logfile = '100'
# start = 108
# end = 154

logfile = '141'
start = 221
end = 242

flight = Flight.from_csv('data/logs/flight_csvs/'+ logfile + '.csv')
firstGPSpos = flight.origin()
print("firstGPS position:", firstGPSpos)

pilot_box = GPSPosition(51.4594504400, -2.7912540674)
# pilot north is roughly SE
heading = np.radians(148)

# # AAM East Field: FlightLine.from_covariance heading is off by 180 degrees
# logfile = "P21_032521"
# # logfile = "M21_032521"
# flight = Flight.from_log('/home/markw/linux_git/kd0aij/PyFlightCoach/data/logs/' + logfile + ".BIN")
# # pilot north is 16 degrees East of North
# heading = np.radians(16)
# # heading = np.radians(106)
# pilot_box = GPSPosition(39.842288, -105.212928)

# # start = 275
# # end = 286
# # start = 60
# # end = 82
# start = 82
# end = 142

print("Pilot North (CW from North) is {:5.1f}".format(np.degrees(heading)))
print("pilot position: ({:f}, {:f})".format(pilot_box.latitude, pilot_box.longitude))

box = Box('heading', pilot_box, heading)
flightline = FlightLine.from_box(box)
sec = Section.from_flight(flight, flightline)

subSec = sec.subset(start, end)

mingspd = 10
# TODO: lower pitch thresholds seem to be best for reducing errors in calculated maneuver roll
# this seems to indicate that the ground course computed in genManeuverRPY is not correct
pThresh = np.radians(30)
[roll, pitch, wca, wca_axis] = genManeuverRPY(subSec, mingspd, pThresh)

span = 1.85
scale = 5
duration = end - start
# draw models mdt seconds apart
mdt = 1

# use orthographic projection for rendering to canvas
fig = go.Figure(
        #boxfrustum() +
        boxfrustumEdges() +
        tiptrace(subSec, scale * span, roll, pitch, wca) +
        ribbon(scale * span * .9, subSec, roll) +
        meshes(obj.scale(scale), mdt, subSec, roll, pitch, wca),
        layout=go.Layout(
            margin=dict(autoexpand=True),
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
fig.update_layout(scene_camera=camera, title="log: {:s}, time range: {:5.1f}-{:5.1f}".format(
                logfile, start, end),
                hoverdistance=60)
fig.update_scenes(xaxis_showspikes=False, yaxis_showspikes=False, zaxis_showspikes=False)

# save interactive figure
from pathlib import Path
basepath = str(Path.home()) + "/temp/"
fname = "%s_%s-%s.html" % (logfile, start, end)
print("writing 3D plot: " + basepath + fname)
fig.write_html(basepath + fname)
fig.show()
