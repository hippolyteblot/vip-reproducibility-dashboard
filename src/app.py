# -----------------------------------------------------------------------------
# Description : Main application file. It defines the layout of the application
# Author      : Hippolyte Blot. <hippolyte.blot@creatis.insa-lyon.fr>
# Created on  : 2023-10-27
# -----------------------------------------------------------------------------
"""
Main application file. It defines the layout of the application
"""

import re
import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager

from utils.girder_vip_client import get_jsons_from_local, GVC
# local imports
from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK, DB, GIRDER_PROCESSED_FOLDER
from models.login import User
from components.login import login_location
from components import navbar, footer


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

    # Login manager object will be used to log in / logout users
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        query = "SELECT * FROM users WHERE id = %s"
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

    local_app.layout = serve_layout  # set the layout to the serve_layout function

    return local_app


def insert_data_from_girder():
    """Insert data from Girder to the database"""
    applications = get_girder_folders(GIRDER_PROCESSED_FOLDER)
    for application in applications:
        insert_application_from_girder(application)


def insert_application_from_girder(application):
    """Insert an application from Girder to the database"""
    application_id = insert_application_if_not_exist(application)
    version_regex = re.compile(r'\d+(\.\d+)*')
    versions = get_girder_folders(application['_id'], regex=version_regex)
    for version in versions:
        insert_version_from_girder(version, application_id)


def insert_version_from_girder(version, application_id):
    """Insert a version from Girder to the database"""
    version_id = insert_version_if_not_exist(version, application_id)
    experiments = get_girder_folders(version['_id'])
    for experiment in experiments:
        insert_experiment_from_girder(experiment, version_id)


def insert_experiment_from_girder(experiment, version_id):
    """Insert an experiment from Girder to the database"""
    experiment_id = insert_experiment_if_not_exist(experiment, version_id)
    timestamp_regex = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}')
    workflows = get_girder_folders(experiment['_id'], regex=timestamp_regex)
    for workflow in workflows:
        insert_workflow_from_girder(workflow, experiment_id)


def insert_workflow_from_girder(workflow, experiment_id):
    """Insert a workflow from Girder to the database"""
    workflow_id = insert_workflow_if_not_exist(workflow, experiment_id)
    #insert_json_if_not_exist(workflow['_id'], workflow_id, experiment_id)


def get_girder_folders(parent_folder_id, regex=None):
    """Get folders from Girder given a parent folder ID"""
    if regex is None:
        return GVC.get_folders(parent_folder_id)
    folders = GVC.get_folders(parent_folder_id)
    return [folder for folder in folders if regex.match(folder['name'])]


def insert_application_if_not_exist(application):
    """Insert an application into the database if it does not exist"""
    query = "SELECT * FROM application WHERE name = %s"
    result = DB.fetch_one(query, (application['name'],))
    if result is None:
        query = "INSERT INTO application (name, girder_id) VALUES (%s, %s)"
        return DB.execute(query, (application['name'], application['_id']))
    return result['id']


def insert_version_if_not_exist(version, application_id):
    """Insert a version into the database if it does not exist"""
    query = "SELECT * FROM app_version WHERE number = %s AND application_id = %s"
    result = DB.fetch_one(query, (version['name'], application_id))
    if result is None:
        query = "INSERT INTO app_version (number, application_id, girder_id) VALUES (%s, %s, %s)"
        return DB.execute(query, (version['name'], application_id, version['_id']))
    return result['id']


def insert_experiment_if_not_exist(experiment, version_id):
    """Insert an experiment into the database if it does not exist"""
    query = "SELECT * FROM experiment WHERE name = %s AND version_id = %s"
    result = DB.fetch_one(query, (experiment['name'], version_id))
    if result is None:
        query = "INSERT INTO experiment (name, version_id, girder_id) VALUES (%s, %s, %s)"
        return DB.execute(query, (experiment['name'], version_id, experiment['_id']))
    return result['id']


def insert_workflow_if_not_exist(workflow, experiment_id):
    """Insert a workflow into the database if it does not exist"""
    query = "SELECT * FROM workflow WHERE girder_id = %s"
    result = DB.fetch_one(query, (workflow['_id'],))
    if result is None:
        query = "INSERT INTO workflow (timestamp, experiment_id, girder_id) VALUES (%s, %s, %s)"
        return DB.execute(query, (workflow['name'], experiment_id, workflow['_id']))
    return result['id']


def insert_json_if_not_exist(workflow_id, workflow_id_db, experiment_id):
    """Insert a JSON file into the database if it does not exist"""
    # jsons = GVC.get_jsons(workflow_id)
    jsons = get_jsons_from_local(workflow_id)
    for json in jsons:
        query = "SELECT * FROM input WHERE md5 = %s"
        result = DB.fetch_one(query, (json['input']['md5'],))
        if result is None:
            query = "INSERT INTO input (md5, girder_id, name) VALUES (%s, %s, %s)"
            input_id = DB.execute(query, (json['input']['md5'], json['input']['girder_id'],
                                          json['input']['file_name']))
        else:
            input_id = result['id']
        query = "SELECT * FROM output WHERE md5 = %s"
        result = DB.fetch_one(query, (json['output']['md5'],))
        if result is None:
            query = "INSERT INTO output (md5, workflow_id, girder_id, name, input_id) VALUES (%s, %s, %s, %s, %s)"
            DB.execute(query, (json['output']['md5'], workflow_id_db, json['output']['girder_id'],
                               json['output']['file_name'], input_id))
    # check if the experiment already has a parameter attached to it
    query = "SELECT * FROM parameter WHERE md5 = %s"
    result = DB.fetch_one(query, (jsons[0]['parameters_file']['md5'],))
    if result is None:
        query = "INSERT INTO parameter (md5, girder_id, name) VALUES (%s, %s, %s)"
        parameter_id = DB.execute(query, (jsons[0]['parameters_file']['md5'],
                                          jsons[0]['parameters_file']['girder_id'],
                                          jsons[0]['parameters_file']['file_name']))
    else:
        parameter_id = result['id']
    query = "SELECT * FROM experiment WHERE id = %s"
    result = DB.fetch_one(query, (experiment_id,))
    if result['parameter_id'] is None:
        query = "UPDATE experiment SET parameter_id = %s WHERE id = %s"
        DB.execute(query, (parameter_id, experiment_id))


# insert_data_from_girder()
app = create_app()
app.run_server(
    host=APP_HOST,
    port=APP_PORT,
    debug=APP_DEBUG,
    dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
)
DB.connect()
