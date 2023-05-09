from dash import html, callback, Input, Output, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.reproduce import get_parameters_for_spectro, get_prebuilt_data, get_execution_data_from_local, \
    get_data_from_girder, get_metadata_from_girder, get_wf_data
from utils.settings import GVC

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, voxels, groups = get_parameters_for_spectro(get_prebuilt_data())

signals = data['Execution'].unique()
# sort
signals.sort()
# add the None option
signals = ["None"] + list(signals)


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
                            dbc.Col(
                                children=[
                                    html.H4('Iteration to highlight'),
                                    dcc.Dropdown(
                                        id='signal-selected',
                                        options=[
                                            {'label': 'Iteration ' + str(signal_id), 'value': signal_id}
                                            for signal_id in signals
                                        ],
                                        value="None",
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
                className='card',
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

"""
@callback(
    Output('metadata', 'children'),
    Input('url', 'href'),
)
def update_metadata(href):
    page = href.split('/')[-1]
    if not page.startswith('repro-workflow'):
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
"""

@callback(
    Output('exec-chart', 'figure'),
    Input('metabolite-name', 'value'),
    Input('signal-selected', 'value'),
)
def update_chart(metabolite, signal_id):
    # Get the query string from the url and get the execution id
    wf_id = int(request.referrer.split('?')[1].split('=')[1])
    user_id = current_user.id if current_user.is_authenticated else None
    #exec_data = get_data_from_girder(wf_id, user_id)
    wf_data = get_wf_data(wf_id)

    if signal_id != 'None':
        # add a new column to the dataframe with the index as name and other for other
        wf_data['Highlight'] = wf_data['Iteration'].apply(
            lambda x: 'Iteration ' + str(signal_id) if x == signal_id else 'Other')

    # get only the data of the wanted metabolite
    if metabolite != 'All':
        exec_data = wf_data[wf_data["Metabolite"] == metabolite]
    else:
        if signal_id != 'None':
            graph = px.scatter(
                x=wf_data['Metabolite'],
                y=wf_data['Amplitude'],
                title='Comparison of metabolites',
                labels={
                    'x': 'Metabolite',
                    'y': 'Amplitude',
                },
                color=wf_data['Highlight'],
            )
            return graph
        else:
            graph = px.box(
                x=wf_data['Metabolite'],
                y=wf_data['Amplitude'],
                title='Comparison of metabolites',
                labels={
                    'x': 'Metabolite',
                    'y': 'Amplitude',
                },
            )
            return graph

    if signal_id == 'None':
        graph = px.scatter(
            x=exec_data['Iteration'],
            y=exec_data['Amplitude'],
            title='Comparison of metabolite ' + metabolite,
            labels={
                'x': 'Iteration',
                'y': 'Amplitude',
            },
        )
        return graph
    else:
        graph = px.scatter(
            x=exec_data['Iteration'],
            y=exec_data['Amplitude'],
            title='Comparison of metabolite ' + metabolite,
            labels={
                'x': 'Iteration',
                'y': 'Amplitude',
            },
            color=exec_data['Highlight'],
        )

        return graph
