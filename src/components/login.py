"""
Components for the login page
"""
from dash import html, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask_login import current_user, logout_user, login_user, UserMixin

from models.login import check_user
from utils.settings import get_GVC


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, user_id, username, role='user'):
        self.id = user_id
        self.username = username
        self.role = role

login_card = dbc.Card(
    [
        dbc.CardHeader('Login'),
        dbc.CardBody(
            [
                dbc.Input(
                    placeholder='Username',
                    type='text',
                    id='login-username',
                    class_name='mb-2'
                ),
                dbc.Input(
                    placeholder='Password',
                    type='password',
                    id='login-password',
                    class_name='mb-2'
                ),
                dbc.Button(
                    'Login',
                    n_clicks=0,
                    type='submit',
                    id='login-button',
                    class_name='float-end'
                ),
                html.Div(children='', id='output-state')
            ]
        )
    ]
)

login_location = dcc.Location(id='url-login', refresh=False)
login_info = html.Div(id='user-status-header')
logged_in_info = html.Div(
    [
        dbc.Button(
            html.I(className='fas fa-circle-user fa-xl'),
            id='user-popover',
            outline=True,
            color='light',
            class_name='border-0'
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader('Settings'),
                dbc.PopoverBody(
                    [
                        dcc.Link(
                            [
                                html.I(className='fas fa-arrow-right-from-bracket me-1'),
                                'Logout'
                            ],
                            href='/logout'
                        )
                    ]
                )
            ],
            target='user-popover',
            trigger='focus',
            placement='bottom'
        )
    ],
)
logged_out_info = dbc.NavItem(
    dbc.NavLink(
        'Login',
        href='/login'
    )
)

modify_experiment = html.Div(
    id='modify-experiment-link',
)

modify_experiment_admin = dbc.NavItem(
    dbc.NavLink(
        'Modify experiment',
        href='/modify-experiment'
    )
)


@callback(
    Output('user-status-header', 'children'),
    Output('modify-experiment-link', 'children'),
    Input('url-login', 'pathname')
)
def update_authentication_status(path):
    """Update the authentication status of the user"""
    logged_in = current_user.is_authenticated
    if path == '/logout' and logged_in:
        logout_user()
        children = [logged_out_info, ""]
    elif logged_in:
        GVC = get_GVC()
        GVC.clean_user_download_folder(current_user.id)
        children = [logged_in_info, modify_experiment_admin] \
            if current_user.role == 'admin' else [logged_in_info, modify_experiment]
    else:
        children = [logged_out_info, ""]
    return children


@callback(
    Output('output-state', 'children'),
    Output('url-login', 'pathname'),
    Input('login-button', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value'),
    State('_pages_location', 'pathname'),
    prevent_initial_call=True
)
def login_button_click(n_clicks, username, password, pathname):
    """Login the user"""
    if n_clicks > 0:
        result = check_user(username, password)
        if result is not None:
            login_user(result)
            return 'Login Successful', '/'
        return 'Incorrect username or password', pathname
    raise PreventUpdate
