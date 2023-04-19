import dash_bootstrap_components as dbc

from components.login import login_card


def layout():
    return dbc.Row(
        dbc.Col(
            login_card,
            md=6,
            lg=4,
            xxl=3,
        ),
        justify='center'
    )