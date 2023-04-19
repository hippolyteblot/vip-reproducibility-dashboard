from dash import html, callback, Output, Input, State
import dash_bootstrap_components as dbc

from models.add_experience import add_experience_to_db
"""
applications = [
    {
        'label': 'App 1',
        'versions': [
            "1.0",
            "1.1",
            "1.2",
        ]
    },
    {
        'label': 'App 2',
        'versions': [
            "0.1",
            "0.2",
        ],
    },
]
"""


def layout():
    return html.Div(
        [
            html.H1('Add a new experience recorded on the VIP platform'),
            html.Div(
                html.P(
                    'Please fill the following form to add a new experience to the dashboard.'
                )
            ),

            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            html.H3('Add an experience'),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Label('Application'),
                                    dbc.Input(
                                        id='application',
                                        type='text',
                                        placeholder='Application',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Label('Version'),
                                    dbc.Input(
                                        id='version',
                                        type='text',
                                        placeholder='Version',
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
                                    html.Label('Fileset directory'),
                                    dbc.Input(
                                        id='fileset-dir',
                                        type='text',
                                        placeholder='Fileset directory',
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
                                    html.Label('Parameters'),
                                    dbc.Input(
                                        id='parameters',
                                        type='text',
                                        placeholder='Parameters',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Label('Results directory'),
                                    dbc.Input(
                                        id='results-dir',
                                        type='text',
                                        placeholder='Results directory',
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
                                    html.Label('Experiment'),
                                    dbc.Input(
                                        id='experiment',
                                        type='text',
                                        placeholder='Experiment',
                                        style={'width': '100%'},
                                    ),
                                ],
                            ),
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
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                    dbc.Row(
                        children=[
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
                                "Add experience",
                                type="submit",
                                color="primary",
                                id="add-experience",
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
            )
        ]
    )


"""
@callback(
    Output('version', 'options'),
    Output('version', 'value'),
    Output('version', 'disabled'),
    Input('application', 'value'),
)
def update_version_options(application):
    app = next(app for app in applications if app['label'] == application)
    return [
        {'label': version, 'value': version}
        for version in app['versions']
    ], app['versions'][0], False
"""


@callback(
    Output('add-exp-output-state', 'children'),
    Output('add-exp-output-state', 'className'),
    Input('add-experience', 'n_clicks'),
    State('application', 'value'),
    State('version', 'value'),
    State('input-to-vary', 'value'),
    State('fileset-dir', 'value'),
    State('parameters', 'value'),
    State('results-dir', 'value'),
    State('experiment', 'value'),
    State('number-of-reminders', 'value'),
    State('launch-frequency', 'value'),
)
def add_experience(n_clicks, application, version, input_to_vary, fileset_dir, parameters, results_dir, experiment,
                   number_of_reminders, launch_frequency):
    if n_clicks is None:
        return '', ''
    alert, alert_type = add_experience_to_db(application, version, input_to_vary, fileset_dir, parameters, results_dir,
                                             experiment, number_of_reminders, launch_frequency)
    return alert, 'alert ' + alert_type
