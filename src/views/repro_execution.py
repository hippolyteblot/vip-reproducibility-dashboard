from dash import html, callback, Input, Output, dcc, dash_table
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
    # foreach metadata, add an url 'test.com' for now
    i = 0
    for metadata in metadata_json:
        metadata['url'] = GVC.url + '/#collection/' + GVC.source_folder + '/folder/' + str(id_list[i])
        i += 1

    metadata_structure = html.Div(
        children=[
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in metadata_json[0].keys()],
                data=metadata_json,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
        ],
        style={'padding': '10px', 'width': '100%'},
    )

    return metadata_structure


@callback(
    Output('exec-chart', 'figure'),
    Input('metabolite-name', 'value'),
)
def update_chart(metabolite):
    # Get the query string from the url and get the execution id
    exec_id = int(request.referrer.split('?')[1].split('=')[1])
    user_id = current_user.id if current_user.is_authenticated else None
    exec_data = get_data_from_girder(exec_id, user_id)

    # get only the data of the wanted metabolite
    if metabolite != 'All':
        exec_data = exec_data[exec_data["Metabolite"] == metabolite]
    else:
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
