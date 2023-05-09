from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from flask_login import current_user

from models.reproduce import get_files_in_folder, read_user_folder


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
    Output('file1-selected-compare', 'value'),
    Output('file2-selected-compare', 'value'),
    Input('url', 'pathname'),
)
def bind_selects(pathname):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]
    files1 = get_files_in_folder(id1)
    files2 = get_files_in_folder(id2)
    return [{'label': file, 'value': file} for file in files1], [{'label': file, 'value': file} for file in files2], \
        files1[0], files2[0]


@callback(
    Output('nn-chart-compare', 'figure'),
    Input('file1-selected-compare', 'value'),
    Input('file2-selected-compare', 'value'),
)
def update_chart(file1, file2):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1]
    data1 = read_user_folder(id1, file1)
    data2 = read_user_folder(id2, file2)
    data1['Amplitude'] = data1['Amplitude'].apply(lambda x: float(x))
    data2['Amplitude'] = data2['Amplitude'].apply(lambda x: float(x))
    data1['File'] = 'File 1'
    data2['File'] = 'File 2'
    data = data1.append(data2)

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

    return fig1

