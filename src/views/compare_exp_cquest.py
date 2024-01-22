import pandas as pd
from dash import html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.cquest_utils import get_cquest_experiment_data, normalize
from models.reproduce import get_experiment_name, parse_url


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2(
                children=[
                    'Compare experiments : ',
                    html.Span(id='experiment1-name-compare', style={'color': 'blue'}),
                    ' and ',
                    html.Span(id='experiment2-name-compare', style={'color': 'blue'}),
                ]
            ),

            # Parameter menu
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Metabolite'),
                                    dcc.Dropdown(
                                        id='metabolite-name-bland-altman',
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
                                        id='signal-selected-bland-altman',
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
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-repro-bland-altman',
                                        options=[
                                            {'label': ' No', 'value': 'No'},
                                            {'label': ' Yes', 'value': 'Yes'},
                                        ],
                                        value='No',
                                        labelStyle={'display': 'block'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Graph type'),
                                    dcc.RadioItems(
                                        id='graph-type-repro-bland-altman',
                                        options=[
                                            {'label': ' General', 'value': 'general'},
                                            {'label': ' Bland-Altman', 'value': 'bland-altman'},
                                        ],
                                        value='general',
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
                    html.Div(
                        # foreach group, show a boxplot
                        children=[
                            dcc.Graph(
                                id='exp-chart-bland-altman',
                                config={"displayModeBar": False},
                            ),

                        ],
                        className='card-body',
                    )
                ],
                className='card',
            ),
            html.Div(
                children=[
                    html.H3('Chart description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-compare-exp-cquest',
                    ),
                ],
            ),
            dcc.Input(id='trigger', value=0, type='hidden'),
            dcc.Input(id='trigger2', value=0, type='hidden'),
        ]
    )


@callback(
    Output('metabolite-name-bland-altman', 'value'),
    Output('signal-selected-bland-altman', 'value'),
    Output('normalization-repro-bland-altman', 'value'),
    Output('graph-type-repro-bland-altman', 'value'),
    Input('url', 'value'),
)
def bind_parameters_from_url(execution_id):
    # check if the url contains parameters
    if execution_id != 'None' and request.referrer is not None and len(request.referrer.split('&')) > 2:
        _, _, metabolite_name, signal_selected, normalization, graph_type = parse_url(request.referrer)
        if not normalization:
            normalization = 'No'

        return metabolite_name, signal_selected, normalization, graph_type
    return 'PCh', 'All', False, 'bland-altman'


def generate_url(exp1, exp2, metabolite_name, signal_selected, graph_type, normalization):
    url = "?exp1=" + str(exp1) + "&exp2=" + str(exp2) + "&metabolite_name=" + str(metabolite_name) + \
          "&signal_selected=" + str(signal_selected) + "&normalization=" + str(normalization) + \
          "&graph_type=" + str(graph_type)
    return url


@callback(
    Output('metabolite-name-bland-altman', 'options'),
    Output('metabolite-name-bland-altman', 'value', allow_duplicate=True),
    Output('signal-selected-bland-altman', 'options'),
    Output('signal-selected-bland-altman', 'value', allow_duplicate=True),
    Output('experiment1-name-compare', 'children'),
    Output('experiment2-name-compare', 'children'),
    Output('url', 'search', allow_duplicate=True),
    Output('trigger', 'value'),
    Input('graph-type-repro-bland-altman', 'value'),
    Input('metabolite-name-bland-altman', 'value'),
    Input('signal-selected-bland-altman', 'value'),
    Input('normalization-repro-bland-altman', 'value'),
    prevent_initial_call=True,
)
def update_metabolite_name_bland_altman(graph, metabolite_name, signal_selected, normalization):
    if not normalization:
        normalization = 'No'
    exec_id_1, exec_id_2 = parse_url(request.referrer)[0:2]
    experiment_data_1 = get_cquest_experiment_data(exec_id_1)
    experiment_data_2 = get_cquest_experiment_data(exec_id_2)

    metabolites = experiment_data_1['Metabolite'].unique()
    metabolites = metabolites.tolist()
    metabolites = [metabolite for metabolite in metabolites if 'water' not in metabolite]

    if graph == 'general':
        # add 'All' to the list of metabolites
        metabolites.insert(0, 'All')

    if metabolite_name not in metabolites:
        metabolite_name = metabolites[0]

    signals = experiment_data_1['Signal'].unique()
    # keep only signals that are also in experiment_data_2
    signals = [signal for signal in signals if signal in experiment_data_2['Signal'].unique()]
    if signal_selected == 'All':
        list_workflows = [{'label': str(signal_id), 'value': signal_id} for signal_id in signals]
        list_workflows.insert(0, {'label': 'None', 'value': 'None'})
    else:
        workflows = experiment_data_1['Workflow'].unique()
        list_workflows = [{'label': str(workflow), 'value': workflow} for workflow in workflows]
        list_workflows.insert(0, {'label': 'None', 'value': 'None'})
    list_metabolites = [{'label': metabolite, 'value': metabolite} for metabolite in metabolites]
    list_metabolites.insert(0, {'label': 'All', 'value': 'All'})
    list_signals = [{'label': str(signal_id), 'value': signal_id} for signal_id in signals]
    list_signals.insert(0, {'label': 'All', 'value': 'All'})
    return [{'label': i, 'value': i} for i in metabolites], metabolite_name, list_signals, \
        signal_selected, get_experiment_name(exec_id_1), get_experiment_name(exec_id_2), \
        generate_url(exec_id_1, exec_id_2, metabolite_name, signal_selected, graph, normalization), 0


