from dash import html, Output, Input, State, callback, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc

from models.home import load_exp_from_db, load_exec_from_db


def layout():
    return html.Div(
        [
            html.H1('Welcome on the VIP reproductibility dashboard'),
            html.Div(
                children=[
                    html.P(
                        'This dashboard allows you to reproduce and compare the results of executions on the VIP '
                        'platform.'
                    ),
                    html.P(
                        'You can visualize a specific execution to analyze its results, or observe the results of an '
                        'experiment composed of several executions, on several data and with different parameters.'
                    ),
                ],
            ),

            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                "Reproduce an execution",
                                id="exec-open",
                                n_clicks=0,
                                style={'width': 'fit-content'},
                                className="mr-1"
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Select an execution to reproduce")),
                                    dbc.ModalBody(
                                        children=[
                                            # Search bar
                                            dbc.Input(
                                                id='search-exec',
                                                type='text',
                                                placeholder='Search for an execution',
                                                style={'width': '100%'},
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    dbc.Row(
                                                        className='card',
                                                        id='execution-container',
                                                        style={'flexDirection': 'row'},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                children=[
                                                    dbc.Row(
                                                        className='card',
                                                        id='execution-container-hidden',
                                                        style={'display': 'none'},
                                                    )
                                                ],
                                            )
                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="exec-close", className="ms-auto", n_clicks=0
                                        )
                                    ),
                                ],
                                id="exec-modal",
                                is_open=False,
                            ),
                            dbc.Button(
                                "Reproduce an experiment",
                                id="exp-open",
                                n_clicks=0,
                                style={'width': 'fit-content'},
                                className="mr-1"
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Select an experiment to reproduce")),
                                    dbc.ModalBody(
                                        children=[
                                            # Search bar
                                            dbc.Input(
                                                id='search-exp',
                                                type='text',
                                                placeholder='Search for an experiment',
                                                style={'width': '100%'},
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    # List of executions (from db)
                                                    dbc.Row(
                                                        className='card',
                                                        id='experiment-container',
                                                        style={'flexDirection': 'row'},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                children=[
                                                    # List of executions (from db)
                                                    dbc.Row(
                                                        className='card',
                                                        id='experiment-container-hidden',
                                                        style={'display': 'none'},
                                                    ),
                                                ],
                                            )

                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="exp-close", className="ms-auto", n_clicks=0
                                        )
                                    ),
                                ],
                                id="exp-modal",
                                is_open=False,
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px'},
                    ),
                ],
                className='card',
            )
        ]
    )


@callback(
    Output("exec-modal", "is_open"),
    Output("execution-container-hidden", "children"),
    [Input("exec-open", "n_clicks"), Input("exec-close", "n_clicks")],
    [State("exec-modal", "is_open")],
)
def toggle_modal_exec(n1, n2, is_open):
    if n1 or n2:
        exec_list = load_exec_from_db()
        exec_data = get_list_structure(exec_list, '/repro-execution')

        return not is_open, exec_data

    return is_open, []


@callback(
    Output("exp-modal", "is_open"),
    Output("experiment-container-hidden", "children", allow_duplicate=True),
    [Input("exp-open", "n_clicks"), Input("exp-close", "n_clicks")],
    [State("exp-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal_exp(n1, n2, is_open):
    if n1 or n2:
        exp_list = load_exp_from_db()
        exp_data = get_list_structure(exp_list, '/repro-experiment')
        return not is_open, exp_data

    return is_open, []


# Search on client side version (use a js function in src/assets/search.js)
clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="search_exp",
    ),
    Output("experiment-container", "children", allow_duplicate=True),
    [Input("search-exp", "value"), Input("experiment-container-hidden", "children")],
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="search_exp",
    ),
    Output("execution-container", "children", allow_duplicate=True),
    [Input("search-exec", "value"), Input("execution-container-hidden", "children")],
    prevent_initial_call=True
)

# Search on server side version
"""
@callback(
    Output("experiment-container", "children", allow_duplicate=True),
    [Input("search-exp", "value")],
    prevent_initial_call=True
)
def search_exp(value):
    exp_list = load_exp_from_db()
    if value is not None:
        exp_list = [exp for exp in exp_list if value.lower() in exp.get("name").lower()]

    exp_data = get_list_structure(exp_list, '/repro-experiment')

    return exp_data


@callback(
    Output("execution-container", "children", allow_duplicate=True),
    [Input("search-exec", "value")],
    prevent_initial_call=True
)
def search_exec(value):
    exec_list = load_exec_from_db()
    if value is not None:
        exec_list = [exec_item for exec_item in exec_list if value.lower() in exec_item.get("name").lower()]

    exec_data = get_list_structure(exec_list, '/repro-execution')

    return exec_data
"""


def get_list_structure(exp_list, href):
    return dbc.Row(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                exp.get("name"),
                                id='repro-execution',
                                className="mr-1",
                                href=href + '?experiment=' + str(exp.get("id")),
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'},
                    )
                    for exp in exp_list
                ],
            )
        ],
        style={'flexDirection': 'row'},
    )
