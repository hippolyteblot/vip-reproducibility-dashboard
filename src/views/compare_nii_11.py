import numpy as np
from dash import html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.brats_utils import get_processed_data_from_niftis, build_difference_image, build_difference_image_ssim, \
    compute_psnr, compute_psnr_foreach_slice
from models.reproduce import parse_url


def layout():
    """Layout of the page"""
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
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Color scale'),
                                    dcc.RadioItems(
                                        id='colorscale-nii-11',
                                        options=[
                                            {'label': 'Based on the maximum from source images', 'value': 'abs'},
                                            {'label': 'Based on the maximum from the differences', 'value': 'relative'},
                                        ],
                                        value='abs',
                                        labelStyle={'display': 'block'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
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
            html.Div(
                children=[
                    html.H3('Chart description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-chart-nii',
                    ),
                ],
            ),

            html.H3('Slice selector'),
            dcc.Slider(
                min=0,
                max=1,
                value=0,
                id='slider-nii',
            ),
            html.Div(
                id='gradient-nii-11',
                style={
                    'width': '100%',
                    'height': '5px',
                    'background': 'linear-gradient(90deg, rgba(255,0,0, 0) 0%, rgba(255,0,0) 20%, rgba(255,0,0) 35%, '
                                  'rgba(255,0,0,0) 100%)',
                },
            ),
            html.Div(
                children=[
                    html.H5(
                        children=[
                            'SSIM: ',
                            html.Span(
                                id='ssim-value',
                            ),
                        ],
                    ),
                    html.H5('Parameters for SSIM'),
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
    Output('axes-nii', 'value'),
    Output('mode-nii-11', 'value'),
    Output('slider-nii', 'value'),
    Output('K1-slider', 'value'),
    Output('K2-slider', 'value'),
    Output('sigma-slider', 'value'),
    Output('colorscale-nii-11', 'value'),
    Input('url', 'value'),
)
def bind_parameters_from_url(url):
    """Bind the parameters from the url to the dropdowns and sliders"""
    # check if the url contains parameters
    if url != 'None' and request.referrer is not None and len(request.referrer.split('&')) > 2:
        # get the parameters
        id1, id2, axe, mode, slicer, k1, k2, sigma, colorscale = parse_url(request.referrer)
        return axe, mode, int(slicer), float(k1), float(k2), float(sigma), colorscale
    return 'z', 'pixel', 0, 0.001, 1, 1, 'abs'


@callback(
    Output('graph-nii1', 'figure', allow_duplicate=True),
    Output('graph-nii-cmp', 'figure', allow_duplicate=True),
    Output('graph-nii2', 'figure', allow_duplicate=True),
    Output('slider-nii', 'min', allow_duplicate=True),
    Output('slider-nii', 'max', allow_duplicate=True),
    Output('slider-nii', 'value', allow_duplicate=True),
    Output('parameters-ssim', 'style'),
    Output('ssim-value', 'children'),
    Output('psnr-slice-value', 'children'),
    Output('description-chart-nii', 'children'),
    Output('url', 'search', allow_duplicate=True),
    Input('slider-nii', 'value'),
    Input('axes-nii', 'value'),
    Input('mode-nii-11', 'value'),
    Input('K1-slider', 'value'),
    Input('K2-slider', 'value'),
    Input('sigma-slider', 'value'),
    Input('colorscale-nii-11', 'value'),
    prevent_initial_call=True,
)
def show_frames(slider_value, axe, mode, k1, k2, sigma, colorscale):
    id1, id2 = parse_url(request.referrer)[0:2]
    img_rgb1, img_rgb2, max_slider, vol1, vol2, maximum = get_processed_data_from_niftis(id1, id2, axe, slider_value)
    value = 0

    if mode == 'pixel':
        description = 'Pixel-wise difference between the two images'
        img_mask3 = build_difference_image(img_rgb1, img_rgb2)
        style = {'display': 'none'}
    else:
        description = 'SSIM difference between the two images'
        img_mask3, value = build_difference_image_ssim(img_rgb1, img_rgb2, k1, k2, sigma)
        style = {'display': 'block'}

    if colorscale == 'relative':
        maximum = img_mask3.max()
        if abs(img_mask3.min()) > maximum:
            maximum = abs(img_mask3.min())

    psnr = compute_psnr(vol1[slider_value, :, :], vol2[slider_value, :, :])
    if not isinstance(psnr, str):
        psnr = round(psnr, 4)

    if slider_value > max_slider:
        slider_value = max_slider
    return (
        px.imshow(img_rgb1, color_continuous_scale='gray'),
        # -1 = red, 0 = white, 1 = green
        px.imshow(img_mask3, color_continuous_scale='Picnic', range_color=[-maximum, maximum]),
        px.imshow(img_rgb2, color_continuous_scale='gray'),
        0,
        max_slider,
        slider_value,
        style,
        round(value, 4),
        psnr,
        description,
        f'?id1={id1}&id2={id2}&axe={axe}&mode={mode}&slice={slider_value}&K1={k1}&K2={k2}&sigma={sigma}&colorscale='
        f'{colorscale}',
    )


@callback(
    Output('gradient-nii-11', 'style'),
    Output('psnr-image-value', 'children'),
    Input('url', 'value'),
    State('axes-nii', 'value'),
    State('slider-nii', 'value'),
)
def update_one_time(_, axe, slicer):
    id1, id2 = parse_url(request.referrer)[0:2]
    img_rgb1, img_rgb2, max_slider, vol1, vol2, maximum = get_processed_data_from_niftis(id1, id2, axe, slicer)
    psnr_list = compute_psnr_foreach_slice(vol1, vol2, axe)
    full_psnr = compute_psnr(vol1, vol2)
    if not isinstance(full_psnr, str):
        full_psnr = round(full_psnr, 4)
    return (
        {'background': build_gradient(psnr_list), 'height': '5px', 'margin-left': '25px', 'margin-right': '25px'},
        full_psnr,
    )


def build_gradient(psnr_values):
    minimum = min(psnr_values)
    # for each psnr value, add a color to the gradient
    gradient = 'linear-gradient(to right, '
    for i in range(psnr_values.size):
        if psnr_values[i] == np.inf:
            value = 0
        else:
            value = 1 - ((psnr_values[i] - (minimum * 0.8)) * 0.05)
        gradient += f'rgba(255, 0, 0, {value}) '
        if i != psnr_values.size - 1:
            gradient += ', '
    gradient += ')'
    return gradient
