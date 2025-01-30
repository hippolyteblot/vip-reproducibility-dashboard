"""
View for the compare xy (many to many files) page for cquest.
"""
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.cquest_utils import (get_files_in_folder, normalize_lcmodel, read_folder_lcmodel, preprocess_lcmodel_data_compare,
                                 read_file_in_folder_lcmodel)
from models.reproduce import parse_url


def layout():
    """Return the layout for the compare xy page for cquest."""
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare LCModel files'),
            dbc.Input(id='data-id1', type='hidden', value=''),
            dbc.Input(id='data-id2', type='hidden', value=''),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('File 1'),
                                    dcc.Dropdown(
                                        id='file1-selected-compare-lcmodel',
                                        options=[
                                        ],
                                        value='',
                                        clearable=False,
                                    ),
                                    dcc.Checklist(
                                        id='aggregate-data-compare-1-lcmodel',
                                        options=[
                                            {'label': 'Aggregate data', 'value': 'aggregate'},
                                        ],
                                        value=[],
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('File 2'),
                                    dcc.Dropdown(
                                        id='file2-selected-compare-lcmodel',
                                        options=[
                                        ],
                                        value='',
                                        clearable=False,
                                    ),
                                    dcc.Checklist(
                                        id='aggregate-data-compare-2-lcmodel',
                                        options=[
                                            {'label': 'Aggregate data', 'value': 'aggregate'},
                                        ],
                                        value=[],
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-compare-xy-lcmodel',
                                        options=[
                                            {'label': 'No', 'value': 'No'},
                                            {'label': 'Yes', 'value': 'Yes'},
                                        ],
                                        value='No',
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
                        id='nn-chart-compare-lcmodel',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
        ]
    )


@callback(
    Output('file1-selected-compare-lcmodel', 'options'),
    Output('file2-selected-compare-lcmodel', 'options'),
    Output('file1-selected-compare-lcmodel', 'value', allow_duplicate=True),
    Output('file2-selected-compare-lcmodel', 'value', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate',
)
def bind_selects(_):
    """Bind the charts to the data"""
    id1, id2 = parse_url(request.referrer)
    files1 = get_files_in_folder(id1, extension='table')
    files2 = get_files_in_folder(id2, extension='table')
    return [{'label': file, 'value': file} for file in files1], [{'label': file, 'value': file} for file in files2], \
        files1[0], files2[0]


@callback(
    Output('nn-chart-compare-lcmodel', 'figure'),
    Output('file1-selected-compare-lcmodel', 'value', allow_duplicate=True),
    Output('file2-selected-compare-lcmodel', 'value', allow_duplicate=True),
    Input('file1-selected-compare-lcmodel', 'value'),
    Input('file2-selected-compare-lcmodel', 'value'),
    Input('aggregate-data-compare-1-lcmodel', 'value'),
    Input('aggregate-data-compare-2-lcmodel', 'value'),
    Input('normalization-compare-xy-lcmodel', 'value'),
    prevent_initial_call=True,
)
def update_chart(file1, file2, aggregate1, aggregate2, normalization):
    """Bind the charts to the data"""
    id1, id2 = parse_url(request.referrer)
    if aggregate1:
        data1 = read_folder_lcmodel(id1)
    else:
        file1 = file1 if file1 else get_files_in_folder(id1, 'table')[0]
        data1 = read_file_in_folder_lcmodel(id1, file1)
    if aggregate2:
        data2 = read_folder_lcmodel(id2)
    else:
        file2 = file2 if file2 else get_files_in_folder(id2, 'table')[0]
        data2 = read_file_in_folder_lcmodel(id2, file2)
    # delete metabolites water1, water2, water3
    data1, data2 = preprocess_lcmodel_data_compare(data1, data2)
    # concat data with pandas.concat
    # replace the previous line using concat instead of append
    data = pd.concat([data1, data2], ignore_index=True)

    if normalization == 'Yes':
        normalize_lcmodel(data)

    fig1 = px.box(
        x=data['Metabolite'],
        y=data['Rate_Raw'],
        title='Comparison of metabolites',
        labels={
            'x': 'Metabolite',
            'y': 'Rate_Raw',
        },
        color=data['File'],
    )
    value_file1 = file1 if not aggregate1 else None
    value_file2 = file2 if not aggregate2 else None
    return fig1, value_file1, value_file2
