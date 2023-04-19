from dash import html
import dash_bootstrap_components as dbc

footer = html.Footer(
    dbc.Container(
        [
            'Footer item'
        ],
    ),
)