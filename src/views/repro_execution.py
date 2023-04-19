from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.reproduce import get_parameters_for_spectro, get_prebuilt_data, get_execution_data_from_local

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, voxels, groups = get_parameters_for_spectro(get_prebuilt_data())


def layout():
    return html.Div(
        [
            html.H2('Reproduce an execution'),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Metabolite'),
                                    dcc.Dropdown(
                                        id='metabolite-name',
                                        options=[
                                            {'label': metabolite.get('label'), 'value': metabolite.get('value')}
                                            for metabolite in metabolites
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
                        id='exec-chart',
                        config={"displayModeBar": False},
                    ),
                ],
                style={'flexDirection': 'row'},
            ),
            dbc.Input(id='execution-id', type='hidden', value=''),
        ]
    )


@callback(
    Output('exec-chart', 'figure'),
    Input('metabolite-name', 'value'),
)
def update_chart(metabolite):
    # Try to use flask.request.referrer to obtain query string inside callback and then parse_qs from urllib
    path = request.referrer.split('?')[1].split('=')[1]

    exec_data = get_execution_data_from_local(path)

    # get only the data of the metabolite
    if metabolite != 'All':
        exec_data = exec_data[exec_data["Metabolite"] == metabolite]

    if metabolite == 'All':
        graph = px.box(
            x=exec_data['Metabolite'],
            y=exec_data['Amplitude'],
            title='Comparison of metabolites',
            labels={
                'x': 'Metabolite',
                'y': 'Amplitude',
            },
        )

        return graph

    graph = px.scatter(
        x=exec_data['Signal'],
        y=exec_data['Amplitude'],
        title='Comparison of metabolite ' + metabolite,
        labels={
            'x': 'Signal',
            'y': 'Amplitude',
        },
    )

    return graph
