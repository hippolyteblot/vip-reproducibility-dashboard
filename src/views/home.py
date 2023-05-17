import re

from dash import html, Output, Input, State, callback, clientside_callback, ClientsideFunction, dcc
import dash_bootstrap_components as dbc

from models.home import load_exp_from_db, load_wf_from_db, get_available_applications, get_available_versions, \
    save_file_for_comparison


def layout():
    return html.Div(
        [
            html.H1('Welcome on the VIP reproducibility dashboard'),
            html.Div(
                children=[
                    html.P(
                        'This dashboard allows you to reproduce and compare the results of executions on the VIP '
                        'platform.'
                    ),
                    html.P(
                        'You can visualize a specific execution to analyze its results, or observe the results of an '
                        'experiment composed of several executions, on several data and with different parameters.'
                    ),
                ],
            ),

            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                "Study and compare workflows",
                                id="exec-open",
                                n_clicks=0,
                                style={'width': 'fit-content'},
                                className="mr-1"
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Select a workflow to study")),
                                    dbc.ModalBody(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Label(
                                                        children=[
                                                            "Select an application",
                                                            html.Br(),
                                                            dbc.Select(
                                                                id='select-app-wf',
                                                                options=[
                                                                    {'label': 'All', 'value': 'all'}
                                                                ],
                                                                value='vip',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                    html.Label(
                                                        children=[
                                                            "Select a version",
                                                            html.Br(),
                                                            dbc.Select(
                                                                id='select-version-wf',
                                                                options=[
                                                                    {'label': 'All', 'value': 'all'}
                                                                ],
                                                                value='all',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                    html.Label(
                                                        children=[
                                                            "Search for a workflow",
                                                            dbc.Input(
                                                                id='search-exec',
                                                                type='text',
                                                                placeholder='Type here to search',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                style={'display': 'flex', 'gap': '10px', 'flexDirection': 'column'},
                                            ),
                                            # Search bar

                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    # List of experiments (from db)
                                                    dbc.Col(
                                                        className='card',
                                                        id='wf-container',
                                                        style={'flexDirection': 'column'},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                children=[
                                                    # Used for the search bar powered by js (not displayed)
                                                    dbc.Row(
                                                        className='card',
                                                        id='wf-container-hidden',
                                                        style={'display': 'none'},
                                                    ),
                                                ],
                                            )

                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="exec-close", className="ms-auto", n_clicks=0
                                        )
                                    ),
                                ],
                                id="exec-modal",
                                is_open=False,
                            ),
                            dbc.Button(
                                "Reproduce an experiment",
                                id="exp-open",
                                n_clicks=0,
                                style={'width': 'fit-content'},
                                className="mr-1"
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Select an experiment to reproduce")),
                                    dbc.ModalBody(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Label(
                                                        children=[
                                                            "Select an application",
                                                            html.Br(),
                                                            dbc.Select(
                                                                id='select-app',
                                                                options=[
                                                                    {'label': 'All', 'value': 'all'}
                                                                ],
                                                                value='vip',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                    html.Label(
                                                        children=[
                                                            "Select a version",
                                                            html.Br(),
                                                            dbc.Select(
                                                                id='select-version',
                                                                options=[
                                                                    {'label': 'All', 'value': 'all'}
                                                                ],
                                                                value='all',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                    html.Label(
                                                        children=[
                                                            "Search for an experiment",
                                                            dbc.Input(
                                                                id='search-exp',
                                                                type='text',
                                                                placeholder='Type here to search',
                                                                style={'width': '100%'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                style={'display': 'flex', 'gap': '10px', 'flexDirection': 'column'},
                                            ),
                                            # Search bar

                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    # List of experiments (from db)
                                                    dbc.Col(
                                                        className='card',
                                                        id='experiment-container',
                                                        style={'flexDirection': 'column'},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                children=[
                                                    # Used for the search bar powered by js (not displayed)
                                                    dbc.Row(
                                                        className='card',
                                                        id='experiment-container-hidden',
                                                        style={'display': 'none'},
                                                    ),
                                                ],
                                            )

                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="exp-close", className="ms-auto", n_clicks=0
                                        )
                                    ),
                                ],
                                id="exp-modal",
                                is_open=False,
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                ],
                style={'display': 'flex', 'justifyContent': 'center', 'gap': '10px'},
                className='card',
            ),
            html.Br(),
            dbc.Row(
                children=[
                    html.Br(),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.P('Select the application'),
                                    dbc.Select(
                                        id='application-selected-for-upload',
                                        options=[
                                            {'label': 'cQuest', 'value': 'cquest'},
                                            {'label': 'BraTS', 'value': 'brats'},
                                        ],
                                        value='cquest',
                                        style={'width': '100%'},
                                    ),
                                    html.Br(),
                                    html.P('Select the format'),
                                    dbc.Select(
                                        id='data-type-selected-for-upload',
                                        options=[
                                            {'label': '1 file to 1 file', 'value': '1-1'},
                                            {'label': 'x files to y files (two zipped folders)', 'value': 'x-y'},
                                            {'label': 'x files (one zipped folder)', 'value': 'x'},
                                        ],
                                        value='1-1',
                                        style={'width': '100%'},
                                    ),
                                ],
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.P('Upload a first file to compare'),
                                    html.Br(),
                                    dcc.Upload(
                                        id='upload-data-1',
                                        children=html.Div(
                                            children=[
                                                'Drag and Drop or ',
                                                html.A('Select Files')
                                            ],
                                            id='upload-data-1-div'
                                        ),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                        },
                                        multiple=False
                                    ),
                                    dcc.Input(
                                        id='data-1-uuid',
                                        type='hidden',
                                    ),
                                    dcc.Input(
                                        id='data-type-uploaded1',
                                        type='hidden',
                                    ),
                                    html.Br(),
                                    html.Div(
                                        id='output-data-upload-1',
                                        style={'display': 'flex', 'justifyContent': 'center'}
                                    ),
                                ],
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.P('Upload a second file to compare'),
                                    html.Br(),
                                    dcc.Upload(
                                        id='upload-data-2',
                                        children=html.Div(
                                            children=[
                                                'Drag and Drop or ',
                                                html.A('Select Files')
                                            ],
                                            id='upload-data-2-div'
                                        ),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                        },
                                        multiple=False
                                    ),
                                    dcc.Input(
                                        id='data-2-uuid',
                                        type='hidden',
                                    ),
                                    dcc.Input(
                                        id='data-type-uploaded2',
                                        type='hidden',
                                    ),
                                    html.Br(),
                                    html.Div(
                                        id='output-data-upload-2',
                                        style={'display': 'flex', 'justifyContent': 'center'}
                                    ),
                                ],
                                className='card-body',
                                id='upload-data-2-container',
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Button(
                                        'Compare',
                                        id='compare-btn',
                                        style={'width': '100%'},
                                        className='btn btn-primary',
                                        href='/compare-11?id1=&id2=',
                                        disabled=True,
                                    ),
                                ],
                                className='card-body',
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                ],
                className='card',
            )
        ]
    )


@callback(
    Output('upload-data-2-container', 'style'),
    Input('data-type-selected-for-upload', 'value'),
)
def update_upload_data_2_container(type_selected):
    if type_selected == 'x':
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@callback(
    Output('compare-btn', 'disabled'),
    Input('compare-btn', 'href'),
    State('data-type-uploaded1', 'value'),
    State('data-type-uploaded2', 'value'),
    State('application-selected-for-upload', 'value'),
    State('data-type-selected-for-upload', 'value'),
    prevent_initial_call=True
)
def update_compare_btn(_, type1, type2, app, type_selected):
    # assert that if type_selected is 1-1, type1 and type2 are txt else zip
    if type_selected == '1-1' and ((type1 == 'txt' and type2 == 'txt' and app == 'cquest') or
                                   (type1 == 'nii' and type2 == 'nii' and app == 'brats') or \
                                   (type1 in ['gz', 'nii'] and type2 in ['gz', 'nii']) and app == 'brats'):
        return False
    elif type_selected == 'x-y' and type1 == 'zip' and type2 == 'zip':
        return False
    elif type_selected == 'x' and type1 == 'zip':
        return False
    else:
        return True


@callback(
    Output('upload-data-1-div', 'children'),
    Output('data-1-uuid', 'value'),
    Output('compare-btn', 'href', allow_duplicate=True),
    Output('data-type-uploaded1', 'value'),
    Input('upload-data-1', 'contents'),
    State('compare-btn', 'href'),
    State('upload-data-1', 'filename'),
    State('upload-data-1', 'last_modified'),
    State('data-type-selected-for-upload', 'value'),
    State('application-selected-for-upload', 'value'),
    prevent_initial_call=True
)
def update_output1(content, href, name, date, type_selected, app):
    return update_output(content, href, name, date, 1, type_selected, app)


@callback(
    Output('upload-data-2-div', 'children'),
    Output('data-2-uuid', 'value'),
    Output('compare-btn', 'href', allow_duplicate=True),
    Output('data-type-uploaded2', 'value'),
    Input('upload-data-2', 'contents'),
    State('compare-btn', 'href'),
    State('upload-data-2', 'filename'),
    State('upload-data-2', 'last_modified'),
    State('data-type-selected-for-upload', 'value'),
    State('application-selected-for-upload', 'value'),
    prevent_initial_call=True
)
def update_output2(content, href, name, date, type_selected, app):
    return update_output(content, href, name, date, 2, type_selected, app)


@callback(
    Output('compare-btn', 'href'),
    Input('application-selected-for-upload', 'value'),
    Input('data-type-selected-for-upload', 'value'),
    State('compare-btn', 'href'),
)
def update_href(app, data_type, href):
    app_str = 'compare'
    if app == 'brats':
        app_str = 'compare-nii'
    data_type_str = '11'
    if data_type == 'x-y':
        data_type_str = 'xy'
    elif data_type == 'x':
        data_type_str = 'x'
    href_end = href.split('?')[1]
    href = app_str + '-' + data_type_str + '?' + href_end
    return href


def update_output(content, href, name, date, data_id, data_type, app):
    print("File name : ", name)
    if content is not None and check_type(data_type, name, app):
        file_extension = name.split('.')[-1]
        if file_extension in ['txt', 'zip', 'nii'] or (name.split('.')[-2] == 'nii' and file_extension == 'gz'):
            # save the file in the server
            uuid = save_file_for_comparison(content, name)
            # get olds values
            id1 = 'id1=' + href.split('id1=')[1].split('&id2=')[0]
            id2 = 'id2=' + href.split('id2=')[1]
            # update the href
            if data_id == 1:
                id1 = 'id1=' + str(uuid)
            else:
                id2 = 'id2=' + str(uuid)
            href_begin = href.split('?')[0]
            href = href_begin + '?' + id1 + '&' + id2
            return html.Div([
                html.P('File uploaded: ' + name),
            ]), str(uuid), href, file_extension
        else:
            return html.Div([
                'Wrong file type, please upload a .txt file'
            ]), None, href, None
    else:
        return html.Div([
            'Wrong file type, please upload a file according to the selected application and data type',
        ]), None, href, None


def check_type(data_type, name, app):
    ext = name.split('.')[-1]
    if data_type == '1-1' and app == 'cquest':
        return ext == 'txt'
    elif data_type == '1-1' and app == 'brats':
        return (ext == 'nii') or (name.split('.')[-2] == 'nii' and ext == 'gz')
    elif data_type == 'x-y' or data_type == 'x':
        return ext == 'zip'
    else:
        return False


@callback(
    Output("exec-modal", "is_open"),
    Output("wf-container-hidden", "children", allow_duplicate=True),
    Output("select-app-wf", "options"),
    [Input("exec-open", "n_clicks"), Input("exec-close", "n_clicks")],
    [State("exec-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal_workflows(n1, n2, is_open):
    if n1 or n2:
        wf_list = load_wf_from_db()
        wf_data = get_list_structure2(wf_list, '/repro-workflow')
        applications = get_available_applications()
        options = [{'label': app['name'], 'value': app['id']} for app in applications]
        options.insert(0, {'label': 'All', 'value': 'all'})
        return not is_open, wf_data, options

    return is_open, [], []


@callback(
    Output("experiment-container", "children", allow_duplicate=True),
    Input("select-version", "value"),
    prevent_initial_call=True
)
def filter_exp(version_id):
    exp_list = load_exp_from_db()
    new_exp_list = []
    if version_id != 'all':
        for exp in exp_list:
            if int(exp['version_id']) == int(version_id):
                new_exp_list.append(exp)
    else:
        new_exp_list = exp_list

    exp_data = get_list_structure2(new_exp_list, '/repro-experiment')

    return exp_data


@callback(
    Output("wf-container", "children", allow_duplicate=True),
    Input("select-version-wf", "value"),
    prevent_initial_call=True
)
def filter_wf(version_id):
    wf_list = load_wf_from_db()
    new_wf_list = []
    if version_id != 'all':
        for wf in wf_list:
            if int(wf['version_id']) == int(version_id):
                new_wf_list.append(wf)
    else:
        new_wf_list = wf_list

    wf_data = get_list_structure2(new_wf_list, '/repro-workflow')

    return wf_data


@callback(
    Output("exp-modal", "is_open"),
    Output("experiment-container-hidden", "children", allow_duplicate=True),
    Output("select-app", "options"),
    [Input("exp-open", "n_clicks"), Input("exp-close", "n_clicks")],
    [State("exp-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal_exp(n1, n2, is_open):
    if n1 or n2:
        exp_list = load_exp_from_db()
        # exp_data = get_list_structure(exp_list, '/repro-experiment')
        exp_data = get_list_structure2(exp_list, '/repro-experiment')
        applications = get_available_applications()
        options = [{'label': app['name'], 'value': app['id']} for app in applications]
        options.insert(0, {'label': 'All', 'value': 'all'})
        return not is_open, exp_data, options

    return is_open, [], []


@callback(
    Output("select-version", "options"),
    Output("experiment-container", "children", allow_duplicate=True),
    [Input("select-app", "value")],
    prevent_initial_call=True
)
def update_exp_version_dropdown(app_id):
    versions = get_available_versions(app_id)
    options = [{'label': version['number'], 'value': version['id']} for version in versions]
    options.insert(0, {'label': 'All', 'value': 'all'})
    exp_list = load_exp_from_db()
    new_exp_list = []
    if app_id != 'all':
        for exp in exp_list:
            if int(exp['application_id']) == int(app_id):
                new_exp_list.append(exp)
    else:
        new_exp_list = exp_list

    exp_data = get_list_structure2(new_exp_list, '/repro-execution')
    return options, exp_data


@callback(
    Output("select-version-wf", "options"),
    Output("wf-container", "children", allow_duplicate=True),
    [Input("select-app-wf", "value")],
    prevent_initial_call=True
)
def update_wf_version_dropdown(app_id):
    versions = get_available_versions(app_id)
    options = [{'label': version['number'], 'value': version['id']} for version in versions]
    options.insert(0, {'label': 'All', 'value': 'all'})
    wf_list = load_wf_from_db()
    new_wf_list = []
    if app_id != 'all':
        for wf in wf_list:
            if int(wf['application_id']) == int(app_id):
                new_wf_list.append(wf)
    else:
        new_wf_list = wf_list

    wf_data = get_list_structure2(new_wf_list, '/repro-workflow')
    return options, wf_data


def get_options_version_dropdown(app_id):
    pass


# Search on client side version (use a js function in src/assets/search.js)
clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="search_exp",
    ),
    Output("experiment-container", "children", allow_duplicate=True),
    [Input("search-exp", "value"), Input("experiment-container-hidden", "children")],
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="search_exp",
    ),
    Output("wf-container", "children", allow_duplicate=True),
    [Input("search-exec", "value"), Input("wf-container-hidden", "children")],
    prevent_initial_call=True
)

# Search on server side version
"""
@callback(
    Output("experiment-container", "children", allow_duplicate=True),
    [Input("search-exp", "value")],
    prevent_initial_call=True
)
def search_exp(value):
    exp_list = load_exp_from_db()
    if value is not None:
        exp_list = [exp for exp in exp_list if value.lower() in exp.get("name").lower()]

    exp_data = get_list_structure(exp_list, '/repro-experiment')

    return exp_data


@callback(
    Output("execution-container", "children", allow_duplicate=True),
    [Input("search-exec", "value")],
    prevent_initial_call=True
)
def search_exec(value):
    exec_list = load_exec_from_db()
    if value is not None:
        exec_list = [exec_item for exec_item in exec_list if value.lower() in exec_item.get("name").lower()]

    exec_data = get_list_structure(exec_list, '/repro-execution')

    return exec_data
"""


def get_list_structure(exp_list, href):
    return dbc.Row(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                exp.get("name"),
                                id='repro-execution',
                                className="mr-1",
                                href=href + '?experiment=' + str(exp.get("id")),
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'},
                    )
                    for exp in exp_list
                ],
            )
        ],
        style={'flexDirection': 'row'},
    )


def get_list_structure2(exp_list, href):
    return dbc.Row(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                exp.get("name") + ' - ' + exp.get("application_name") + '/' +
                                exp.get("application_version"),
                                id='repro-execution',
                                className="mr-1",
                                href=href + '?id=' + str(exp.get("id")),
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'},
                    )
                    for exp in exp_list
                ],
            )
        ],
        style={'flexDirection': 'row'},
    )
