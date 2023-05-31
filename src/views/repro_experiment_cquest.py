from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.reproduce import get_prebuilt_data, get_parameters_for_spectro, get_experiment_data

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, _, _ = get_parameters_for_spectro(data)
# Voxels values are converted to string to avoid Dash to use a gradient color scale


def layout():
    return html.Div(
        [
            html.H2('Reproduce an experiment'),
            # Parameter menu
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
                                    html.H4('Graph'),
                                    dcc.Dropdown(
                                        id='graph-type',
                                        options=[
                                            {'label': 'Box', 'value': 'box'},
                                            {'label': 'Violin', 'value': 'violin'},
                                            {'label': 'Scatter', 'value': 'scatter'},
                                        ],
                                        value='box',
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
                    html.Div(
                        # foreach group, show a boxplot
                        children=[
                            dcc.Graph(
                                id='exp-chart-group1',
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
    Output('exp-chart-group1', 'figure'),
    Input('metabolite-name', 'value'),
    Input('graph-type', 'value')
)
def update_chart(metabolite, graph_type):
    exec_id = int(request.referrer.split('?')[1].split('=')[1])
    experiment_data = get_experiment_data(exec_id)

    # get only the data of the metabolite
    if metabolite != 'All':
        df = experiment_data[experiment_data["Metabolite"] == metabolite]
    else:
        df = experiment_data

    if metabolite == 'All':

        selected_metabolites = df['Metabolite'].unique()
        # for data1 and data2, get the mean and the std foreach metabolite
        means = {}
        stds = {}
        for metabolite in selected_metabolites:
            means[metabolite] = df[df['Metabolite'] == metabolite]['Amplitude'].mean()
            stds[metabolite] = df[df['Metabolite'] == metabolite]['Amplitude'].std()

        # Foreach amplitude in each metabolite, normalize it by the mean and std of the metabolite
        for metabolite in selected_metabolites:
            mean = means[metabolite]
            std = stds[metabolite]
            df.loc[df['Metabolite'] == metabolite, 'Normalized'] = (df[df['Metabolite'] == metabolite]
                                                                    ['Amplitude'] - mean) / std

        graph = None
        if graph_type == 'box':
            graph = px.box(
                x=df['Metabolite'],
                y=df['Normalized'],
                color=df['Workflow'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Workflow',
                },
            )
        elif graph_type == 'violin':
            graph = px.violin(
                x=df['Metabolite'],
                y=df['Normalized'],
                color=df['Workflow'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Workflow',
                },
            )

        elif graph_type == 'scatter':
            graph = px.scatter(
                x=df['Metabolite'],
                y=df['Normalized'],
                color=df['Workflow'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Workflow',
                },
            )

        return graph

    graph = None
    if graph_type == 'box':
        graph = px.box(
            x=df['Iteration'],
            y=df['Amplitude'],
            color=df['Workflow'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Iteration',
                'y': 'Amplitude',
                'color': 'Workflow',
            },
        )

    elif graph_type == 'violin':
        graph = px.violin(
            x=df['Iteration'],
            y=df['Amplitude'],
            color=df['Workflow'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Iteration',
                'y': 'Amplitude',
                'color': 'Workflow',
            },
        )

    elif graph_type == 'scatter':
        graph = px.scatter(
            x=df['Iteration'],
            y=df['Amplitude'],
            color=df['Workflow'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Iteration',
                'y': 'Amplitude',
                'color': 'Workflow',
            },
        )

    return graph
