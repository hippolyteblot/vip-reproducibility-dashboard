import base64
import json
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, callback, clientside_callback, ctx
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
                                                    'Drag and Drop or Select Files',
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
                                            accept='.feather',
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
                                                children="Drag and Drop or Select Files",
                                                id='upload-config-label',
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
                                            accept='.json',
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
                                    dbc.Col(
                                        children=[
                                            # Filled by the callback
                                        ],
                                        id='filters-container',
                                    ),
                                    dbc.Button(
                                        'Add filter',
                                        id='add-filter-btn',
                                        style={'marginTop': 10},
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        'Remove filter',
                                        id='remove-filter-btn',
                                        style={'marginTop': 10, 'marginLeft': 10},
                                        className='btn btn-danger',
                                    ),
                                    dbc.Button(
                                        'Apply filter(s)',
                                        id='apply-filters-btn',
                                        style={'marginTop': 10, 'marginLeft': 10},
                                        className='btn btn-success',
                                    ),
                                    clientside_callback(
                                        """
                                        function(n_clicks, current_content, template) {
                                            if (n_clicks === undefined) return current_content;
                                            // Clone the current content to avoid modifying it directly
                                            let list = JSON.parse(JSON.stringify(current_content));
                                            
                                            list.push(template[0].props.children[0]);

                                            // Return the updated content
                                            return list;
                                        }
                                        """,
                                        Output('filters-container', 'children'),
                                        Input('add-filter-btn', 'n_clicks'),
                                        State('filters-container', 'children'),
                                        State('filter-template', 'children'),
                                    ),
                                    clientside_callback(
                                        """
                                        function(n_clicks, current_content) {
                                            // Remove the last filter
                                            if (n_clicks === undefined) return current_content;
                                            // Clone the current content to avoid modifying it directly
                                            let list = JSON.parse(JSON.stringify(current_content));
                                            list.pop();
                                            // Return the updated content
                                            return list;
                                        }
                                        """,
                                        Output('filters-container', 'children', allow_duplicate=True),
                                        Input('remove-filter-btn', 'n_clicks'),
                                        State('filters-container', 'children'),
                                        prevent_initial_call=True,
                                    ),

                                    clientside_callback(
                                        """
                                        function(n_clicks, current_content) {
                                            if (n_clicks === undefined) return "";
                                            // Read all the filters and build a string

                                            // Clone the current content to avoid modifying it directly
                                            let list = JSON.parse(JSON.stringify(current_content));

                                            // Get the filters
                                            let filters = [];
                                            for (let i = 0; i < list.length; i++) {
                                                let filter = list[i].props.children;
                                                let field = filter[0].props.children[1].props.value;
                                                let operator = filter[1].props.children[1].props.value;
                                                let value = filter[2].props.children[1].props.value;
                                                filters.push(field + operator + value);
                                            }

                                            // Return the updated content
                                            return filters.join(',');
                                        }
                                        """,
                                        Output('filters-template', 'value'),
                                        Input('apply-filters-btn', 'n_clicks'),
                                        State('filters-container', 'children'),
                                    ),

                                    clientside_callback(
                                        """
                                        function(n_clicks, filters_str, filter_template) {
                                            if (n_clicks === undefined) return "";
                                            filters_str = filters_str.replace('\\n', '');
                                            // Read the string and build the filters
                                            let rows = filters_str.split(',');
                                            let filters = [];
                                            for (let i = 0; i < rows.length; i++) {
                                                let row = rows[i];
                                                // Search for the operator (>, <, =, !=)
                                                let operator = '';
                                                if (row.includes('!=')) {
                                                    operator = '!=';
                                                } else if (row.includes('>')) {
                                                    operator = '>';
                                                } else if (row.includes('<')) {
                                                    operator = '<';
                                                } else if (row.includes('=')) {
                                                    operator = '=';
                                                }
                                                // Split the row
                                                let [field, value] = row.split(operator);
                                                
                                                let clone = JSON.parse(JSON.stringify(filter_template));
                                                clone = clone[0].props.children[0   ]
                                                console.log(clone);
                                                clone.props.children[0].props.children[1].props.value = field;
                                                clone.props.children[1].props.children[1].props.value = operator;
                                                clone.props.children[2].props.children[1].props.value = value;
                                                filters.push(clone);
                                            }
                                            console.log(filters);
                                            return filters;
                                        }
                                        """,
                                        Output('filters-container', 'children', allow_duplicate=True),
                                        Input('filters-clientside-trigger', 'value'),
                                        State('filters-template', 'value'),
                                        State('filter-template', 'children'),
                                        prevent_initial_call=True,
                                    ),
                                ],
                                className='card-body',
                                style={'width': 'auto'},
                            ),
                            dcc.Input(
                                id='filters-template',
                                type='hidden',
                            ),
                            dcc.Input(
                                id='filters-clientside-trigger',
                                type='hidden',
                            ),
                            html.Div(
                                id='filter-template',
                                children=[
                                    html.Div(
                                        children=[
                                            dbc.Row(
                                                className='filter-row',
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            html.P(
                                                                'Field',
                                                                style={'marginBottom': 0},
                                                            ),
                                                            dcc.Dropdown(
                                                                options=[],  # options are updated in the callback
                                                                clearable=False,
                                                                id='field-filter-template',
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Col(
                                                        children=[
                                                            html.P(
                                                                'Operator',
                                                                style={'marginBottom': 0},
                                                            ),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': '=', 'value': '='},
                                                                    {'label': '!=', 'value': '!='},
                                                                    {'label': '>', 'value': '>'},
                                                                    {'label': '<', 'value': '<'},
                                                                ],
                                                                clearable=False,
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Col(
                                                        children=[
                                                            html.P(
                                                                'Value',
                                                                style={'marginBottom': 0},
                                                            ),
                                                            dbc.Input(
                                                                type='text',
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Col(
                                                        children=[
                                                            html.P(
                                                                'Enter the value(s). You can separate them with | to '
                                                                'allow multiple values.',
                                                                style={'marginBottom': 0},
                                                            ),
                                                        ],
                                                        style={'display': 'flex', 'alignItems': 'center'},
                                                    ),
                                                ],
                                                style={'display': 'flex', 'flexDirection': 'row'},
                                            ),

                                        ],
                                    ),
                                ],
                                style={'display': 'none'},
                            ),
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                ],

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
                className='btn btn-success',
            ),
        ],
        style={'margin': 10},
    )


