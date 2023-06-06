from dash import html, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc

from models.add_experiment import add_experiment_to_db, get_available_applications, get_available_versions
from utils.settings import GVC


def layout():
    return html.Div(
        [
            html.H1('Add a new experiment recorded on the VIP platform'),
            html.Div(
                html.P(
                    'Please fill the following form to add a new experiment to the dashboard.'
                )
            ),

            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            html.H3('Add an experiment'),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Experiment name'),
                                    dbc.Input(
                                        id='experiment',
                                        type='text',
                                        placeholder='Experiment',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Application'),
                                    dbc.Select(
                                        id='application',
                                        options=load_applications(),
                                    ),
                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Label('Version'),
                                    dbc.Select(
                                        id='version',
                                        options=[
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Input to vary'),
                                    dbc.Input(
                                        id='input-to-vary',
                                        type='text',
                                        placeholder='Input to vary',
                                        style={'width': '100%'},
                                    ),

                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Label('Inputs directory (on girder)'),
                                    # button for opening a modal to add a new input to vary
                                    dbc.Button(
                                        'Select a fileset directory',
                                        id='add-new-input-to-vary',
                                        color='primary',
                                        className='mr-1',
                                        style={'width': '100%', 'marginTop': '10px', 'marginBottom': '10px'},
                                    ),
                                    dbc.Input(
                                        id='fileset-directory',
                                        type='text',
                                        placeholder='Fileset directory id',
                                        style={'width': '100%', 'display': 'none'},
                                    ),
                                    dbc.Input(
                                        id='fileset-directory-label',
                                        type='text',
                                        placeholder='Fileset directory label',
                                        style={'width': '100%'},
                                        disabled=True,
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader('Girder directory'),
                                            dbc.ModalBody(
                                                children=[
                                                    dbc.Row(
                                                        id='girder-path',
                                                        children='source_folder',
                                                        style={'fontWeight': 'bold', 'padding': '10px'},
                                                    ),
                                                    dbc.Row(
                                                        id='girder-id-path',
                                                        children='63b6e2d34d15dd536f0484c3',
                                                        style={'display': 'none'},
                                                    ),
                                                    dbc.RadioItems(
                                                        id='selected-option',
                                                        options=[]
                                                    ),
                                                ],
                                                id='select-fileset-directory-modal-body',
                                            ),
                                            html.Div(
                                                children=[],
                                                id='container',
                                            ),
                                            dbc.ModalFooter(
                                                children=[
                                                    dbc.Button(
                                                        'Back',
                                                        id='parent-folder-btn',
                                                        className='mr-auto',
                                                        color='danger',
                                                    ),
                                                    dbc.Button(
                                                        'Open',
                                                        id='open-folder-btn',
                                                        className='mr-auto',
                                                    ),
                                                    dbc.Button(
                                                        'Choose',
                                                        id='choose-folder-btn',
                                                        className='mr-auto',
                                                        color='success',
                                                    ),
                                                ],
                                            ),
                                        ],
                                        id='select-fileset-directory-modal',
                                        size='lg',
                                    ),
                                ],
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Parameters'),
                                    dbc.Textarea(
                                        id='parameters',
                                        placeholder='Parameters',
                                        style={'width': '100%', 'height': '100px'},
                                    ),
                                ],
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Number of reminders'),
                                    dbc.Input(
                                        id='number-of-reminders',
                                        type='number',
                                        placeholder='Number of reminders',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Label('Launch frequency'),
                                    dbc.Input(
                                        id='launch-frequency',
                                        type='number',
                                        placeholder='Launch frequency',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),

                    dbc.Row(
                        children=[
                            dbc.Button(
                                "Add experiment",
                                type="submit",
                                color="primary",
                                id="add-experiment",
                                className="mr-1",
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    html.Div(children='', id='add-exp-output-state'),
                ],
                style={'marginLeft': '20%', 'marginRight': '20%', 'padding': '20px'},
                className='card',
            ),
        ]
    )


@callback(
    Output('fileset-directory', 'value'),
    Output('fileset-directory-label', 'value'),
    Output('select-fileset-directory-modal', 'is_open', allow_duplicate=True),
    Input('choose-folder-btn', 'n_clicks'),
    State('selected-option', 'value'),
    State('girder-path', 'children'),
    State('selected-option', 'options'),
    prevent_initial_call=True,
)
def update_fileset_directory(choose_folder_btn, selected_option, girder_path, options):
    if choose_folder_btn is not None:
        if selected_option not in girder_path.split('/'):
            # need to add the label of the selected item to girder_path
            selected_folder = ''
            for option in options:
                if option['value'] == selected_option:
                    selected_folder = option['label']
                    break
            girder_path += '/' + selected_folder

        return selected_option, girder_path, False
    return '', '', True


@callback(
    Output('selected-option', 'options', allow_duplicate=True),
    Output('girder-path', 'children'),
    Output('girder-id-path', 'children'),
    Input('open-folder-btn', 'n_clicks'),
    Input('parent-folder-btn', 'n_clicks'),
    State('selected-option', 'value'),
    State('selected-option', 'options'),
    State('girder-path', 'children'),
    State('girder-id-path', 'children'),
    prevent_initial_call=True,
)
def update_dir_options(open_folder_btn, parent_folder_btn, selected_option, options, girder_path, girder_id_path):
    selected_label = None

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    # if parent_folder_btn is the trigger
    if trigger == 'parent-folder-btn':
        if len(girder_path.split('/')) < 2:
            return get_dir_options(), girder_path, girder_id_path
        parent_id = girder_id_path.split('/')[-2]
        parent_path = '/'.join(girder_path.split('/')[:-1])
        return get_dir_options(parent_id), parent_path, '/'.join(girder_id_path.split('/')[:-1])

    if selected_option is not None:
        for option in options:
            if option['value'] == selected_option:
                selected_label = option['label']
                break
    if selected_option is not None:
        return get_dir_options(
            selected_option), girder_path + '/' + selected_label, girder_id_path + '/' + selected_option
    return [], girder_path


@callback(
    Output('select-fileset-directory-modal', 'is_open'),
    Output('selected-option', 'options'),
    Output('girder-path', 'children', allow_duplicate=True),
    Output('girder-id-path', 'children', allow_duplicate=True),
    Input('add-new-input-to-vary', 'n_clicks'),
    State('select-fileset-directory-modal', 'is_open'),
    prevent_initial_call=True,
)
def select_fileset_directory_modal(n_clicks, is_open):
    if n_clicks is None:
        return is_open, [], ''
    return not is_open, get_dir_options(), 'source_folder', '63b6e2d34d15dd536f0484c3'


def get_dir_options(location_id=None):
    if location_id is None:
        folders = GVC.get_folders_in_folder()
        items = []
    else:
        folders = GVC.get_folders_in_folder(location_id)
        items = GVC.get_items_in_folder(location_id)

    folders_structure = [
        {'label': folder['name'], 'value': folder['_id']} for folder in folders
    ]

    items_structure = [
        {'label': item['name'], 'value': item['_id'], 'disabled': True} for item in items
    ]

    return folders_structure + items_structure


@callback(
    Output('add-exp-output-state', 'children'),
    Output('add-exp-output-state', 'className'),
    Input('add-experiment', 'n_clicks'),
    State('application', 'value'),
    State('version', 'value'),
    State('input-to-vary', 'value'),
    State('parameters', 'value'),
    State('experiment', 'value'),
    State('number-of-reminders', 'value'),
    State('launch-frequency', 'value'),
)
def add_experiment(n_clicks, application, version, input_to_vary, parameters, experiment,
                   number_of_reminders, launch_frequency):
    if n_clicks is None:
        return '', ''
    elif not application or not version or not parameters or \
            not experiment or not number_of_reminders or not launch_frequency:
        return 'Please fill all the fields', 'alert alert-danger'
    single_run = False
    alert, alert_type, _ = add_experiment_to_db(application, version, input_to_vary, "a enlever", parameters,
                                                "undefined", experiment, number_of_reminders, launch_frequency,
                                                single_run)
    return alert, 'alert ' + alert_type


def load_applications():
    applications = get_available_applications()
    return [{'label': app['name'], 'value': app['id']} for app in applications]


@callback(
    Output('version', 'options'),
    Input('application', 'value'),
)
def load_versions(application):
    versions = get_available_versions(application)
    return [{'label': version['number'], 'value': version['id']} for version in versions]
