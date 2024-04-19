"""
Visualize an experiment page for cquest.
"""
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, dcc, State
from flask import request

from models.cquest_utils import (get_cquest_experiment_data, generate_box_plot, create_signal_group_column,
                                 create_workflow_group_column, create_dropdown_options,
                                 filter_and_get_unique_values, normalize, generate_url)
from models.reproduce import get_experiment_name, parse_url, get_experiment_descriptions


def layout():
    """Return the layout for the visualize experiment cquest page."""
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
                                            {'label': 'No', 'value': 'No'},
                                            {'label': 'Yes', 'value': 'Yes'},
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
            dbc.Input(id='execution-id', type='hidden', value='None'),
            html.Div(
                children=[
                    html.H3('Chart description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-chart-cquest',
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.H3('Experiment description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-exp-cquest',
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.H3('Inputs description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-inputs-cquest',
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.H3('Outputs description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-outputs-cquest',
                    ),
                ],
            ),
            html.Div(
                id='trigger-update',
                style={'display': 'none'},
            ),
        ]
    )


@callback(
    Output('metabolite-name', 'value'),
    Output('signal-selected', 'value'),
    Output('workflow-selected', 'value'),
    Output('normalization-repro-wf', 'value'),
    Input('url', 'value'),
)
def bind_parameters_from_url(execution_id):
    """Bind the parameters from the url to the dropdowns"""
    # check if the url contains parameters
    if execution_id != 'None' and request.referrer is not None and len(request.referrer.split('&')) > 1:
        # get the parameters
        _, metabolite_name, signal_selected, workflow_selected, normalization = parse_url(request.referrer)
        return metabolite_name, signal_selected, workflow_selected, normalization
    return 'All', 'All', 'None', 'No'


@callback(
    Output('metabolite-name', 'options'),
    Output('signal-selected', 'options'),
    Output('workflow-selected', 'options'),
    Output('metabolite-name', 'value', allow_duplicate=True),
    Output('signal-selected', 'value', allow_duplicate=True),
    Output('workflow-selected', 'value', allow_duplicate=True),
    Output('experiment-name', 'children'),
    Output('trigger-update', 'children'),
    Output('url', 'search', allow_duplicate=True),
    Output('description-exp-cquest', 'children'),
    Output('description-inputs-cquest', 'children'),
    Output('description-outputs-cquest', 'children'),
    Input('execution-id', 'value'),
    Input('metabolite-name', 'value'),
    Input('signal-selected', 'value'),
    Input('workflow-selected', 'value'),
    Input('normalization-repro-wf', 'value'),
    prevent_initial_call=True,
)
def update_dropdowns(_, metabolite_name, signal_selected, workflow_selected, normalization):
    """Update the dropdowns"""
    wf_id = int(parse_url(request.referrer)[0])
    wf_data = get_cquest_experiment_data(wf_id)

    metabolites, signals = filter_and_get_unique_values(wf_data)

    list_metabolites = create_dropdown_options(metabolites, 'All')
    list_signals = create_dropdown_options(signals, 'All')

    if signal_selected == 'All':
        list_workflows = create_dropdown_options(signals, 'All')
    else:
        workflows = wf_data['Workflow'].unique()
        list_workflows = create_dropdown_options(workflows, 'None')

    exp_desc, in_desc, out_desc = get_experiment_descriptions(wf_id).values()

    return (list_metabolites, list_signals, list_workflows, metabolite_name, signal_selected, workflow_selected,
            get_experiment_name(wf_id), 'update', generate_url(wf_id, metabolite_name, signal_selected,
                                                               workflow_selected, normalization),
            exp_desc, in_desc, out_desc)


@callback(
    Output('signal-selected', 'value', allow_duplicate=True),
    Input('exec-chart', 'clickData'),
    State('signal-selected', 'value'),
    prevent_initial_call=True,
)
def update_signal_dropdown(click_data, signal_selected):
    """Update the signal dropdown"""
    if click_data is None:
        return signal_selected
    return click_data['points'][0]['customdata'][0]


@callback(
    Output('exec-chart', 'figure'),
    Output('workflow-selected', 'options', allow_duplicate=True),
    Output('data-to-highlight-label', 'children'),
    Output('description-chart-cquest', 'children'),
    Input('trigger-update', 'children'),
    State('metabolite-name', 'value'),
    State('signal-selected', 'value'),
    State('workflow-selected', 'value'),
    State('normalization-repro-wf', 'value'),
    prevent_initial_call=True,
)
def update_chart(_, metabolite, signal, workflow, normalization):
    """Update the chart"""
    combination = [
        metabolite == 'All',
        signal == 'All',
        workflow == 'None',
    ]

    exp_id = int(parse_url(request.referrer)[0])
    exp_data = get_cquest_experiment_data(exp_id)

    # suppress metabolite that start with water
    exp_data = exp_data[~exp_data['Metabolite'].str.startswith('water')]

    # sort data to keep the same order
    exp_data = exp_data.sort_values(by=['Metabolite', 'Signal', 'Workflow'])

    if normalization == 'Yes':
        normalize(exp_data)

    if combination == [True, True, True]:  # Cas 1 : Display everything
        list_workflows = create_dropdown_options(exp_data['Signal'].unique(), 'All')
        figure = generate_box_plot(exp_data, 'Metabolite', 'Amplitude',
                                   'Comparison of metabolites')
        label = 'Signal to highlight'
        description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed "
                       "by cQUEST and their provenance is shown in the table below.")
    elif combination == [True, True, False]:  # Cas 2 : Display everything but highlight a signal
        list_workflows = create_dropdown_options(exp_data['Signal'].unique(), 'None')
        create_signal_group_column(exp_data, workflow)
        figure = generate_box_plot(exp_data, 'Metabolite', 'Amplitude',
                                   'Comparison of metabolites', 'Signal group')
        label = 'Signal to highlight'
        description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed "
                       "by cQUEST and their provenance is shown in the table below.")
    elif combination == [True, False, True]:  # Cas 3 : Filter to keep only the data of the selected signal
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Signal'] == signal]
        figure = generate_box_plot(exp_data, 'Metabolite', 'Amplitude',
                                   'Comparison of metabolites')
        label = 'Workflow to highlight'
        description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed "
                       "by cQUEST and their provenance is shown in the table below.")
    elif combination == [True, False, False]:  # Cas 4 : Filter to keep only the data of the signal and highlight a wf
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Signal'] == signal]
        create_workflow_group_column(exp_data, workflow)
        figure = generate_box_plot(exp_data, 'Metabolite', 'Amplitude',
                                   'Comparison of metabolites', 'Workflow group')
        label = 'Workflow to highlight'
        description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed "
                       "by cQUEST and their provenance is shown in the table below.")
    elif combination == [False, True, True]:  # Cas 5 : Filter to keep only the selected metabolite. Signals on abscissa
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Metabolite'] == metabolite]
        figure = generate_box_plot(exp_data, 'Signal', 'Amplitude',
                                   f'Comparison of metabolite {metabolite}')
        label = 'Workflow to highlight'
        description = (f"This chart shows the amplitude of the signal {signal} for each metabolite. Results are "
                       "computed by cQUEST and their provenance is shown in the table below.")
    elif combination == [False, True, False]:  # Cas 6 : Same as 5 but highlight a wf (not really useful)
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Metabolite'] == metabolite]
        create_workflow_group_column(exp_data, workflow)
        figure = generate_box_plot(exp_data, 'Signal', 'Amplitude',
                                   f'Comparison of metabolite {metabolite}', 'Workflow group')
        label = 'Workflow to highlight'
        description = (f"This chart shows the amplitude of the signal {signal} for each metabolite. Results are "
                       "computed by cQUEST and their provenance is shown in the table below.")
    elif combination == [False, False, True]:  # Cas 7 : Filter to keep only the selected metabolite and signal
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Metabolite'] == metabolite]
        exp_data = exp_data[exp_data['Signal'] == signal]
        figure = generate_box_plot(exp_data, 'Workflow', 'Amplitude',
                                   f'Comparison of metabolite {metabolite}')
        label = 'Workflow to highlight'
        description = (f"This chart shows the amplitude of the signal {signal} for each metabolite. Results are "
                       "computed by cQUEST and their provenance is shown in the table below.")
    elif combination == [False, False, False]:  # Cas 8 : Filter to keep only the metabolite and signal + highlight a wf
        list_workflows = create_dropdown_options(exp_data['Workflow'].unique(), 'None')
        exp_data = exp_data[exp_data['Metabolite'] == metabolite]
        exp_data = exp_data[exp_data['Signal'] == signal]
        create_workflow_group_column(exp_data, workflow)
        figure = generate_box_plot(exp_data, 'Workflow', 'Amplitude',
                                   f'Comparison of metabolite {metabolite}', 'Workflow group')
        label = 'Workflow to highlight'
        description = (f"This chart shows the amplitude of the signal {signal} for each metabolite. Results are "
                       "computed by cQUEST and their provenance is shown in the table below.")
    else: # Cas 9 : Display everything
        list_workflows = create_dropdown_options(exp_data['Signal'].unique(), 'All')
        figure = generate_box_plot(exp_data, 'Metabolite', 'Amplitude',
                                   'Comparison of metabolites')
        label = 'Signal to highlight'
        description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed "
                       "by cQUEST and their provenance is shown in the table below.")

    return figure, list_workflows, label, description