@callback(
    Output('exp-chart-bland-altman', 'figure'),
    Output('description-compare-exp-cquest', 'children'),
    Input('trigger', 'value'),
    State('metabolite-name-bland-altman', 'value'),
    State('signal-selected-bland-altman', 'value'),
    State('normalization-repro-bland-altman', 'value'),
    State('graph-type-repro-bland-altman', 'value'),
    prevent_initial_call=True,
)
def update_exp_chart_bland_altman(_, metabolite_name, signal_selected, normalization, graph_type):
    exec_id_1, exec_id_2 = parse_url(request.referrer)[0:2]
    experiment_data_1 = get_cquest_experiment_data(exec_id_1)
    experiment_data_2 = get_cquest_experiment_data(exec_id_2)

    # Add a column to experiment_data_1 and experiment_data_2 to identify the samples
    experiment_data_1['Experiment'] = get_experiment_name(exec_id_1)
    experiment_data_2['Experiment'] = get_experiment_name(exec_id_2)

    # keep only raws if the field 'Signal' is in both dataframes
    experiment_data_1 = experiment_data_1[experiment_data_1['Signal'].isin(experiment_data_2['Signal'])]
    experiment_data_2 = experiment_data_2[experiment_data_2['Signal'].isin(experiment_data_1['Signal'])]

    if metabolite_name != 'All':
        # Keep only the selected metabolite
        experiment_data_1 = experiment_data_1[experiment_data_1['Metabolite'] == metabolite_name]
        experiment_data_2 = experiment_data_2[experiment_data_2['Metabolite'] == metabolite_name]
    if graph_type == 'bland-altman':
        # Group by signal and metabolite by computing the mean
        experiment_data_1 = experiment_data_1.groupby(['Signal', 'Metabolite', 'Experiment']).mean(True).reset_index()
        experiment_data_2 = experiment_data_2.groupby(['Signal', 'Metabolite', 'Experiment']).mean(True).reset_index()

        bland_altman_data = pd.DataFrame(columns=['Mean', 'Difference', '% Difference', 'Sample'])

        # Sample is the row Signal
        for sample in experiment_data_1['Signal'].unique():
            mean_1 = experiment_data_1[experiment_data_1['Signal'] == sample]['Amplitude'].mean()
            mean_2 = experiment_data_2[experiment_data_2['Signal'] == sample]['Amplitude'].mean()

            diff = mean_1 - mean_2
            percent_diff = diff / ((mean_1 + mean_2) / 2)
            data_to_concat = [
                bland_altman_data,
                pd.DataFrame({
                    'Mean': (mean_1 + mean_2) / 2,
                    'Difference': diff,
                    '% Difference': percent_diff,
                    'Sample': sample
                }, index=[0])
            ]
            data_to_concat = [df.dropna(axis=1, how='all') for df in data_to_concat]
            bland_altman_data = pd.concat(data_to_concat, ignore_index=True)

        fig = px.scatter(
            bland_altman_data,
            x='Mean',
            y='Difference',
            hover_data=['% Difference', 'Sample'],
            title='Bland-Altman plot',
        )

        # Add the linear regression if the Difference column is not always 0
        if not bland_altman_data['Difference'].eq(0).all():
            fig.add_trace(
                px.scatter(
                    bland_altman_data,
                    x='Mean',
                    y='Difference',
                    trendline='ols',
                    color_discrete_sequence=['black'],
                ).data[1],
            )

        mean_diff = bland_altman_data['Difference'].mean()
        std_diff = bland_altman_data['Difference'].std()
        upper_bound = mean_diff + 1.96 * std_diff
        lower_bound = mean_diff - 1.96 * std_diff

        # Add the upper and lower bounds
        fig.add_trace(
            px.line(
                x=[bland_altman_data['Mean'].min(), bland_altman_data['Mean'].max()],
                y=[upper_bound, upper_bound],
                color_discrete_sequence=['red'],
            ).data[0],
        )
        fig.add_trace(
            px.line(
                x=[bland_altman_data['Mean'].min(), bland_altman_data['Mean'].max()],
                y=[lower_bound, lower_bound],
                color_discrete_sequence=['red'],
            ).data[0],
        )

        description = "Bland-Altman plot of the two experiments. First, the mean of each value " \
                      "(a metabolite for a signal) is computed for each workflow of an experiment. " \
                      "Then, the mean of the two experiments is computed. Finally, the difference between the two " \
                      "experiments is plotted against the mean of the two experiments. The red lines represent the " \
                      "95% confidence interval of the difference."

        return fig, description
    else:
        concat_data = pd.concat([experiment_data_1, experiment_data_2], ignore_index=True)

        graph_list = [px.box, px.scatter]
        # Delete rows where Metabolite contains 'water'
        concat_data = concat_data[~concat_data['Metabolite'].str.contains('water')]
        # keep only the wanted signal
        if signal_selected != 'All':
            concat_data = concat_data[concat_data['Signal'] == signal_selected]

        if signal_selected == 'All':
            # Keep one value per signal by taking the mean
            concat_data = concat_data.groupby(['Metabolite', 'Signal', 'Experiment']).mean(numeric_only=True).\
                reset_index()

        if metabolite_name != 'All':
            concat_data = concat_data[concat_data["Metabolite"] == metabolite_name]

        else:
            addon = ''
            if normalization == 'Yes':
                normalize(concat_data)
                addon = 'The metabolites are normalized by subtracting the mean and dividing by the standard deviation.'

            first_x_value = concat_data['Metabolite'].iloc[0]
            if len(concat_data[concat_data['Metabolite'] == first_x_value]) < 4:
                selected_graph = graph_list[1]
            else:
                selected_graph = graph_list[0]

            graph = selected_graph(
                x=concat_data['Metabolite'],
                y=concat_data['Amplitude'],
                title='Comparison of metabolites',
                labels={
                    'x': 'Metabolite',
                    'y': 'Amplitude',
                },
                color=concat_data['Experiment'],
                data_frame=concat_data,
                hover_data=['Signal']
            )
            description = "Boxplot of the amplitude of the metabolites for the two experiments. " \
                          "The amplitude is the area under the curve of the metabolite. " + addon
            return graph, description

        if signal_selected == 'None':
            first_x_value = concat_data['Workflow'].iloc[0]
            if len(concat_data[concat_data['Workflow'] == first_x_value]) < 4:
                selected_graph = graph_list[1]
            else:
                selected_graph = graph_list[0]
            graph = selected_graph(
                x=concat_data['Workflow'],
                y=concat_data['Amplitude'],
                title='Comparison of metabolite ' + metabolite_name,
                color=concat_data['Experiment'],
                data_frame=concat_data,
                hover_data=['Signal']
            )
            description = "Boxplot of the amplitude of the metabolite " + metabolite_name + " for the two " \
                          "experiments. The amplitude is the area under the curve of the metabolite."
            return graph, description
        else:
            first_x_value = concat_data['Signal'].iloc[0]
            if len(concat_data[concat_data['Signal'] == first_x_value]) < 4:
                selected_graph = graph_list[1]
            else:
                selected_graph = graph_list[0]
            signal_values = concat_data['Signal']
            amplitude_values = concat_data['Amplitude']
            graph = selected_graph(
                x=signal_values,
                y=amplitude_values,
                title='Comparison',
                color=concat_data['Experiment'],
                data_frame=concat_data,
                hover_data=['Signal']
            )
            description = "Boxplot of the amplitude of the metabolite " + metabolite_name + " for the two " \
                          "experiments for the signal " + signal_selected + ". The amplitude is the area under the " \
                          "curve of the metabolite."

            return graph, description
