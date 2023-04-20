from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.reproduce import get_parameters_for_spectro, get_prebuilt_data, get_execution_data_from_local, \
    get_data_from_girder, get_metadata_from_girder
from utils.settings import GVC

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, voxels, groups = get_parameters_for_spectro(get_prebuilt_data())


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
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
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Metadata'),
                                    html.Div(
                                        id='metadata',
                                        children=[
                                            html.P('No metadata available'),
                                        ],
                                        style={'display': 'flex', 'flexDirection': 'row', 'overflow': 'auto',
                                               'gap': '10px'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                ],
            ),
        ]
    )


@callback(
    Output('metadata', 'children'),
    Input('url', 'href'),
)
def update_metadata(href):
    page = href.split('/')[-1]
    if not page.startswith('repro-execution'):
        return html.P('No metadata available')
    exec_id = int(href.split('?')[1].split('=')[1])
    metadata_json, id_list = get_metadata_from_girder(exec_id)

    metadata_structure = [
        html.Div(
            [
                html.P('Session name : ' + metadata_json[i]['session_name']),
                html.P('Workflow id : ' + metadata_json[i]['workflow_id']),
                html.P('Workflow start : ' + metadata_json[i]['workflow_start']),
                html.P('Workflow status : ' + metadata_json[i]['workflow_status']),
                html.P(
                    children=[
                        'Folder link : ',
                        html.A(
                            'Girder',
                            href=GVC.url + '/#collection/' + GVC.source_folder + '/folder/' + id_list[i],
                            target='_blank',
                        ),
                    ]
                ),
            ],
            className='card-body',
        )
        for i in range(len(metadata_json))
    ]

    return metadata_structure


@callback(
    Output('exec-chart', 'figure'),
    Input('metabolite-name', 'value'),
)
def update_chart(metabolite):
    # Try to use flask.request.referrer to obtain query string inside callback and then parse_qs from urllib
    exec_id = int(request.referrer.split('?')[1].split('=')[1])
    exec_data = get_data_from_girder(exec_id, current_user.id)

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
