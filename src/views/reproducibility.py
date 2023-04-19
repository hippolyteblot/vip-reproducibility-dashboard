from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc


def layout():
    return html.Div(
        [
            html.H1('Choose an execution to reproduce'),

            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            html.H2(
                                'Spectro'
                            ),
                            dbc.Button(
                                "Reproduce",
                                color="primary",
                                id="ask-private-access",
                                className="mr-1",
                                href='/reproduce',
                            ),
                            dbc.Input(
                                id="access-password",
                                type="password",
                                placeholder="Enter password",
                            ),
                            html.Div(
                                id="alert",
                                style={"display": "none"},
                            ),
                        ],
                        className='card-body',
                    ),
                ],
                className='card-body',
            ),
        ]
    )


@callback(
    Output("alert", "children"),
    Output("alert", "className"),
    Output("alert", "style"),
    Output("ask-private-access", "n_clicks"),
    Input("ask-private-access", "n_clicks"),
    Input("access-password", "value"),
)
def ask_private_access(n_clicks, password):
    if n_clicks is None:
        return "Enter password", "alert alert-primary", {"display": "none"}, None
    if password == "1234":
        return "Correct password", "alert alert-success", {"display": "block"}, None
    return "Wrong password", "alert alert-danger", {"display": "block"}, None