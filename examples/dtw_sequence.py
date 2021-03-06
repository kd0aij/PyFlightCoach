from flightanalysis import Section, Schedule, FlightLine

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flightplotting.plots import plotsec
from flightplotting.traces import elementtraces, manoeuvretraces, axis_rate_trace, boxtrace
from flightdata import Flight
from flightplotting.model import OBJ
from geometry import Transformation, Quaternion, Point
from io import open
from json import load

import numpy as np
import pandas as pd

obj = OBJ.from_obj_file('data/models/ColdDraftF3APlane.obj').transform(Transformation(
    Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
))


p21 = Schedule.from_json("FlightAnalysis/schedules/P21.json")
template = Section.from_schedule(p21, 170.0, "left")


flight = Flight.from_csv("data/logs/flight_csvs/00000136.csv")
flown = Section.from_flight(flight, FlightLine.from_covariance(flight)).subset(102, 490)  # 490


plotsec(template, obj, 7, 100, color='orange').show()


plotsec(flown, obj, 6.0).show()

fig = make_subplots(rows=2, cols=1)
for tr in axis_rate_trace(flown, True):
   fig.add_trace(tr,row=1, col=1)
for tr in axis_rate_trace(template, True):
   fig.add_trace(tr,row=2, col=1)
fig.show()


distance, aligned = Section.align(flown, template)
print(distance)

go.Figure(
   data=manoeuvretraces(aligned),
   layout=go.Layout(template="flight3d+judge_view")
   ).show()

fig = go.Figure(layout=go.Layout(template="flight3d"))
for manoeuvre in aligned.manoeuvre.unique():
   fig.add_traces(elementtraces(aligned.get_manoeuvre(manoeuvre)))
fig.show()