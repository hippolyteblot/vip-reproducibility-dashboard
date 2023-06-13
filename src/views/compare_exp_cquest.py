import pandas as pd
from dash import html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.cquest_utils import get_cquest_experiment_data
from models.reproduce import get_experiment_name


def layout():
    return html.Div(
        [
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
                                            {'label': ' No', 'value': False},
                                            {'label': ' Yes', 'value': True},
                                        ],
                                        value=False,
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
                                        value='bland-altman',
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
            )
        ]
    )


@callback(
    Output('metabolite-name-bland-altman', 'options'),
    Output('metabolite-name-bland-altman', 'value'),
    Output('signal-selected-bland-altman', 'options'),
    Output('signal-selected-bland-altman', 'value'),
    Output('experiment1-name-compare', 'children'),
    Output('experiment2-name-compare', 'children'),
    Input('graph-type-repro-bland-altman', 'value'),
    Input('metabolite-name-bland-altman', 'value'),
    Input('signal-selected-bland-altman', 'value'),
)
def update_metabolite_name_bland_altman(graph, metabolite_name, signal_selected):
    exec_id_1 = int(request.referrer.split('?')[1].split('=')[1].split('&')[0])
    exec_id_2 = int(request.referrer.split('?')[1].split('=')[2])
    experiment_data_1 = get_cquest_experiment_data(exec_id_1)

    metabolites = experiment_data_1['Metabolite'].unique()
    metabolites = metabolites.tolist()
    metabolites = [metabolite for metabolite in metabolites if 'water' not in metabolite]

    if graph == 'general':
        # add 'All' to the list of metabolites
        metabolites.insert(0, 'All')

    if metabolite_name not in metabolites:
        metabolite_name = metabolites[0]

    signals = experiment_data_1['Signal'].unique()
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
        signal_selected, get_experiment_name(exec_id_1), get_experiment_name(exec_id_2)


@callback(
    Output('exp-chart-bland-altman', 'figure'),
    Input('metabolite-name-bland-altman', 'value'),
    Input('signal-selected-bland-altman', 'value'),
    Input('normalization-repro-bland-altman', 'value'),
    Input('graph-type-repro-bland-altman', 'value'),
    prevent_initial_call=True,
)
def update_exp_chart_bland_altman(metabolite_name, signal_selected, normalization, graph_type):
    exec_id_1 = int(request.referrer.split('?')[1].split('=')[1].split('&')[0])
    exec_id_2 = int(request.referrer.split('?')[1].split('=')[2])
    experiment_data_1 = get_cquest_experiment_data(exec_id_1)
    experiment_data_2 = get_cquest_experiment_data(exec_id_2)
    # add a column to experiment_data_1 and experiment_data_2 to identify the sample
    experiment_data_1['Experiment'] = get_experiment_name(exec_id_1)
    experiment_data_2['Experiment'] = get_experiment_name(exec_id_2)
    if metabolite_name != 'All':
        # keep only the metabolite selected
        experiment_data_1 = experiment_data_1[experiment_data_1['Metabolite'] == metabolite_name]
        experiment_data_2 = experiment_data_2[experiment_data_2['Metabolite'] == metabolite_name]

    if graph_type == 'bland-altman':
        # group by signal and metabolite by computing the mean
        experiment_data_1 = experiment_data_1.groupby(['Signal', 'Metabolite', 'Experiment']).mean(True).reset_index()
        experiment_data_2 = experiment_data_2.groupby(['Signal', 'Metabolite', 'Experiment']).mean(True).reset_index()
        bland_altman_data = pd.DataFrame(columns=['Mean', 'Difference', '% Difference', 'Sample'])
        # sample is the row Signal
        for sample in experiment_data_1['Signal'].unique():
            bland_altman_data = pd.concat([
                bland_altman_data,
                pd.DataFrame({
                    'Mean': (experiment_data_1[experiment_data_1['Signal'] == sample]['Amplitude'].mean() +
                             experiment_data_2[experiment_data_2['Signal'] == sample]['Amplitude'].mean()) / 2,
                    'Difference': experiment_data_1[experiment_data_1['Signal'] == sample]['Amplitude'].mean() -
                                  experiment_data_2[experiment_data_2['Signal'] == sample]['Amplitude'].mean(),
                    '% Difference': (experiment_data_1[experiment_data_1['Signal'] == sample]['Amplitude'].mean() -
                                     experiment_data_2[experiment_data_2['Signal'] == sample]['Amplitude'].mean()) /
                                    ((experiment_data_1[experiment_data_1['Signal'] == sample]['Amplitude'].mean() +
                                      experiment_data_2[experiment_data_2['Signal'] == sample][
                                          'Amplitude'].mean()) / 2),
                    'Sample': sample,
                }, index=[0]),
            ], ignore_index=True)

        fig = px.scatter(
            bland_altman_data,
            x='Mean',
            y='Difference',
            hover_data=['% Difference', 'Sample'],
            title='Bland-Altman plot',
        )
        # add the linear regression

        fig.add_trace(
            px.scatter(
                bland_altman_data,
                x='Mean',
                y='Difference',
                trendline='ols',
                color_discrete_sequence=['black'],
            ).data[1],
        )

        upper_bound = bland_altman_data['Difference'].mean() + 1.96 * bland_altman_data['Difference'].std()
        lower_bound = bland_altman_data['Difference'].mean() - 1.96 * bland_altman_data['Difference'].std()

        # add the upper and lower bound
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

        return fig
    else:
        concat_data = pd.concat([experiment_data_1, experiment_data_2], ignore_index=True)
        # delete the row where Metabolite contains 'water'
        concat_data = concat_data[~concat_data['Metabolite'].str.contains('water')]

        if signal_selected != 'All':
            # keep one value by signal by taking the mean
            concat_data = concat_data.groupby(['Metabolite', 'Signal', 'Experiment']).mean().reset_index()

        # get only the data of the wanted metabolite
        if metabolite_name != 'All':
            concat_data = concat_data[concat_data["Metabolite"] == metabolite_name]
        else:
            if normalization:
                means = concat_data.groupby('Metabolite').mean()['Amplitude']
                stds = concat_data.groupby('Metabolite').std()['Amplitude']
                concat_data['Amplitude'] = concat_data.apply(lambda row: (row['Amplitude'] - means[row['Metabolite']]) /
                                                                         stds[row['Metabolite']], axis=1)

            graph = px.box(
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
            return graph

        if signal_selected == 'None':
            graph = px.box(
                x=concat_data['Workflow'],
                y=concat_data['Amplitude'],
                title='Comparison of metabolite ' + metabolite_name,
                color=concat_data['Experiment'],
                data_frame=concat_data,
                hover_data=['Signal']
            )
            return graph
        else:
            signal_values = concat_data['Signal']
            amplitude_values = concat_data['Amplitude']
            graph = px.box(
                x=signal_values,
                y=amplitude_values,
                title='Comparison',
                color=concat_data['Experiment'],
                data_frame=concat_data,
                hover_data=['Signal']
            )

            return graph
