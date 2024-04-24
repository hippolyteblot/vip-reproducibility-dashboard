# -----------------------------------------------------------------------------
# Description : Main application file. It defines the layout of the application
# Author      : Hippolyte Blot. <hippolyte.blot@creatis.insa-lyon.fr>
# Created on  : 2023-10-27
# -----------------------------------------------------------------------------
"""
Main application file. It defines the layout of the application
"""
import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
import ssl

# local imports
from utils.settings import (APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK, SSL_CERT_CHAIN, SSL_SERVER_KEY,
                            get_DB, PRODUCTION)

from components import navbar, footer
from components.login import User, login_location
from api.girder_scanner import GirderScanner


def create_app():
    """The create_app function is used to create the Dash app. It is used to create the app in the main.py file."""
    server = Flask(__name__)
    local_app = dash.Dash(
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

    local_app.layout = serve_layout  # set the layout to the serve_layout function

    # create a tmp folder if it does not exist
    if not os.path.exists('src/tmp'):
        os.makedirs('src/tmp')

    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        DB = get_DB()
        query = "SELECT * FROM users WHERE id = %s"
        result = DB.fetch_one(query, (user_id,))
        if result is None:
            return None
        return User(user_id, result['username'], result['role'])

    return local_app


app = create_app()
api = Api(app.server)
api.add_resource(GirderScanner, '/api/girder_scanner')

context = None
if PRODUCTION:
    print("Running in production mode")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(SSL_CERT_CHAIN, SSL_SERVER_KEY)

app.run_server(
    host=APP_HOST,
    port=APP_PORT,
    debug=APP_DEBUG,
    dev_tools_props_check=DEV_TOOLS_PROPS_CHECK,
    ssl_context=context
)
