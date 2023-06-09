from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.cquest_utils import get_txt_files_in_folder, read_cquest_file_in_folder, read_cquest_folder


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare quest2 files'),
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
                                        id='file1-selected-compare',
                                        options=[
                                        ],
                                        value='',
                                        clearable=False,
                                    ),
                                    dcc.Checklist(
                                        id='aggregate-data-compare-1',
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
                                        id='file2-selected-compare',
                                        options=[
                                        ],
                                        value='',
                                        clearable=False,
                                    ),
                                    dcc.Checklist(
                                        id='aggregate-data-compare-2',
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
                                        id='normalization-compare-xy',
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
                    dcc.Graph(
                        id='nn-chart-compare',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
        ]
    )


@callback(
    Output('file1-selected-compare', 'options'),
    Output('file2-selected-compare', 'options'),
    Output('file1-selected-compare', 'value', allow_duplicate=True),
    Output('file2-selected-compare', 'value', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate',
)
def bind_selects(pathname):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]
    files1 = get_txt_files_in_folder(id1)
    files2 = get_txt_files_in_folder(id2)
    return [{'label': file, 'value': file} for file in files1], [{'label': file, 'value': file} for file in files2], \
        files1[0], files2[0]


@callback(
    Output('nn-chart-compare', 'figure'),
    Output('file1-selected-compare', 'value', allow_duplicate=True),
    Output('file2-selected-compare', 'value', allow_duplicate=True),
    Input('file1-selected-compare', 'value'),
    Input('file2-selected-compare', 'value'),
    Input('aggregate-data-compare-1', 'value'),
    Input('aggregate-data-compare-2', 'value'),
    Input('normalization-compare-xy', 'value'),
    prevent_initial_call=True,
)
def update_chart(file1, file2, aggregate1, aggregate2, normalization):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]

    if aggregate1:
        data1 = read_cquest_folder(id1)
    else:
        file1 = file1 if file1 else get_txt_files_in_folder(id1)[0]
        data1 = read_cquest_file_in_folder(id1, file1)
    if aggregate2:
        data2 = read_cquest_folder(id2)
    else:
        file2 = file2 if file2 else get_txt_files_in_folder(id2)[0]
        data2 = read_cquest_file_in_folder(id2, file2)

    # delete metabolites water1, water2, water3
    data1 = data1[~data1['Metabolite'].str.contains('water')]
    data2 = data2[~data2['Metabolite'].str.contains('water')]

    data1['Amplitude'] = data1['Amplitude'].apply(lambda x: float(x))
    data2['Amplitude'] = data2['Amplitude'].apply(lambda x: float(x))
    data1['File'] = 'File 1'
    data2['File'] = 'File 2'
    # concat data with pandas.concat
    data = data1.append(data2, ignore_index=True)

    if normalization:
        # subtract mean and divide by std by metabolite
        means = data.groupby('Metabolite').mean()['Amplitude']
        stds = data.groupby('Metabolite').std()['Amplitude']
        data['Amplitude'] = data.apply(lambda row: (row['Amplitude'] - means[row['Metabolite']]) / stds[row['Metabolite']], axis=1)

    fig1 = px.scatter(
        x=data['Metabolite'],
        y=data['Amplitude'],
        title='Comparison of metabolites',
        labels={
            'x': 'Metabolite',
            'y': 'Amplitude',
        },
        color=data['File'],
    )
    value_file1 = file1 if not aggregate1 else None
    value_file2 = file2 if not aggregate2 else None
    return fig1, value_file1, value_file2

