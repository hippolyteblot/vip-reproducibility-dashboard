from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.reproduce import read_user_file


def layout():
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
                                    html.H4('Metabolite'),
                                    dcc.Dropdown(
                                        id='metabolite-name-compare',
                                        options=[
                                        ],
                                        value='All',
                                        clearable=False,
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
                        id='11-chart-compare',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
        ]
    )


@callback(
    Output('11-chart-compare', 'figure'),
    Input('url', 'pathname'),
)
def bind_charts(pathname):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]
    data1 = read_user_file(id1)
    data2 = read_user_file(id2)
    data1['Amplitude'] = data1['Amplitude'].apply(lambda x: float(x))
    data2['Amplitude'] = data2['Amplitude'].apply(lambda x: float(x))
    data1['File'] = 'File 1'
    data2['File'] = 'File 2'

    data = data1.append(data2)

    fig1 = px.scatter(
        x=data['Metabolite'],
        y=data['Amplitude'],
        title='Comparison of metabolites',
        labels={
            'x': 'Metabolite',
            'y': 'Amplitude',
            'color': 'File',
        },
        color=data['File'],
    )
    return fig1