@callback(
    Output('x-axis-template', 'options'),
    Output('y-axis-template', 'options'),
    Output('field-filter-template', 'options'),
    Output('color-group-template', 'options'),
    Output('x-axis-template', 'value'),
    Output('y-axis-template', 'value'),
    Output('color-group-template', 'value'),
    Output('add-filter-btn', 'disabled'),
    Input('upload-data-template', 'contents'),
)
def update_dropdowns(contents):
    triggered_id = ctx.triggered_id
    if triggered_id is None:
        raise dash.exceptions.PreventUpdate
    if contents is None:
        return [], [], [], [], dash.no_update, dash.no_update, dash.no_update, True
    content_type, content_string = contents[0].split(',')
    with open('src/views/data.feather', 'wb') as f:
        f.write(base64.b64decode(content_string))
    data = pd.read_feather('src/views/data.feather')
    options = [{'label': column, 'value': column} for column in data.columns]
    options.sort(key=lambda x: x['label'])
    color_options = [{'label': 'None', 'value': 'None'}] + options
    return options, options, options, color_options, options[0]['value'], options[1]['value'], 'None', False


@callback(
    Output('exec-chart-template', 'figure'),
    Input('x-axis-template', 'value'),
    Input('y-axis-template', 'value'),
    Input('graph-type-template', 'value'),
    Input('color-group-template', 'value'),
    Input('filters-template', 'value'),
)
def update_chart(x_column, y_column, graph_type, color_column, filters):
    triggered_id = ctx.triggered_id
    print(triggered_id)
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

    # check that the data is not empty
    if data.empty:
        return {}
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
    Output('filters-template', 'value', allow_duplicate=True),
    Output('filters-clientside-trigger', 'value'),
    Output('description-exp-template', 'value'),
    Output('upload-config-label', 'children'),
    Input('upload-template', 'contents'),
    State('upload-template', 'filename'),
    State('x-axis-template', 'options'),
    prevent_initial_call=True,
)
def upload_config(contents, filename, fields):
    """Upload the config file"""
    fields_list = [f['label'] for f in fields]
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Drag and Drop or Select Files'
    content_type, content_string = contents[0].split(',')
    if 'json' in filename[0]:
        try:
            config = json.loads(base64.b64decode(content_string).decode('utf-8'))
            filters_str = '\n'.join(config['filters']).replace('\n', ',\n')
            # Check that the fields are still in the data
            print(config['x_column'], config['y_column'], config['color_column'])
            print(fields_list)
            if config['x_column'] not in fields_list or config['y_column'] not in fields_list:
                print('field not in fields')

            if config['color_column'] not in fields_list and config['color_column'] != 'None':
                print('field not in fields or None')
                raise dash.exceptions.PreventUpdate
            for f in config['filters']:
                operator = ''
                if '!=' in f:
                    operator = '!='
                elif '>' in f:
                    operator = '>'
                elif '<' in f:
                    operator = '<'
                elif '=' in f:
                    operator = '='
                else:
                    print('field not in fields FILTERS')
                    raise dash.exceptions.PreventUpdate
                field, value = f.split(operator)
                if field not in fields_list:
                    print('field not in fields')
                    raise dash.exceptions.PreventUpdate
            return (config['graph_type'], config['x_column'], config['y_column'], config['color_column'], filters_str,
                    0, config['description'], filename[0])
        except Exception as e:
            print(e)
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, 'The config file is not valid or unadapted to the current data')
    return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, 'Drag and Drop or Select Files')
