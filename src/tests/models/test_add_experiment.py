from models import add_experiment_to_db
from utils.settings import DB

"""
def test_add_experiment_to_db(mocker):

    class MockUser:
        is_authenticated = True
        id = 1
        role = 'admin'

    mocker.patch('flask_login.utils._get_user', return_value=MockUser())

    # Add an experiment to the database
    message, alert, insert_id = add_experiment_to_db('test_application', 'test_version', 'test_input_to_vary',
                                                     'test_fileset_dir', 'test_parameters', 'test_results_dir',
                                                     'test_experiment', 1, 1, True)

    # Check that the experiment was added correctly
    assert message == 'Experiment added successfully'
    assert alert == 'alert-success'
    assert insert_id is not None
    assert DB.fetch('SELECT * FROM EXPERIMENTS WHERE id = %s', [insert_id]) is not None

    # Delete the experiment from the database
    query = 'DELETE FROM EXPERIMENTS WHERE id = %s'
    DB.execute(query, [insert_id])
    # Check that the experiment was deleted correctly
    query = 'SELECT * FROM EXPERIMENTS WHERE id = %s'
    result = DB.fetch(query, [insert_id])
    assert result == []
"""