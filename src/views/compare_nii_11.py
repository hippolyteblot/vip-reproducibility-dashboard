import imageio
import numpy as np
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.brats_utils import get_processed_data_from_niftis, build_difference_image, build_difference_image_ssim, \
    compute_psnr


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
                            dbc.Col(
                                children=[
                                    html.H4('Mode'),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'Compare each pixel', 'value': 'pixel'},
                                            {'label': 'Use SSIM', 'value': 'ssim'},
                                        ],
                                        value='pixel',
                                        clearable=False,
                                        id='mode-nii-11',
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            )
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                ]
            ),
            html.P(
                children=[
                    'PSNR for the whole image: ',
                    html.Span(
                        id='psnr-image-value',
                    ),
                ],
            ),
            html.P(
                children=[
                    'PSNR for this slice: ',
                    html.Span(
                        id='psnr-slice-value',
                    ),
                ],
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
            html.H3('Slice selector'),
            dcc.Slider(
                min=0,
                max=1,
                value=0,
                id='slider-nii',
            ),
            html.Div(
                children=[
                    html.H4(
                        children=[
                            'SSIM: ',
                            html.Span(
                                id='ssim-value',
                            ),
                        ],
                    ),
                    html.H4('Parameters for SSIM'),
                    html.A(
                        'What is SSIM?',
                        href='https://en.wikipedia.org/wiki/Structural_similarity',
                        target='_blank',
                    ),
                    html.P("K1"),
                    dcc.Slider(0.001, 1,
                               value=0.001,
                               id='K1-slider'
                               ),
                    html.P("K2"),
                    dcc.Slider(0.005, 1.5,
                               value=1,
                               id='K2-slider'
                               ),
                    html.P("Sigma"),
                    dcc.Slider(0, 1,
                               value=1.0,
                               id='sigma-slider'
                               ),
                ],
                id='parameters-ssim',
                style={'display': 'none'},
            ),
        ]
    )


@callback(
    Output('slider-nii', 'min'),
    Output('slider-nii', 'max'),
    Output('slider-nii', 'value'),
    Input('url', 'pathname'),
)
def bind_components(_):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]

    # TODO : lot of data processing here, should be done in a better way
    _, _, size, _, _ = get_processed_data_from_niftis(id1, id2, 0, 'x')

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
    Output('parameters-ssim', 'style'),
    Output('ssim-value', 'children'),
    Output('psnr-image-value', 'children'),
    Output('psnr-slice-value', 'children'),
    Input('slider-nii', 'value'),
    Input('axes-nii', 'value'),
    Input('mode-nii-11', 'value'),
    Input('K1-slider', 'value'),
    Input('K2-slider', 'value'),
    Input('sigma-slider', 'value'),
    prevent_initial_call=True,
)
def show_frames(slider_value, axe, mode, k1, k2, sigma):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]

    img_rgb1, img_rgb2, max_slider, vol1, vol2 = get_processed_data_from_niftis(id1, id2, slider_value, axe)
    value = 0

    if mode == 'pixel':
        img_mask3 = build_difference_image(img_rgb1, img_rgb2)
        style = {'display': 'none'}
    else:
        img_mask3, value = build_difference_image_ssim(img_rgb1, img_rgb2, k1, k2, sigma)
        style = {'display': 'block'}

    if slider_value > max_slider:
        slider_value = max_slider
    return (
        px.imshow(img_rgb1, color_continuous_scale='gray'),
        px.imshow(img_mask3),
        px.imshow(img_rgb2, color_continuous_scale='gray'),
        0,
        max_slider,
        slider_value,
        style,
        value,
        compute_psnr(vol1, vol2),
        compute_psnr(vol1[slider_value, :, :], vol2[slider_value, :, :]),
    )
