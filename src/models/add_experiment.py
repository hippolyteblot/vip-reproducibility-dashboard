from utils.settings import DB
from flask_login import current_user


def add_experiment_to_db(application: str, version: str, input_to_vary: str, fileset_dir: str, parameters: str,
                         results_dir: str, experiment: str, number_of_reminders: int, launch_frequency: int,
                         single_run: bool):
    """Add an experiment to the database"""
    # Check if the user is logged in
    if not current_user.is_authenticated:
        message = 'You are not logged in'
        alert = 'alert-danger'
        insert_id = None
    # Check if the user is an admin
    elif not current_user.role == 'admin':
        message = 'You are not authorized to add an experiment'
        alert = 'alert-danger'
        insert_id = None
    # Add the experiment to the database directly
    else:
        query = 'INSERT INTO experiment (application_name, application_version, input_to_vary, fileset_dir, ' \
                'parameters, results_dir, experiment, number_of_reminders, launch_frequency, user_id, single) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        insert_id = DB.execute(query,
                               (application, version, input_to_vary, fileset_dir, parameters, results_dir, experiment,
                                number_of_reminders, launch_frequency, current_user.id, single_run))
        message = 'Experiment added successfully'
        alert = 'alert-success'
    return message, alert, insert_id


def get_available_applications():
    """Get the list of available applications"""
    query = 'SELECT * FROM application'
    applications = DB.fetch(query)
    return applications


def get_available_versions(application_id):
    """Get the list of available versions"""
    query = 'SELECT * FROM app_version WHERE application_id = %s'
    versions = DB.fetch(query, (application_id,))
    return versions
