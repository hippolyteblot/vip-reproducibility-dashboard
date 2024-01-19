import imageio
import numpy as np
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.brats_utils import get_processed_data_from_niftis_folder
from models.reproduce import parse_url


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare multiple niftis'),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
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
                                        id='axes-nii-xy',
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Only display the differences mask'),
                                    dcc.RadioItems(
                                        options=[
                                            {'label': 'Yes', 'value': 'yes'},
                                            {'label': 'No', 'value': 'no'},
                                        ],
                                        value='no',
                                        id='only-differences-nii-xy',
                                    ),
                                ],
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
                            html.H4('Differences'),
                            dcc.Graph(
                                id="graph-nii-xy",
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
                id='slider-nii-xy',
            ),
        ]
    )


@callback(
    Output('slider-nii-xy', 'min'),
    Output('slider-nii-xy', 'max'),
    Output('slider-nii-xy', 'value'),
    Input('url', 'pathname'),
)
def bind_components(_):
    folder_id = parse_url(request.referrer)[0]
    _, size = get_processed_data_from_niftis_folder(folder_id, 0, "z", False)

    return (
        0,
        size,
        0,
    )


@callback(
    Output('graph-nii-xy', 'figure'),
    Output('slider-nii-xy', 'min', allow_duplicate=True),
    Output('slider-nii-xy', 'max', allow_duplicate=True),
    Output('slider-nii-xy', 'value', allow_duplicate=True),
    Input('slider-nii-xy', 'value'),
    Input('axes-nii-xy', 'value'),
    Input('only-differences-nii-xy', 'value'),
    prevent_initial_call=True,
)
def show_frames(slider_value, axe, only_differences):
    folder_id = parse_url(request.referrer)[0]
    diff_matrix, size = get_processed_data_from_niftis_folder(folder_id, slider_value, axe, only_differences == 'yes')

    if slider_value > size:
        slider_value = size
    return (
        px.imshow(diff_matrix),
        0,
        size,
        slider_value,
    )
