import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager
import os

# local imports
from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK
from components.login import User, login_location
from components import navbar, footer
from utils.settings import DB


def create_app():
    server = Flask(__name__)
    app = dash.Dash(
        __name__,
        server=server,
        use_pages=True,  # turn on Dash pages
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME
        ],  # fetch the proper css items we want
        meta_tags=[
            {  # check if device is a mobile device. This is a must if you do any mobile styling
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1'
            }
        ],
        suppress_callback_exceptions=True,
        title='Reproducibility Dashboard'
    )

    server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

    # Login manager object will be used to log in / logout users
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        query = "SELECT * FROM USERS WHERE id = %s"
        result = DB.fetch_one(query, (user_id,))
        if result is None:
            return None
        return User(user_id, result['username'], result['role'])

    def serve_layout():
        """Define the layout of the application"""
        return html.Div(
            [
                login_location,
                navbar,
                dbc.Container(
                    dash.page_container,
                    class_name='my-2'
                ),
                footer
            ]
        )

    app.layout = serve_layout  # set the layout to the serve_layout function

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(
        host=APP_HOST,
        port=APP_PORT,
        debug=APP_DEBUG,
        dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )
