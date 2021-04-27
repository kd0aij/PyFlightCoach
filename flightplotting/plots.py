import plotly.graph_objects as go
from .model import OBJ
from geometry import Point, Coord, Points
import numpy as np
from typing import List, Union
from math import cos, sin, tan, radians


# distance from pilot box to runway centerline
# note that origin is on runway centerline
pbox = 15
# max distance from pilot box to aerobatic box
depth = 175
xlim = depth * tan(radians(60))
ylim = depth - pbox
zmin = 20

# maneuvering box: 60 degrees horizontal and vertical from pilot box
def boxtrace():
    return [go.Mesh3d(
        #      0     1     2      3     4     5      6
        x=[    0, xlim,    0, -xlim, xlim,    0, -xlim],
        y=[-pbox, ylim, ylim,  ylim, ylim, ylim,  ylim],
        z=[    0,    0,    0,     0, xlim, xlim,  xlim],
        i=[0, 0, 0, 0, 0],
        j=[1, 2, 1, 3, 4],
        k=[2, 3, 4, 6, 6],
        opacity=0.4
    )]

# centerline of maneuvering box at depth
def boxplane():
    return [go.Mesh3d(
        #     0      1      2     3
        x=[xlim, -xlim, -xlim, xlim],
        y=[ylim,  ylim,  ylim, ylim],
        z=[zmin,  zmin,  xlim, xlim],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        opacity=0.4
    )]

# maneuvering box over depth range
mindepth = 125
xlim2 = mindepth * tan(radians(60))
ylim2 = mindepth - pbox
def boxfrustum():
    return [go.Mesh3d(
        #     0      1      2     3      4       5       6      7
        x=[xlim, -xlim, -xlim, xlim, xlim2, -xlim2, -xlim2, xlim2],
        y=[ylim,  ylim,  ylim, ylim, ylim2,  ylim2,  ylim2, ylim2],
        z=[zmin,  zmin,  xlim, xlim,  zmin,   zmin,  xlim2, xlim2],
        # i=[0, 0, 4, 4, 2, 7, 1, 6, 7, 0],
        # j=[1, 2, 5, 6, 3, 6, 2, 5, 3, 4],
        # k=[2, 3, 6, 7, 7, 2, 6, 1, 0, 7],
        i=[2, 7, 1, 6, 7, 0],
        j=[3, 6, 2, 5, 3, 4],
        k=[7, 2, 6, 1, 0, 7],
        opacity=0.4
    )]

def meshes(obj, npoints, seq):
    start = seq.data.index[0]
    end = seq.data.index[-1]
    return [
        obj.transform(
            seq.get_state_from_time(
                start + (end-start) * i / npoints
            ).transform
        ).create_mesh(
            "{:.1f}".format(start + (end-start) * i / npoints)
        ) for i in range(0, npoints+1)
    ]

# create a mesh for a "ribbon" plot
# 3 triangles for each pair of poses: current origin to each current/next wingtip
# and origin to next left/right wingtip
# TODO: add colors indicating roll angle ranges
def ribbon(scale, seq):
    left  = Point(0, -scale/2, 0)
    right = Point(0,  scale/2, 0)

    # transform origin and wingtips to world frame
    curPose = seq.get_state_from_index(0).transform
    ctr = seq.get_state_from_index(0).pos
    curLeft = curPose.point(left)
    curRight = curPose.point(right)

    # init vertex and face lists
    x = [ctr.x, curLeft.x, curRight.x]
    y = [ctr.y, curLeft.y, curRight.y]
    z = [ctr.z, curLeft.z, curRight.z]
    faces = []

    ctrIndex = 0
    for i in range(1, seq.data.shape[0]):
        # transform origin and wingtips to world frame
        nextPose = seq.get_state_from_index(i).transform
        nextctr = seq.get_state_from_index(i).pos
        nextLeft = nextPose.point(left)
        nextRight = nextPose.point(right)

        # update vertex and face lists
        x.extend([nextctr.x, nextLeft.x, nextRight.x])
        y.extend([nextctr.y, nextLeft.y, nextRight.y])
        z.extend([nextctr.z, nextLeft.z, nextRight.z])

        # clockwise winding direction
        faces.append([ctrIndex, ctrIndex+1, ctrIndex+4])
        faces.append([ctrIndex, ctrIndex+5, ctrIndex+2])
        faces.append([ctrIndex, ctrIndex+4, ctrIndex+5])
        ctrIndex += 3;

    I, J, K = np.array(faces).T
    return [go.Mesh3d(
        x=x, y=y, z=z, i=I, j=J, k=K,
        name='',
        showscale=False,
        hoverinfo="name"
    )]  # vertexcolor=points[:, 3:], #the color codes must be triplets of floats  in [0,1]!!

def trace3d(datax, datay, dataz, colour='black', width=2, text=None):
    return go.Scatter3d(
        x=datax,
        y=datay,
        z=dataz,
        line=dict(color=colour, width=width, showscale=True),
        mode='lines',
        text=text,
        hoverinfo="text"
    )


def trace(seq):
    return trace3d(
        *seq.pos.to_numpy().T,
        colour="black",
        text=["{:.1f}".format(val) for val in seq.data.index]
    )


def tiptrace(seq, span):
    text = ["{:.1f}".format(val) for val in seq.data.index]

    def make_offset_trace(pos, colour, text):
        return trace3d(
            *seq.body_to_world(pos).data.T,
            colour=colour,
            text=text
        )

    return [
        make_offset_trace(Point(0, span/2, 0), "blue", text),
        make_offset_trace(Point(0, -span/2, 0), "red", text)
    ]


def create_3d_plot(traces):
    return go.Figure(
        traces,
        layout=go.Layout(
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(aspectmode='data')
        ))

def _axistrace(cid):
    return trace3d(*cid.get_plot_df(20).to_numpy().T)

def axestrace(cids: Union[Coord, List[Coord]]):
    if isinstance(cids, List):
        return [_axistrace(cid) for cid in cids]
    elif isinstance(cids, Coord):
        return _axistrace(cids)
