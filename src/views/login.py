"""
Login page.
"""
import dash_bootstrap_components as dbc

from components.login import login_card


def layout():
    """Return the layout for the login page."""
    return dbc.Row(
        dbc.Col(
            login_card,
            md=6,
            lg=4,
            xxl=3,
        ),
        justify='center'
    )
