import imageio
import numpy as np
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.reproduce import read_file


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare quest2 files'),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('File to compare'),
                                    dcc.Dropdown(
                                        options=[
                                        ],
                                        value='All',
                                        clearable=False,
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Axes'),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'X', 'value': 'x'},
                                            {'label': 'Y', 'value': 'y'},
                                            {'label': 'Z', 'value': 'z'},
                                        ],
                                        value='z',
                                        clearable=False,
                                        id='axes-nii',
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                ]
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.H4('File 1'),
                            dcc.Graph(
                                id="graph-nii1",
                            ),
                        ],
                        style={'width': '100%'},
                    ),
                    html.Div(
                        children=[
                            html.H4('Difference'),
                            dcc.Graph(
                                id="graph-nii-cmp",
                            ),
                        ],
                        style={'width': '100%'},
                    ),
                    html.Div(
                        children=[
                            html.H4('File 2'),
                            dcc.Graph(
                                id="graph-nii2",
                            ),
                        ],
                        style={'width': '100%'},
                    ),
                ],
                style={
                    "display": "flex",
                },
            ),
            dcc.Slider(
                min=0,
                max=1,
                value=0,
                id='slider-nii',
            ),
        ]
    )


@callback(
    Output('slider-nii', 'min'),
    Output('slider-nii', 'max'),
    Output('slider-nii', 'value'),
    Input('url', 'pathname'),
)
def bind_components(pathname):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]

    _, _, size = get_processed_data_from_niftis(id1, id2, 0, 'x')


    return (
        0,
        size,
        0,
    )


@callback(
    Output('graph-nii1', 'figure', allow_duplicate=True),
    Output('graph-nii-cmp', 'figure', allow_duplicate=True),
    Output('graph-nii2', 'figure', allow_duplicate=True),
    Output('slider-nii', 'min', allow_duplicate=True),
    Output('slider-nii', 'max', allow_duplicate=True),
    Output('slider-nii', 'value', allow_duplicate=True),
    Input('slider-nii', 'value'),
    Input('axes-nii', 'value'),
    prevent_initial_call=True,
)
def show_frames(slider_value, axe):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]

    img_rgb1, img_rgb2, max_slider = get_processed_data_from_niftis(id1, id2, slider_value, axe)

    img_mask3 = build_difference_image(img_rgb1, img_rgb2)

    if slider_value > max_slider:
        slider_value = max_slider

    return (
        px.imshow(img_rgb1),
        px.imshow(img_mask3),
        px.imshow(img_rgb2),
        0,
        max_slider,
        slider_value,
    )


def get_processed_data_from_niftis(id1, id2, slider_value, axe):
    data1 = "src/tmp/user_compare/" + id1 + ".nii"
    data2 = "src/tmp/user_compare/" + id2 + ".nii"

    vol1 = imageio.volread(data1)
    vol2 = imageio.volread(data2)
    max_vol1 = np.max(vol1)
    max_vol2 = np.max(vol2)

    # build an image using the slider value
    if axe == 'z':
        img_mask1 = vol1[slider_value, :, :]
        img_mask2 = vol2[slider_value, 3:, 5:]
    elif axe == 'y':
        img_mask1 = vol1[:, slider_value, :]
        img_mask2 = vol2[4:, slider_value, 5:]
    else:
        img_mask1 = vol1[:, :, slider_value]
        img_mask2 = vol2[4:, 3:, slider_value]

    img_rgb1 = np.stack([img_mask1 / max_vol1, img_mask1 / max_vol1, img_mask1 / max_vol1], axis=-1)
    img_rgb2 = np.stack([img_mask2 / max_vol2, img_mask2 / max_vol2, img_mask2 / max_vol2], axis=-1)

    axe_index = 2
    if axe == 'y':
        axe_index = 1
    elif axe == 'z':
        axe_index = 0

    return img_rgb1, img_rgb2, vol1.shape[axe_index]


def build_difference_image(img_rgb1, img_rgb2):
    min_shape0 = min(img_rgb1.shape[0], img_rgb2.shape[0])
    min_shape1 = min(img_rgb1.shape[1], img_rgb2.shape[1])
    img_mask3 = np.zeros(img_rgb1.shape)
    for i in range(min_shape0):
        for j in range(min_shape1):
            if img_rgb1[i, j, 0] == img_rgb2[i, j, 0]:
                img_mask3[i, j] = img_rgb1[i, j]
            else:
                img_mask3[i, j] = [255, 0, 0]

    return img_mask3
