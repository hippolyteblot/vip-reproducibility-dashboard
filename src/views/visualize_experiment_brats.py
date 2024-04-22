"""
Visualize an experiment brats page.
"""
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.brats_utils import get_global_brats_experiment_data, download_brats_file
from models.reproduce import parse_url, get_experiment_descriptions


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
                children=[
                    html.H3('Chart description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-chart-brats',
                    ),
                ],
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
            html.Div(
                children=[
                    html.H3('Experiment description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-exp-brats',
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
                        id='description-inputs-brats',
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
                        id='description-outputs-brats',
                    ),
                ],
            ),
        ]
    )


@callback(
    Output("modal-brats-exp", "is_open"),
    [Input("open-modal-brats-exp", "n_clicks"), Input("close-modal-brats-exp", "n_clicks")],
)
def toggle_modal(n1, n2):
    """Toggle the modal"""
    if n1 or n2:
        return not False
    return False


@callback(
    Output('general-chart-brats-exp', 'figure'),
    Output('file-brats-exp', 'options'),
    Output('description-chart-brats', 'children'),
    Output('description-exp-brats', 'children'),
    Output('description-inputs-brats', 'children'),
    Output('description-outputs-brats', 'children'),
    Input('general-chart-brats-exp', 'figure'),
    Input('file-brats-exp', 'value'),
)
def update_chart(_, file):
    """Update the chart for the experiment visualization"""
    exec_id = int(parse_url(request.referrer)[0])

    experiment_data = get_global_brats_experiment_data(exec_id)
    files = experiment_data['File'].unique()
    if file == 'All':
        description = 'Significant digits mean per step for each file. Significant digits are computed as with ' \
                      'https://raw.githubusercontent.com/gkpapers/2020AggregateMCA/master/code/utils.py. ' \
                      'The mean is computed for each step and each file.'
        title = 'Significant digits mean per step for each file'
    else:
        experiment_data = experiment_data[experiment_data['File'] == file]
        description = f'Significant digits mean per step for file {file}. Significant digits are computed with ' \
                      f'https://raw.githubusercontent.com/gkpapers/2020AggregateMCA/master/code/utils.py. ' \
                      f'The mean is computed for each step.'
        title = f'Significant digits mean per step for file {file}'

    files = list(files)
    files.insert(0, 'All')

    figure = px.box(experiment_data, x="File", y="Mean_sigdigits", color="File", facet_col="Image",
                    title=title,
                    category_orders={"Step": experiment_data['File'].unique().tolist(),
                                     "Image": experiment_data['Image'].unique().tolist()},
                    color_discrete_sequence=px.colors.qualitative.Plotly)
    figure.update_layout(
        yaxis_title="Significant digits mean",
    )
    exp_desc, in_desc, out_desc = get_experiment_descriptions(wf_id).values()
    return figure, [{'label': file, 'value': file} for file in files], description, exp_desc, in_desc, out_desc


@callback(
    Output('compare-files-brats-exp', 'href'),
    Input('file-1-brats-exp', 'value'),
    Input('file-2-brats-exp', 'value'),
    prevent_initial_call=True,
)
def update_compare_link(file_1, file_2):
    """Update the compare link"""
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
