import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.brats_utils import get_global_brats_experiment_data, download_brats_file


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
                                        id='file-brats-exp',
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
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-brats-exp',
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
                    html.Div(
                        # foreach group, show a boxplot
                        children=[
                            dcc.Graph(
                                id='general-chart-brats-exp',
                                config={"displayModeBar": False},
                            ),
                            dcc.Graph(
                                id='specific-file-chart-brats-exp',
                                config={"displayModeBar": False},
                                style={'display': 'none'},
                            ),
                        ],
                        className='card-body',
                    )
                ],
                className='card',
            ),
            html.Div(
                html.Div(
                    children=[
                        html.H3("Visualize a file"),
                        # modal
                        dbc.Button(
                            "Open modal",
                            id="open-modal-brats-exp",
                            className="ml-auto",
                            color="primary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    html.H3("Visualize a file")
                                ),
                                dbc.ModalBody(
                                    [
                                        html.P(
                                            children=[
                                                html.Span(
                                                    "Files for patient ",
                                                    className="font-weight-bold",
                                                ),
                                                html.Span(
                                                    "UPENN-GBM-00019",
                                                    id="patient-id-brats-exp",
                                                ),
                                                html.Span(
                                                    " on file type ",
                                                    className="font-weight-bold",
                                                ),
                                                html.Span(
                                                    "T1",
                                                    id="file-type-brats-exp",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(

                                                ),
                                                html.Div(

                                                ),
                                            ],
                                            id='possible-files-brats-exp',
                                            className='card',
                                            style={'flexDirection': 'row'},
                                        ),
                                    ],
                                ),
                                dbc.ModalFooter(
                                    [
                                        dbc.Button(
                                            "Close", id="close-modal-brats-exp", className="ml-auto"
                                        ),
                                        dbc.Button(
                                            html.A(
                                                "Compare",
                                                id="compare-files-brats-exp",
                                                className="ml-auto",
                                                href="/compare_nii_11",
                                                style={'color': 'white', 'text-decoration': 'none'},
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                            id="modal-brats-exp",
                            size="xl",
                        ),
                    ],
                    className='card-body',
                ),
                className='card',
                id='modal-brats-exp-container',
                style={'display': 'none'},
            ),
        ]
    )


@callback(
    Output("modal-brats-exp", "is_open"),
    [Input("open-modal-brats-exp", "n_clicks"), Input("close-modal-brats-exp", "n_clicks")],
)
def toggle_modal(n1, n2):
    if n1 or n2:
        return not False
    return False


@callback(
    Output('general-chart-brats-exp', 'figure'),
    Output('file-brats-exp', 'options'),
    Input('general-chart-brats-exp', 'figure'),
    Input('file-brats-exp', 'value'),
    Input('normalization-brats-exp', 'value'),
)
def update_chart(_, file, normalization):
    exec_id = int(request.referrer.split('?')[1].split('=')[1])

    if file == 'All':
        experiment_data, files = get_global_brats_experiment_data(exec_id)
    else:
        experiment_data, files = get_global_brats_experiment_data(exec_id, file=file)
    # Delete row beginning with T1CE
    experiment_data = experiment_data[~experiment_data['File'].str.contains('T1CE')]

    # put in first row where File contains raw, after rai, after SRI, after SRI_brain
    sorted_experiments = pd.DataFrame()
    # check each row of experiment_data
    for index, row in experiment_data.iterrows():
        # check if File contains raw
        if 'T1_raw.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data = experiment_data.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data.iterrows():
        # check if File contains rai
        if 'T1_rai.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data = experiment_data.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data.iterrows():
        # check if File contains rai
        if 'T1_rai_n4.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data = experiment_data.drop(index)
    # check each row of experiment_data
    for index, row in experiment_data.iterrows():
        # check if File contains SRI
        if 'T1_to_SRI.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data = experiment_data.drop(index)
    for index, row in experiment_data.iterrows():
        # check if File contains SRI
        if 'T1_to_SRI_brain.nii.gz' in row['File']:
            sorted_experiments = sorted_experiments.append(row)
            experiment_data = experiment_data.drop(index)

    files = [file for file in files]
    files.insert(0, 'All')

    figure = px.box(sorted_experiments, x="File", y="Sigdig_mean",
                    title="Significant digits mean per file")
    figure.update_layout(
        xaxis_title="Patient",
        yaxis_title="Significant digits mean",
        legend_title="Patient",
    )
    return figure, [{'label': file, 'value': file} for file in files]


# callback when clicking on a boxplot
@callback(
    Output('specific-file-chart-brats-exp', 'figure'),
    Output('possible-files-brats-exp', 'children'),
    Output('file-type-brats-exp', 'children'),
    Output('modal-brats-exp-container', 'style'),
    Output('specific-file-chart-brats-exp', 'style'),
    Input('general-chart-brats-exp', 'clickData'),
    prevent_initial_call=True,
)
def update_chart(click_data):
    if click_data is None:
        return {}
    else:
        file = click_data['points'][0]['x']
        exec_id = int(request.referrer.split('?')[1].split('=')[1])
        experiment_data, files = get_global_brats_experiment_data(exec_id)
        experiment_data = experiment_data[experiment_data['File'] == file]
        experiment_data = experiment_data.sort_values(by=['Execution'])
        # scatter where index is used as x and y is the significant digits mean
        figure = px.box(experiment_data, x=experiment_data["Execution"], y="Sigdig_mean",
                        title="Significant digits mean for file " + file,
                        hover_data=['Patient_id'])
        figure.update_layout(
            xaxis_title="Execution",
            yaxis_title="Significant digits",
            legend_title="Patient",
        )

        # possible_files is juste file_1, file_2, file_3, ...
        possible_files = [
            html.Div(
                children=[
                    html.H5("File 1"),
                    dcc.RadioItems(
                        id="file-1-brats-exp",
                        options=[
                            {'label': "File " + str(i), 'value': i + "/-/" + str(file)}
                            for i in experiment_data['Execution']
                        ],
                    ),
                ],
                className='card-body',
            ),
            html.Div(
                children=[
                    html.H5("File 2"),
                    dcc.RadioItems(
                        id="file-2-brats-exp",
                        options=[
                            {'label': "File " + str(i), 'value': i + "/-/" + str(file)}
                            for i in experiment_data['Execution']
                        ],
                    ),
                ],
                className='card-body',
            ),
        ]

        return figure, possible_files, file, {'display': 'block'}, {'display': 'block'}


@callback(
    Output('compare-files-brats-exp', 'href'),
    Input('file-1-brats-exp', 'value'),
    Input('file-2-brats-exp', 'value'),
    prevent_initial_call=True,
)
def update_compare_link(file_1, file_2):
    if file_1 is None or file_2 is None:
        return ""
    execution_number_1 = file_1.split('/-/')[0]
    execution_number_2 = file_2.split('/-/')[0]
    file = file_1.split('/-/')[1]
    patient_id = file_1.split('/-/')[2]
    experiment_id = int(request.referrer.split('?')[1].split('=')[1])
    md5_1 = download_brats_file(execution_number_1, file, patient_id, experiment_id)
    md5_2 = download_brats_file(execution_number_2, file, patient_id, experiment_id)
    return "/compare-nii-11?id1=" + md5_1 + "&id2=" + md5_2
