"""
View for 404 page
"""
from dash import html


def layout():
    """Return the layout for the 404 page."""
    return html.Div(
        [
            html.H1('404 - Page not found'),
            html.Div(
                html.A('Return home', href='/')
            )
        ]
    )
