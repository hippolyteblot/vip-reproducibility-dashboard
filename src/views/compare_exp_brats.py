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

    if file == 'All':
        experiment_data1, files = get_global_brats_experiment_data(exec_id1)
        experiment_data2, _ = get_global_brats_experiment_data(exec_id2)
    else:
        experiment_data1, files = get_global_brats_experiment_data(exec_id1, file=file)
        experiment_data2, _ = get_global_brats_experiment_data(exec_id2, file=file)
    # Delete row beginning with T1CE
    experiment_data1 = experiment_data1[~experiment_data1['File'].str.contains('T1CE')]
    experiment_data2 = experiment_data2[~experiment_data2['File'].str.contains('T1CE')]

    files = [file for file in files]
    files.insert(0, 'All')

    # concat both dataframes but add a column to know which one is which
    experiment_data1['Experiment'] = 'Experiment 1'
    experiment_data2['Experiment'] = 'Experiment 2'

    # put in first row where File contains raw, after rai, after SRI, after SRI_brain
    sorted_experiments = pd.DataFrame()
    # check each row of experiment_data
    for index, row in experiment_data1.iterrows():
        # check if File contains raw
        if '_raw.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data1 = experiment_data1.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data1.iterrows():
        # check if File contains rai
        if '_rai.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data1 = experiment_data1.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data1.iterrows():
        # check if File contains rai
        if '_rai_n4.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data1 = experiment_data1.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data1.iterrows():
        # check if File contains SRI
        if '_to_SRI.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data1 = experiment_data1.drop(index)
    for index, row in experiment_data1.iterrows():
        # check if File contains SRI
        if '_to_SRI_brain.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data1 = experiment_data1.drop(index)

    for index, row in experiment_data2.iterrows():
        # check if File contains raw
        if '_raw.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data2 = experiment_data2.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data2.iterrows():
        # check if File contains rai
        if '_rai.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data2 = experiment_data2.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data2.iterrows():
        # check if File contains rai
        if '_rai_n4.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data2 = experiment_data2.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data2.iterrows():
        # check if File contains SRI
        if '_to_SRI.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data2 = experiment_data2.drop(index)
    for index, row in experiment_data2.iterrows():
        # check if File contains SRI
        if '_to_SRI_brain.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data2 = experiment_data2.drop(index)

    figure = px.box(sorted_experiments, x="File", y="Mean_sigdigits",
                    title="Significant digits mean per file", color="Experiment")
    figure.update_layout(
        xaxis_title="Patient",
        yaxis_title="Significant digits mean",
        legend_title="Patient",
    )
    description = 'This chart shows the mean of significant digits per file per patient. ' \
                  'The significant digits are calculated by the formula: ' \
                  'significant digits = -ln(|std/mean|). ' \
                  'The mean of significant digits is calculated by using a file per execution.'
    return figure, [{'label': file, 'value': file} for file in files], description
