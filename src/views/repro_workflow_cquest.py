import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request
from flask_login import current_user

from models.reproduce import get_parameters_for_spectro, get_prebuilt_data, get_wf_data, get_metadata_cquest, get_experiment_data


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
                                            {'label': 'All', 'value': 'All'}
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
                                            {'label': 'None', 'value': 'None'}
                                        ],
                                        value="None",
                                        clearable=False,
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-repro-wf',
                                        options=[
                                            {'label': 'No', 'value': False},
                                            {'label': 'Yes', 'value': True},
                                        ],
                                        value=False,
                                        labelStyle={'display': 'block'},
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

@callback(
    Output('metabolite-name', 'options'),
    Output('signal-selected', 'options'),
    Output('metabolite-name', 'value'),
    Output('signal-selected', 'value'),
    Output('metadata', 'children'),
    Input('execution-id', 'value'),
)
def update_dropdowns(_):
    wf_id = int(request.referrer.split('?')[1].split('=')[1])
    wf_data = get_experiment_data(wf_id)
    metabolites = wf_data['Metabolite'].unique()
    signals = wf_data['Iteration'].unique()
    list_metabolites = [{'label': metabolite, 'value': metabolite} for metabolite in metabolites]
    list_metabolites.insert(0, {'label': 'All', 'value': 'All'})
    list_signals = [{'label': 'Iteration ' + str(signal_id), 'value': signal_id} for signal_id in signals]
    list_signals.insert(0, {'label': 'None', 'value': 'None'})

    metadata = get_metadata_cquest(wf_id)
    metadata_structure = [
        dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th('Input name'),
                            html.Th('Outputs name'),
                            html.Th('Outputs number'),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(output['input_name']),
                                html.Td(output['output_name']),
                                html.Td(output['count']),
                            ]
                        )
                        for output in metadata
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
        )
    ]

    return list_metabolites, list_signals, 'All', 'None', metadata_structure


@callback(
    Output('exec-chart', 'figure'),
    Input('metabolite-name', 'value'),
    Input('signal-selected', 'value'),
    Input('normalization-repro-wf', 'value'),
)
def update_chart(metabolite, signal_id, normalization):
    # Get the query string from the url and get the execution id
    wf_id = int(request.referrer.split('?')[1].split('=')[1])
    # exec_data = get_data_from_girder(wf_id, user_id)
    wf_data = get_experiment_data(wf_id)

    if signal_id != 'None':
        # add a new column to the dataframe with the index as name and other for other
        wf_data['Highlight'] = wf_data['Iteration'].apply(
            lambda x: 'Iteration ' + str(signal_id) if x == signal_id else 'Other')

    # get only the data of the wanted metabolite
    if metabolite != 'All':
        exec_data = wf_data[wf_data["Metabolite"] == metabolite]
    else:
        if normalization:
            means = wf_data.groupby('Metabolite').mean()['Amplitude']
            stds = wf_data.groupby('Metabolite').std()['Amplitude']
            wf_data['Amplitude'] = wf_data.apply(lambda row: (row['Amplitude'] - means[row['Metabolite']]) /
                                              stds[row['Metabolite']], axis=1)
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
                data_frame=wf_data,
                hover_data=['Iteration']
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
                data_frame=wf_data,
                hover_data=['Iteration']
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
            data_frame=exec_data,
            hover_data=['Iteration']
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
            data_frame=exec_data,
            hover_data=['Iteration']
        )

        return graph
