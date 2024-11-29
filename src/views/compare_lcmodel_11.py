"""
Compare two quest2 files of cquest
"""
import pandas as pd
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.cquest_utils import read_cquest_file, normalize, preprocess_cquest_data_compare, read_lcmodel_file, \
    preprocess_lcmodel_data_compare
from models.reproduce import parse_url


def layout():
    """Return the layout for the compare quest2 files page."""
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare quest2 files'),
            dbc.Input(id='data-id1', type='hidden', value=''),
            dbc.Input(id='data-id2', type='hidden', value=''),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-compare-11-lcmodel',
                                        options=[
                                            {'label': 'No', 'value': False},
                                            {'label': 'Yes', 'value': True},
                                        ],
                                        value=False,
                                        labelStyle={'display': 'block'},
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
                    dcc.Graph(
                        id='11-chart-compare-lcmodel',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
        ]
    )


@callback(
    Output('11-chart-compare-lcmodel', 'figure'),
    Input('url', 'pathname'),
    Input('normalization-compare-11-lcmodel', 'value'),
)
def bind_charts(_, normalization):
    """Bind the charts to the data"""
    id1, id2 = parse_url(request.referrer)
    data1 = read_lcmodel_file(id1)
    data2 = read_lcmodel_file(id2)
    # delete metabolites water1, water2, water3
    data1, data2 = preprocess_lcmodel_data_compare(data1, data2)

    data = pd.concat([data1, data2])

    if normalization:
        normalize(data)

    fig1 = px.scatter(
        x=data['Metabolite'],
        y=data['Rate_Raw'],
        title='Comparison of metabolites',
        labels={
            'x': 'Metabolite',
            'y': 'Rate_Raw',
            'color': 'File',
        },
        color=data['File'],
    )
    return fig1
