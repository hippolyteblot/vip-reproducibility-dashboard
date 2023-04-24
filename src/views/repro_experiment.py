from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

from models.reproduce import get_prebuilt_data, get_parameters_for_spectro, get_all_execution_data

# Todo : Optimize data loading (dont load data when the server starts)
data = get_prebuilt_data()
metabolites, voxels, groups = get_parameters_for_spectro(data)
# Voxels values are converted to string to avoid Dash to use a gradient color scale


def layout():
    return html.Div(
        [
            html.H2('Reproduce an experiment'),
            # Parameter menu
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Metabolite'),
                                    dcc.Dropdown(
                                        id='metabolite-name',
                                        options=[
                                            {'label': metabolite.get('label'), 'value': metabolite.get('value')}
                                            for metabolite in metabolites
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
                                    html.H4('Voxel'),
                                    dcc.Dropdown(
                                        id='voxel-number',
                                        options=[
                                            {'label': voxel.get('label'), 'value': voxel.get('value')}
                                            for voxel in voxels
                                        ],
                                        value=-1,
                                        clearable=False,
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Graph'),
                                    dcc.Dropdown(
                                        id='graph-type',
                                        options=[
                                            {'label': 'Box', 'value': 'box'},
                                            {'label': 'Violin', 'value': 'violin'},
                                            {'label': 'Scatter', 'value': 'scatter'},
                                        ],
                                        value='box',
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
                                id='exp-chart-group1',
                                config={"displayModeBar": False},
                            ),
                            dcc.Graph(
                                id='exp-chart-group2',
                                config={"displayModeBar": False},
                            ),
                        ],
                        className='card-body',
                    )
                ],
                className='card',
            )
        ]
    )


@callback(
    Output('exp-chart-group1', 'figure'),
    Output('exp-chart-group2', 'figure'),
    Input('metabolite-name', 'value'),
    Input('voxel-number', 'value'),
    Input('graph-type', 'value')
)
def update_chart(metabolite, voxel, graph_type):
    global data  # TODO: find a proper way to do this



    # get only the data of the metabolite
    if metabolite != 'All':
        df = data[data["Metabolite"] == metabolite]
    else:
        df = data
    if voxel != -1:
        # get only the data of the voxel
        df = df[df["Voxel"] == voxel]
    data1 = df[df["Group"] == "A"]
    data2 = df[df["Group"] == "B"]

    if metabolite == 'All':

        selected_metabolites = data1['Metabolite'].unique()
        # for data1 and data2, get the mean and the std foreach metabolite
        means1 = {}
        stds1 = {}
        means2 = {}
        stds2 = {}
        for metabolite in selected_metabolites:
            means1[metabolite] = data1[data1['Metabolite'] == metabolite]['Amplitude'].mean()
            stds1[metabolite] = data1[data1['Metabolite'] == metabolite]['Amplitude'].std()
            means2[metabolite] = data2[data2['Metabolite'] == metabolite]['Amplitude'].mean()
            stds2[metabolite] = data2[data2['Metabolite'] == metabolite]['Amplitude'].std()

        # Foreach amplitude in each metabolite, normalize it by the mean and std of the metabolite
        for metabolite in selected_metabolites:
            mean = means1[metabolite]
            std = stds1[metabolite]
            data1.loc[data1['Metabolite'] == metabolite, 'Normalized'] = (data1[data1['Metabolite'] == metabolite]
                                                                          ['Amplitude'] - mean) / std
            mean = means2[metabolite]
            std = stds2[metabolite]
            data2.loc[data2['Metabolite'] == metabolite, 'Normalized'] = (data2[data2['Metabolite'] == metabolite]
                                                                          ['Amplitude'] - mean) / std
            # redo the previous instructions but use .loc['row_indexer', 'column_indexer'] = value

        graph1 = None
        graph2 = None
        if graph_type == 'box':
            graph1 = px.box(
                x=data1['Metabolite'],
                y=data1['Normalized'],
                color=data1['Voxel'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )

            graph2 = px.box(
                x=data2['Metabolite'],
                y=data2['Normalized'],
                color=data2['Voxel'],
                title='Comparison of metabolites with set of parameters B',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )
        elif graph_type == 'violin':
            graph1 = px.violin(
                x=data1['Metabolite'],
                y=data1['Normalized'],
                color=data1['Voxel'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )

            graph2 = px.violin(
                x=data2['Metabolite'],
                y=data2['Normalized'],
                color=data2['Voxel'],
                title='Comparison of metabolites with set of parameters B',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )
        elif graph_type == 'scatter':
            graph1 = px.scatter(
                x=data1['Metabolite'],
                y=data1['Normalized'],
                color=data1['Voxel'],
                title='Comparison of metabolites with set of parameters A',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )

            graph2 = px.scatter(
                x=data2['Metabolite'],
                y=data2['Normalized'],
                color=data2['Voxel'],
                title='Comparison of metabolites with set of parameters B',
                labels={
                    'x': 'Metabolite',
                    'y': 'Normalized amplitude',
                    'color': 'Voxel',
                },
            )

        return graph1, graph2

    graph1 = None
    graph2 = None
    if graph_type == 'box':
        graph1 = px.box(
            x=data1['Signal'],
            y=data1['Amplitude'],
            color=data1['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )

        graph2 = px.box(
            x=data2['Signal'],
            y=data2['Amplitude'],
            color=data2['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters B',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )
    elif graph_type == 'violin':
        graph1 = px.violin(
            x=data1['Signal'],
            y=data1['Amplitude'],
            color=data1['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )

        graph2 = px.violin(
            x=data2['Signal'],
            y=data2['Amplitude'],
            color=data2['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters B',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )
    elif graph_type == 'scatter':
        graph1 = px.scatter(
            x=data1['Signal'],
            y=data1['Amplitude'],
            color=data1['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters A',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )

        graph2 = px.scatter(
            x=data2['Signal'],
            y=data2['Amplitude'],
            color=data2['Voxel'],
            title='Comparison of metabolite ' + metabolite + ' with set of parameters B',
            labels={
                'x': 'Signal',
                'y': 'Amplitude',
                'color': 'Voxel',
            },
        )

    return graph1, graph2
