from utils.settings import DB
from flask_login import current_user


def add_experiment_to_db(application: str, version: str, input_to_vary: str, fileset_dir: str, parameters: str,
                         results_dir: str, experiment: str, number_of_reminders: int, launch_frequency: int,
                         single_run: bool):
    """Add an experiment to the database"""
    # Check if the user is logged in
    if not current_user.is_authenticated:
        return 'You are not logged in', 'alert-danger'
    # Get the user id
    user_id = current_user.id
    # Get the user role
    user_role = current_user.role
    # Check if the user is an admin
    if not user_role == 'admin':
        return 'You are not authorized to add an experiment', 'alert-danger'
    # Add the experiment to the database directly
    query = 'INSERT INTO EXPERIMENTS (application_name, application_version, input_to_vary, fileset_dir, parameters, ' \
            'results_dir, experiment, number_of_reminders, launch_frequency, user_id, single) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    DB.execute(query, (application, version, input_to_vary, fileset_dir, parameters, results_dir, experiment,
                       number_of_reminders, launch_frequency, user_id, single_run))
    return 'Experiment added successfully', 'alert-success'
