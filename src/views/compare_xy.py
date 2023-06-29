import os
import time

import pandas as pd
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request
from models.reproduce import get_girder_id_of_wf
from utils.settings import GVC


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
                                    html.H4('Metabolite'),
                                    dcc.Dropdown(
                                        id='metabolite-name-bland-altman-upload',
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
    Output('metabolite-name-bland-altman-upload', 'value'),
    Input('url', 'value'),
)
def bind_parameters_from_url(execution_id):
    # check if the url contains parameters
    if execution_id != 'None' and request.referrer is not None and len(request.referrer.split('&')) > 2:
        # get the parameters
        metabolite_name = request.referrer.split('&')[2].split('=')[1]

        return metabolite_name
    return 'PCh'


@callback(
    Output('nn-chart-compare', 'figure'),
    Output('metabolite-name-bland-altman-upload', 'options'),
    Output('metabolite-name-bland-altman-upload', 'value', allow_duplicate=True),
    Output('url', 'search'),
    Input('nn-chart-compare', 'children'),
    Input('metabolite-name-bland-altman-upload', 'value'),
    prevent_initial_call=True,
)
def update_chart(_, metabolite):
    id1 = request.referrer.split('id1=')[1].split('&')[0]
    id2 = request.referrer.split('id2=')[1].split('&')[0]

    gid1 = get_girder_id_of_wf(id1)
    gid2 = get_girder_id_of_wf(id2)
    path1 = GVC.download_feather_data(gid1)
    path2 = GVC.download_feather_data(gid2)

    meta_name = metabolite

    while not os.path.exists(path1):
        time.sleep(0.1)
    while not os.path.exists(path2):
        time.sleep(0.1)

    data1 = pd.read_feather(path1)
    data2 = pd.read_feather(path2)

    metabolites = data1['Metabolite'].unique()

    if metabolite is None or metabolite == 'All':
        metabolite = data1['Metabolite'].unique()[0]
    # keep only metabolite of interest
    data1 = data1[data1['Metabolite'] == metabolite]
    data2 = data2[data2['Metabolite'] == metabolite]



    data1['Amplitude'] = data1['Amplitude'].apply(lambda x: float(x))
    data2['Amplitude'] = data2['Amplitude'].apply(lambda x: float(x))

    bland_altman_data = pd.DataFrame(columns=['Mean', 'Difference', '% Difference', 'Sample'])
    # sample is the row Signal
    for sample in data1['Signal'].unique():
        bland_altman_data = pd.concat([
            bland_altman_data,
            pd.DataFrame({
                'Mean': (data1[data1['Signal'] == sample]['Amplitude'].mean() +
                         data2[data2['Signal'] == sample]['Amplitude'].mean()) / 2,
                'Difference': data1[data1['Signal'] == sample]['Amplitude'].mean() -
                              data2[data2['Signal'] == sample]['Amplitude'].mean(),
                '% Difference': (data1[data1['Signal'] == sample]['Amplitude'].mean() -
                                 data2[data2['Signal'] == sample]['Amplitude'].mean()) /
                                ((data1[data1['Signal'] == sample]['Amplitude'].mean() +
                                  data2[data2['Signal'] == sample][
                                      'Amplitude'].mean()) / 2),
                'Sample': sample,
            }, index=[0]),
        ], ignore_index=True)

    fig = px.scatter(
        bland_altman_data,
        x='Mean',
        y='Difference',
        hover_data=['% Difference', 'Sample'],
        title='Bland-Altman plot',
    )
    # add the linear regression

    fig.add_trace(
        px.scatter(
            bland_altman_data,
            x='Mean',
            y='Difference',
            trendline='ols',
            color_discrete_sequence=['black'],
        ).data[1],
    )

    upper_bound = bland_altman_data['Difference'].mean() + 1.96 * bland_altman_data['Difference'].std()
    lower_bound = bland_altman_data['Difference'].mean() - 1.96 * bland_altman_data['Difference'].std()

    # add the upper and lower bound
    fig.add_trace(
        px.line(
            x=[bland_altman_data['Mean'].min(), bland_altman_data['Mean'].max()],
            y=[upper_bound, upper_bound],
            color_discrete_sequence=['red'],
        ).data[0],
    )
    fig.add_trace(
        px.line(
            x=[bland_altman_data['Mean'].min(), bland_altman_data['Mean'].max()],
            y=[lower_bound, lower_bound],
            color_discrete_sequence=['red'],
        ).data[0],
    )

    url = '?id1=' + id1 + '&id2=' + id2 + '&metabolite=' + meta_name

    return fig, [{'label': i, 'value': i} for i in metabolites], metabolite, url
