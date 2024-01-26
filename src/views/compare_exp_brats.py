"""
Compare the results of two brats experiments
"""
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, dcc
from flask import request

from models.brats_utils import get_experiment_data, create_box_plot, sort_experiment_data
from models.reproduce import parse_url


def layout():
    """Return the layout for the visualize experiment brats page."""
    return html.Div(
        [
            html.H2('Visualize an experiment'),
            # Parameter menu
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('File'),
                                    dcc.Dropdown(
                                        id='file-brats-exp-compare',
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
                                id='general-chart-brats-exp-compare',
                                config={"displayModeBar": False},
                            ),
                            dcc.Graph(
                                id='specific-file-chart-brats-exp-compare',
                                config={"displayModeBar": False},
                                style={'display': 'none'},
                            ),
                        ],
                        className='card-body',
                    ),
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
                        id='description-compare-exp-brats',
                    ),
                ],
            ),
        ]
    )


@callback(
    Output('general-chart-brats-exp-compare', 'figure'),
    Output('file-brats-exp-compare', 'options'),
    Output('description-compare-exp-brats', 'children'),
    Input('general-chart-brats-exp-compare', 'figure'),
    Input('file-brats-exp-compare', 'value'),
)
def update_chart(_, file):
    """Update the chart with the given file"""
    exec_id1, exec_id2 = parse_url(request.referrer)

    experiment_data1, files = get_experiment_data(exec_id1, file)
    experiment_data2, _ = get_experiment_data(exec_id2, file)

    experiment_data1['Experiment'] = 'Experiment 1'
    experiment_data2['Experiment'] = 'Experiment 2'

    sorted_experiments = sort_experiment_data(experiment_data1, experiment_data2)

    figure = create_box_plot(sorted_experiments, file != 'All')

    description = 'This chart shows the mean of significant digits per file per patient. ' \
                  'The significant digits are calculated by the formula: ' \
                  'significant digits = -ln(|std/mean|). ' \
                  'The mean of significant digits is calculated by using a file per execution.'

    files.insert(0, 'All')

    return figure, [{'label': file, 'value': file} for file in files], description
