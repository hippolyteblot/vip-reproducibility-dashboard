from dash import html, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from flask_login import login_required, current_user

from models.home import get_available_applications, get_available_versions
from models.modify_experiment import get_available_experiments, update_experiment_on_db, get_experiment_details


def layout():
    return html.Div(
        id='modify_experiment',
        children=[
            html.Div(
                [
                    dbc.Spinner(color="primary"),
                ],
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '50vh'}
            ),
            html.P("Checking access rights..."),
        ]
    )

def authorize_page():
    return html.Div(
        [
            html.H1('Modify an existing experiment'),
            html.Div(
                html.P(
                    'Please select an experiment to modify from the list below. '
                )
            ),
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(
                                [
                                    html.P('Application:', style={'margin-bottom': '0'}),
                                    dbc.Select(
                                        id='application-select',
                                        options=[
                                            {'label': 'All', 'value': -1},
                                        ],
                                        value='app1'
                                    ),
                                ],
                                style={'width': '50%'}
                            ),
                            html.Div(
                                [
                                    html.P('Version:', style={'margin-bottom': '0'}),
                                    dbc.Select(
                                        id='version-select',
                                    ),
                                ],
                                style={'width': '50%'}
                            ),
                        ],
                        style={'display': 'flex', 'justify-content': 'space-between'}
                    ),
                    html.Div(
                        [
                            html.P('Experiment:', style={'margin-bottom': '0'}),
                            dbc.Select(
                                id='experiment-select',
                                options=[
                                ],
                            ),
                        ],
                    ),
                ],
                style={'display': 'flex', 'flex-direction': 'column', 'gap': '1rem'}
            ),
            html.Br(),
            dbc.Card(
                [
                    dbc.CardHeader('Experiment details'),
                    dbc.CardBody(
                        [
                            html.P('Experiment name:'),
                            dbc.Input(id='experiment-name', type='text', placeholder='Experiment name'),
                            html.Br(),
                            html.P('Experiment description:'),
                            dbc.Textarea(id='experiment-description', placeholder='Experiment description'),
                            html.Br(),
                            html.P('Inputs description:'),
                            dbc.Textarea(id='inputs-description', placeholder='Inputs description'),
                            html.Br(),
                            html.P('Outputs description:'),
                            dbc.Textarea(id='outputs-description', placeholder='Outputs description'),
                            dbc.Button('Save changes', id='save-changes', color='primary', className='mt-3')
                        ]
                    )
                ]
            ),
            html.Div(id='update_info')
        ]
    )

def refuse_page():
    return html.Div(
        [
            html.H1('Modify an existing experiment'),
            html.Div(
                html.P(
                    'You do not have permission to access this page.'
                )
            )
        ]
    )


@callback(
    Output('modify_experiment', 'children'),
    Input('modify_experiment', 'children')
)
def check_admin_access(_):
    if not current_user.is_authenticated or not current_user.role == 'admin':
        return refuse_page()
    return authorize_page()

@callback(
    Output('application-select', 'options'),
    Input('application-select', 'value')
)
def update_application_list(app_id):
    apps = get_available_applications()
    apps_list = [
        {'label': app['name'], 'value': app['id']} for app in apps
    ]
    apps_list.insert(0, {'label': 'All', 'value': -1})
    return apps_list


@callback(
    Output('version-select', 'options'),
    Output('version-select', 'value'),
    Input('application-select', 'value'),
)
def update_version_list(app_id):
    # Get the list of versions from the database
    app_versions = get_available_versions(app_id)
    return [
        {'label': version['number'], 'value': version['id']} for version in app_versions
    ], app_versions[0]['id'] if app_versions else None


@callback(
    Output('experiment-select', 'options'),
    Output('experiment-select', 'value'),
    Input('version-select', 'value')
)
def update_experiment_list(version):
    # Get the list of experiments from the database
    exps = get_available_experiments(version)
    return [
        {'label': exp['name'], 'value': exp['id']} for exp in exps
    ], exps[0]['id'] if exps else None


@callback(
    Output('experiment-name', 'value'),
    Output('experiment-description', 'value'),
    Output('inputs-description', 'value'),
    Output('outputs-description', 'value'),
    Input('experiment-select', 'value')
)
def update_experiment_info(exp_id):
    # Get the experiment details from the database
    exp = get_experiment_details(exp_id)
    return exp['name'], exp['experiment_description'], exp['inputs_description'], exp['outputs_description']


@callback(
    Output('update_info', 'children'),
    Input('save-changes', 'n_clicks'),
    State('experiment-select', 'value'),
    State('experiment-name', 'value'),
    State('experiment-description', 'value'),
    State('inputs-description', 'value'),
    State('outputs-description', 'value'),
    prevent_initial_call=True
)
def save_experiment_info(_, exp_id, name, description, inputs, outputs):
    if not current_user.is_authenticated or not current_user.role == 'admin':
        return dbc.Alert('You do not have permission to access this page.', color='danger')
    result = update_experiment_on_db(exp_id, name, description, inputs, outputs)
    if result:
        return dbc.Alert('Experiment updated successfully!', color='success')
    else:
        return dbc.Alert('An error occurred while updating the experiment.', color='danger')
