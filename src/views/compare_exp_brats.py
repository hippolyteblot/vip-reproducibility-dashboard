import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.brats_utils import get_global_brats_experiment_data


def layout():
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


def get_experiment_data(exec_id, file):
    experiment_data = get_global_brats_experiment_data(exec_id)
    files = experiment_data['File'].unique().tolist()
    if file != 'All':
        experiment_data = experiment_data[experiment_data['File'] == file]

    experiment_data = experiment_data[~experiment_data['File'].str.contains('T1CE')]

    return experiment_data, files


def sort_experiment_data(experiment_data1, experiment_data2):
    sorted_experiments = pd.DataFrame()
    files_to_check = ['_raw.nii.gz', '_rai.nii.gz', '_rai_n4.nii.gz', '_to_SRI.nii.gz', '_to_SRI_brain.nii.gz']

    dfs_to_concat = []

    for file_to_check in files_to_check:
        for index, row in experiment_data1.iterrows():
            if file_to_check in row['File']:
                dfs_to_concat.append(row)

        for index, row in experiment_data2.iterrows():
            if file_to_check in row['File']:
                dfs_to_concat.append(row)

    if dfs_to_concat:
        sorted_experiments = pd.concat(dfs_to_concat, axis=1).T

    sorted_experiments.reset_index(drop=True, inplace=True)

    return sorted_experiments


def create_box_plot(sorted_experiments, unique_file=False):
    if unique_file:
        title = f"Significant digits mean per step for file {sorted_experiments['File'].iloc[0]}"
    else:
        title = "Significant digits mean per step for each file"
    figure = px.box(sorted_experiments, x="File", y="Mean_sigdigits",
                    title=title, color='Experiment')
    figure.update_layout(
        xaxis_title="File",
        yaxis_title="Significant digits mean",
        legend_title="Patient",
    )

    return figure


@callback(
    Output('general-chart-brats-exp-compare', 'figure'),
    Output('file-brats-exp-compare', 'options'),
    Output('description-compare-exp-brats', 'children'),
    Input('general-chart-brats-exp-compare', 'figure'),
    Input('file-brats-exp-compare', 'value'),
)
def update_chart(_, file):
    exec_id1 = int(request.referrer.split('?')[1].split('=')[1].split('&')[0])
    exec_id2 = int(request.referrer.split('?')[1].split('=')[2])

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

