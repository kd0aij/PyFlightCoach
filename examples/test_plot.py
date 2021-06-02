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
from math import pi
from flightplotting.traces import tiptrace, meshes, ribbon, \
     boxfrustumEdges, genManeuverRPY, wrapPi
from flightplotting.model import OBJ
from geometry import Transformation, Point, Quaternion, GPSPosition
import plotly.graph_objects as go

obj = OBJ.from_obj_file('/home/markw/linux_git/kd0aij/PyFlightCoach/data/models/ColdDraftF3APlane.obj').transform(
    Transformation(
        Point(0.75, 0, 0),
        Quaternion.from_euler(Point(pi, 0, -pi/2))
    )
)

testNum = 1

# the heading in the box.json file must be a compass heading:
# direction pilot is facing in degrees CW from true North
if testNum == 0:
    # Thomas David's logs
    # FC_examples = '/mnt/c/Users/markw/GoogleDrive/blackbox_logs/FlightCoach/examples/logs/'
    # flight = Flight.from_log(FC_examples + logfile + '.BIN')
    # flight.to_csv('data/logs/flight_csvs/100.csv')
    pbox = 'TD_box'

    # vertical 8
    logfile = '100'
    start = 108
    end = 154

elif testNum == 1:
    pbox = 'TD_box'
    # stall turn
    logfile = '141'
    start = 221
    end = 242

elif testNum == 2:
    # AAM East Field: FlightLine.from_covariance heading is off by 180 degrees
    logfile = "P21_032521"
    # flight = Flight.from_log('/home/markw/linux_git/kd0aij/PyFlightCoach/data/logs/' + logfile + ".BIN")
    # flight.to_csv('data/logs/flight_csvs/M21_032521.csv')

    pbox = 'AAMeast_box'

    # v8 and stall turn
    start = 92
    end = 146

elif testNum == 3:
    logfile = "M21_032521"
    # pilot north is 16 degrees East of North
    pbox = 'AAMeast_box'

    # stall turn
    start = 268
    end = 288

flight = Flight.from_csv('data/logs/flight_csvs/'+ logfile + '.csv')
firstGPSpos = flight.origin()
print("firstGPS position:", firstGPSpos)

box = Box.from_json('examples/' + pbox + '.json')

print("Pilot North (CW from North): {:5.1f}".format(np.degrees(box.heading)))
print("pilot position: ", box.pilot_position)

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
