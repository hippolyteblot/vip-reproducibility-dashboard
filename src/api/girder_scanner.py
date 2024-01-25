import re
from flask_restful import Resource
from utils.settings import DB, GVC, GIRDER_PROCESSED_FOLDER


class GirderScanner(Resource):
    def __init__(self):
        pass

    def get(self):
        """Get the data from Girder"""
        insert_data_from_girder()
        return {"message": "Data inserted from Girder to the database"}


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
    insert_workflow_if_not_exist(workflow, experiment_id)
    # insert_json_if_not_exist(workflow['_id'], workflow_id, experiment_id)


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
