from dash import html, callback, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.reproduce import get_prebuilt_data, get_parameters_for_spectro, get_global_brats_experiment_data, \
    download_brats_file

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, _, _ = get_parameters_for_spectro(data)


# Voxels values are converted to string to avoid Dash to use a gradient color scale


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
)
def update_chart(pathname, file):
    exec_id = int(request.referrer.split('?')[1].split('=')[1])

    if file == 'All':
        experiment_data, files = get_global_brats_experiment_data(exec_id)
    else:
        experiment_data, files = get_global_brats_experiment_data(exec_id, file=file)

    files = [file for file in files]
    files.insert(0, 'All')

    # keep only the patient_id UPENN-GBM-00019
    # experiment_data = experiment_data[experiment_data['Patient_id'] == 'UPENN-GBM-00019']

    # normalize sigdig_mean by File_type and Patient_id
    """for file_type in experiment_data['File_type'].unique():
        for patient in experiment_data['Patient_id'].unique():
            mean = \
                experiment_data[
                    (experiment_data['File_type'] == file_type) & (experiment_data['Patient_id'] == patient)][
                    'Sigdig_mean'].mean()
            experiment_data.loc[(experiment_data['File_type'] == file_type) & (
                    experiment_data['Patient_id'] == patient), 'Sigdig_mean'] = \
                experiment_data[
                    (experiment_data['File_type'] == file_type) & (experiment_data['Patient_id'] == patient)][
                    'Sigdig_mean'] / mean
    """
    figure = px.box(experiment_data, x="File_type", y="Sigdig_mean",
                    title="Significant digits mean per file")
    figure.update_layout(
        xaxis_title="Patient",
        yaxis_title="Normalized significant digits mean",
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
        file_type = click_data['points'][0]['x']
        exec_id = int(request.referrer.split('?')[1].split('=')[1])
        experiment_data, files = get_global_brats_experiment_data(exec_id)
        experiment_data = experiment_data[experiment_data['File_type'] == file_type]
        experiment_data = experiment_data.sort_values(by=['Execution'])
        # scatter where index is used as x and y is the significant digits mean
        figure = px.box(experiment_data, x=experiment_data["Execution"], y="Sigdig_mean",
                            title="Significant digits mean for file " + file_type,
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
                            {'label': "File " + str(i), 'value': i + "/-/" + str(file_type)}
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
                            {'label': "File " + str(i), 'value': i + "/-/" + str(file_type)}
                            for i in experiment_data['Execution']
                        ],
                    ),
                ],
                className='card-body',
            ),
        ]

        return figure, possible_files, file_type, {'display': 'block'}, {'display': 'block'}


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
    file_type = file_1.split('/-/')[1]
    patient_id = file_1.split('/-/')[2]
    experiment_id = int(request.referrer.split('?')[1].split('=')[1])
    md5_1 = download_brats_file(execution_number_1, file_type, patient_id, experiment_id)
    md5_2 = download_brats_file(execution_number_2, file_type, patient_id, experiment_id)
    return "/compare-nii-11?id1=" + md5_1 + "&id2=" + md5_2
