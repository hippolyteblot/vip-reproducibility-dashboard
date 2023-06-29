from dash import html, callback, Output, Input, State
import dash_bootstrap_components as dbc

# local imports
from .login import login_info, add_experiment

logo_main = '/assets/logos/logo_main.png'

# component
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        html.Img(src=logo_main, style={'height': '40px', 'width': '40px', 'marginRight': '10px',
                                                       'backgroundColor': 'white', 'borderRadius': '50%',
                                                       'padding': '5px'}),
                        html.P('Reproducibility Dashboard', className='logo-text',
                               style={'margin': '0', 'textDecoration': 'none', 'color': 'white'}),
                    ],
                    align='center',
                    className='g-0',
                    style={'fontSize': '1.8rem', 'display': 'flex', 'flexWrap': 'nowrap', 'alignTtems': 'center',
                           'justifyContent': 'center'}
                ),
                href='/',
            ),
            dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink(
                                'Home',
                                href='/'
                            )
                        ),
                        add_experiment,
                        html.Div(
                            login_info,
                            style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}
                        )
                    ]
                ),
                id='navbar-collapse',
                style={'maxWidth': 'fit-content', 'fontSize': '1.4rem'},
                navbar=True
            ),
        ]
    ),
    color='dark',
    dark=True,
)


@callback(
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open'),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
