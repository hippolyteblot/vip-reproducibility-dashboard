from mysql.connector import DatabaseError

from utils.settings import DB
from flask_login import current_user


def get_available_experiments(version_id):
    """Get the available experiments from the database"""
    if version_id is None:
        query = 'SELECT * FROM experiment'
        experiments = DB.fetch(query)
    else:
        query = 'SELECT * FROM experiment WHERE version_id = %s'
        experiments = DB.fetch(query, (version_id,))
    return experiments


def get_experiment_details(exp_id):
    """Get the details of an experiment from the database"""
    query = 'SELECT * FROM experiment WHERE id = %s'
    return DB.fetch_one(query, (exp_id,))


def update_experiment_on_db(exp_id, name, description, inputs, outputs):
    """Update the details of an experiment in the database"""
    try:
        query = ('UPDATE experiment SET name = %s, experiment_description = %s, inputs_description = %s, '
                 'outputs_description = %s WHERE id = %s')
        DB.execute(query, (name, description, inputs, outputs, exp_id))
        return True
    except DatabaseError as e:
        print("Database error:", e)
        return False
    except Exception as e:
        print("An unexpected error occurred:", e)
        return False
