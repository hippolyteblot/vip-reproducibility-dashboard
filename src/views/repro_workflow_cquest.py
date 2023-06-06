import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, callback, Input, Output, dcc, State
from flask import request
from flask_login import current_user

from models.reproduce import get_parameters_for_spectro, get_prebuilt_data, get_wf_data, get_metadata_cquest, \
    get_experiment_data, get_experiment_name


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2(
                children=[
                    'Study an experiment : ',
                    html.Span(
                        id='experiment-name',
                        style={'color': 'blue'},
                    ),
                ],
            ),

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
                                    html.H4('Signal'),
                                    dcc.Dropdown(
                                        id='signal-selected',
                                        options=[
                                            {'label': 'None', 'value': 'None'}
                                        ],
                                        value="All",
                                        clearable=False,
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4(
                                        children='Workflow to highlight',
                                        id='data-to-highlight-label',
                                    ),
                                    dcc.Dropdown(
                                        id='workflow-selected',
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


@callback(
    Output('metabolite-name', 'options'),
    Output('signal-selected', 'options'),
    Output('workflow-selected', 'options'),
    Output('metabolite-name', 'value'),
    Output('signal-selected', 'value'),
    Output('workflow-selected', 'value'),
    Output('metadata', 'children'),
    Output('experiment-name', 'children'),
    Input('execution-id', 'value'),
    State('metabolite-name', 'value'),
    State('signal-selected', 'value'),
    State('workflow-selected', 'value'),
)
def update_dropdowns(_, metabolite_name, signal_selected, workflow_selected):
    wf_id = int(request.referrer.split('?')[1].split('=')[1])
    wf_data = get_experiment_data(wf_id)
    metabolites = wf_data['Metabolite'].unique()
    # delete water from metabolites
    metabolites = [metabolite for metabolite in metabolites if 'water' not in metabolite]
    signals = wf_data['Signal'].unique()
    if signal_selected == 'All':
        list_workflows = [{'label': str(signal_id), 'value': signal_id} for signal_id in signals]
        list_workflows.insert(0, {'label': 'None', 'value': 'None'})
    else:
        workflows = wf_data['Workflow'].unique()
        list_workflows = [{'label': str(workflow), 'value': workflow} for workflow in workflows]
        list_workflows.insert(0, {'label': 'None', 'value': 'None'})
    list_metabolites = [{'label': metabolite, 'value': metabolite} for metabolite in metabolites]
    list_metabolites.insert(0, {'label': 'All', 'value': 'All'})
    list_signals = [{'label': str(signal_id), 'value': signal_id} for signal_id in signals]
    list_signals.insert(0, {'label': 'All', 'value': 'All'})

    metadata = get_metadata_cquest(wf_id)
    metadata_structure = [
        dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th('Signal'),
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
                                html.Td(i),
                                html.Td(metadata[i]['input_name']),
                                html.Td(metadata[i]['output_name']),
                                html.Td(metadata[i]['count']),
                            ]
                        )
                        for i in range(len(metadata))
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
        )
    ]

    return list_metabolites, list_signals, list_workflows, metabolite_name, signal_selected, workflow_selected, \
        metadata_structure, get_experiment_name(wf_id)


@callback(
    Output('exec-chart', 'figure'),
    Output('workflow-selected', 'options', allow_duplicate=True),
    Output('data-to-highlight-label', 'children'),
    Input('metabolite-name', 'value'),
    Input('signal-selected', 'value'),
    Input('workflow-selected', 'value'),
    Input('normalization-repro-wf', 'value'),
    prevent_initial_call=True,
)
def update_chart(metabolite, signal, workflow, normalization):
    # Get the query string from the url and get the execution id
    wf_id = int(request.referrer.split('?')[1].split('=')[1])
    # exec_data = get_data_from_girder(wf_id, user_id)
    wf_data = get_experiment_data(wf_id)
    # sort by metabolite
    wf_data = wf_data.sort_values(by=['Metabolite'])

    wf_data = wf_data[~wf_data['Metabolite'].str.contains('water')]

    if signal != 'All':
        # Keep only the wanted signal
        wf_data = wf_data[wf_data['Signal'] == signal]
        wf_children = wf_data['Workflow'].unique()
        label = 'Workflow to highlight'
    else:
        wf_children = wf_data['Signal'].unique()
        label = 'Signal to highlight'
        if workflow == 'None':
            # keep one value by signal by taking the mean
            wf_data = wf_data.groupby(['Metabolite', 'Signal']).mean().reset_index()

    list_workflows = [{'label': str(wf_id), 'value': wf_id} for wf_id in wf_children]

    # get only the data of the wanted metabolite
    if metabolite != 'All':
        exec_data = wf_data[wf_data["Metabolite"] == metabolite]
    else:
        if normalization:
            means = wf_data.groupby('Metabolite').mean()['Amplitude']
            stds = wf_data.groupby('Metabolite').std()['Amplitude']
            wf_data['Amplitude'] = wf_data.apply(lambda row: (row['Amplitude'] - means[row['Metabolite']]) /
                                                             stds[row['Metabolite']], axis=1)
        if workflow != 'None' and signal != 'All':
            wf_data['Workflow group'] = wf_data['Workflow'].apply(
                lambda x: str(workflow) if x == workflow else 'Other')
            graph = px.box(
                x=wf_data['Metabolite'],
                y=wf_data['Amplitude'],
                title='Comparison of metabolites',
                labels={
                    'x': 'Metabolite',
                    'y': 'Amplitude',
                },
                color=wf_data['Workflow group'],
                data_frame=wf_data,
                hover_data=['Signal']
            )
            return graph, list_workflows, label

        if workflow != 'None' and signal == 'All':
            # Create a new column with "selected signal" and "other"
            wf_data['Signal group'] = wf_data['Signal'].apply(
                lambda x: workflow if x == workflow else 'Other')
            graph = px.box(
                x=wf_data['Metabolite'],
                y=wf_data['Amplitude'],
                title='Comparison of metabolites',
                labels={
                    'x': 'Metabolite',
                    'y': 'Amplitude',
                },
                color=wf_data['Signal group'],
                data_frame=wf_data,
                hover_data=['Signal']
            )
            return graph, list_workflows, label
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
                hover_data=['Signal']
            )
            return graph, list_workflows, label

    if signal == 'None':
        graph = px.box(
            x=exec_data['Workflow'],
            y=exec_data['Amplitude'],
            title='Comparison of metabolite ' + metabolite,
            labels={
                'x': 'Workflow',
                'y': 'Amplitude',
            },
            data_frame=exec_data,
            hover_data=['Signal']
        )
        return graph, list_workflows, label
    else:
        graph = px.box(
            x=exec_data['Signal'],
            y=exec_data['Amplitude'],
            title='Comparison of metabolite ' + metabolite,
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
            },
            # color=exec_data['Highlight'],
            data_frame=exec_data,
            hover_data=['Signal']
        )

        return graph, list_workflows, label


# when a point of the graphe is clicked, the callback is called to update the value of the dropdown "Signal"
@callback(
    Output('signal-selected', 'value', allow_duplicate=True),
    Input('exec-chart', 'clickData'),
    State('signal-selected', 'value'),
    prevent_initial_call=True,
)
def update_signal_dropdown(click_data, signal_selected):
    if click_data is None:
        return signal_selected
    else:
        return click_data['points'][0]['customdata'][0]
