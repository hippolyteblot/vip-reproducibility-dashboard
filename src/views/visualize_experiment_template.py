import base64
import json
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import plotly.express as px


def layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2(
                children=[
                    'Study an experiment : ',
                    html.Span(
                        id='experiment-name',
                        style={'color': 'blue'},
                    ),
                ],
            ),
            html.Div(
                dbc.Row(
                    children=[
                        html.Div(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.H4('Upload a data file'),
                                        dcc.Upload(
                                            id='upload-data-template',
                                            children=html.Div(
                                                [
                                                    'Drag and Drop or ',
                                                    html.A('Select Files'),
                                                ]
                                            ),
                                            style={
                                                'height': '60px',
                                                'lineHeight': '60px',
                                                'borderWidth': '1px',
                                                'borderStyle': 'dashed',
                                                'borderRadius': '5px',
                                                'textAlign': 'center',
                                                'margin': '10px',
                                            },
                                            multiple=True,
                                        ),
                                    ],
                                ),
                            ],
                            className='card-body',
                            style={'width': 'auto'},
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.H4('Upload a config file'),
                                        dcc.Upload(
                                            id='upload-template',
                                            children=html.Div(
                                                [
                                                    'Drag and Drop or ',
                                                    html.A('Select Files'),
                                                ]
                                            ),
                                            style={
                                                'height': '60px',
                                                'lineHeight': '60px',
                                                'borderWidth': '1px',
                                                'borderStyle': 'dashed',
                                                'borderRadius': '5px',
                                                'textAlign': 'center',
                                                'margin': '10px',
                                            },
                                            multiple=True,
                                        ),
                                    ],
                                )
                            ],
                            className='card-body',
                            style={'width': 'auto'},
                        )
                    ],
                    style={'display': 'flex', 'flexDirection': 'row'},
                    className='card',
                ),
            ),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Graph type'),
                                    dcc.Dropdown(
                                        id='graph-type-template',
                                        options=[
                                            {'label': 'Bar chart', 'value': 'bar'},
                                            {'label': 'Scatter plot', 'value': 'scatter'},
                                            {'label': 'Box plot', 'value': 'box'},
                                        ],
                                        value='bar',
                                        clearable=False,
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('X axis'),
                                    dcc.Dropdown(
                                        id='x-axis-template',
                                        clearable=False,
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Y axis'),
                                    dcc.Dropdown(
                                        id='y-axis-template',
                                        clearable=False,
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Color group'),
                                    dcc.Dropdown(
                                        id='color-group-template',
                                        clearable=False,
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
                            ),
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('Filters'),
                                    dbc.Textarea(
                                        id='filters-template',
                                        placeholder='Enter a filter. Enter conditions separated by a comma such as '
                                                    '"Signal group=1|4, Signal group!=2", Amplitude>2',
                                        style={'width': '100%', 'height': 100},
                                    ),
                                    dbc.Button(
                                        'Apply filters',
                                        id='trigger-filters-template',
                                        style={'marginTop': 10},
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
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
                        id='exec-chart-template',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
            html.Div(
                children=[
                    html.H3('Chart description'),
                    dbc.Textarea(
                        id='description-exp-template',
                        style={'width': '100%', 'height': 100},
                        placeholder='Type the description of the chart here...',
                    ),
                ],
            ),
            html.Div(
                children=[
                ],
                id='additional-info-template',
            ),
            dcc.Download(
                id='download-template'
            ),
            dbc.Button(
                'Download',
                id='download-button-template',
                style={'marginTop': 10},
            ),

        ]
    )


@callback(
    Output('x-axis-template', 'options'),
    Output('y-axis-template', 'options'),
    Output('color-group-template', 'options'),
    Output('x-axis-template', 'value'),
    Output('y-axis-template', 'value'),
    Output('color-group-template', 'value'),
    Input('upload-data-template', 'contents'),
)
def update_dropdowns(contents):
    """Update the dropdowns"""
    if contents is None:
        return [], [], [], dash.no_update, dash.no_update, dash.no_update
    content_type, content_string = contents[0].split(',')
    with open('src/views/data.feather', 'wb') as f:
        f.write(base64.b64decode(content_string))
    data = pd.read_feather('src/views/data.feather')
    options = [{'label': column, 'value': column} for column in data.columns]
    options.sort(key=lambda x: x['label'])
    color_options = [{'label': 'None', 'value': 'None'}] + options
    return options, options, color_options, options[0]['value'], options[1]['value'], 'None'


@callback(
    Output('exec-chart-template', 'figure'),
    Input('x-axis-template', 'value'),
    Input('y-axis-template', 'value'),
    Input('graph-type-template', 'value'),
    Input('color-group-template', 'value'),
    Input('trigger-filters-template', 'n_clicks'),
    State('filters-template', 'value'),
)
def update_chart(x_column, y_column, graph_type, color_column, _, filters):
    print(x_column, y_column, graph_type, color_column, filters)
    """Update the chart"""
    if x_column is None or y_column is None:
        return {}
    data = pd.read_feather('src/views/data.feather')
    charts = {
        'bar': px.bar,
        'scatter': px.scatter,
        'box': px.box,
    }

    for column in data.columns:
        if data[column].dtype == 'object':
            try:
                data[column] = data[column].apply(lambda x: float(x))
            except ValueError:
                pass

    if filters is not None:
        filters = filters.split(',')
        filters = [f.replace('\n', '') for f in filters]
        for f in filters:
            # check if there is = or !=
            if '!=' in f:
                column, values = f.split('!=')
                values = values.split('|')
                # keep only the values that are not in values
                data = data[~data[column].isin(values)]
            elif '>' in f:
                column, value = f.split('>')
                if '=' in value:
                    data = data[data[column] >= float(value)]
                else:
                    data = data[data[column] > float(value)]
            elif '<' in f:
                column, value = f.split('<')
                if '=' in value:
                    data = data[data[column] <= float(value)]
                else:
                    data = data[data[column] < float(value)]
            elif '=' in f:
                column, values = f.split('=')
                values = values.split('|')
                data = data[data[column].isin(values)]

    graph = charts[graph_type](
        x=data[x_column],
        y=data[y_column],
        title="Choose one",
        labels={'x': x_column, 'y': y_column},
        data_frame=data,
        color=data[color_column] if color_column != 'None' else None,
    )
    return graph


# output is a file (json)
@callback(
    Output('download-template', 'data'),
    Input('download-button-template', 'n_clicks'),
    State('graph-type-template', 'value'),
    State('x-axis-template', 'value'),
    State('y-axis-template', 'value'),
    State('color-group-template', 'value'),
    State('filters-template', 'value'),
    State('description-exp-template', 'value'),
    prevent_initial_call=True,
)
def download_config(_, graph_type, x_column, y_column, color_column, filters, description):
    """Download the config file"""
    config = {
        'graph_type': graph_type,
        'x_column': x_column,
        'y_column': y_column,
        'color_column': color_column,
        'filters': filters.replace('\n', '').split(',') if filters is not None else [],
        'description': description,
    }
    return dict(
        content=json.dumps(config, indent=4),
        filename='config.json'
    )


@callback(
    Output('graph-type-template', 'value'),
    Output('x-axis-template', 'value', allow_duplicate=True),
    Output('y-axis-template', 'value', allow_duplicate=True),
    Output('color-group-template', 'value', allow_duplicate=True),
    Output('filters-template', 'value'),
    Output('description-exp-template', 'value'),
    Input('upload-template', 'contents'),
    State('upload-template', 'filename'),
    prevent_initial_call=True,
)
def upload_config(contents, filename):
    """Upload the config file"""
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    content_type, content_string = contents[0].split(',')
    if 'json' in filename[0]:
        config = json.loads(base64.b64decode(content_string).decode('utf-8'))
        filters_str = '\n'.join(config['filters']).replace('\n', ',\n')
        return (config['graph_type'], config['x_column'], config['y_column'], config['color_column'], filters_str,
                config['description'])
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
