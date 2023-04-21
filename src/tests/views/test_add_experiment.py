from views.add_experiment import add_experiment


# TODO : Correct this

def test_add_experiment(mocker):
    """Test the add_experiment callback function"""
    class MockUser:
        is_authenticated = True
        id = 1
        role = 'admin'

    class MokeDB:
        def execute(self, query, args):
            pass

    mocker.patch('flask_login.utils._get_user', return_value=MockUser())
    mocker.patch('utils.database_client.DatabaseClient', return_value=MokeDB())  # TODO : Look like this is not working

    # Test the case where the user has not clicked on the button
    alert, alert_type = add_experiment(None, None, None, None, None, None, None, None, None, None, None)
    assert alert == ''
    assert alert_type == ''

    # Test the case where the user has clicked on the button
    alert, alert_type = add_experiment(1, None, None, None, None, None, None, None, None, None, None)
    assert alert == 'Please fill all the fields'
    assert alert_type == 'alert alert-danger'

    # Test the case where the user has clicked on the button and filled in all the fields
    alert, alert_type = add_experiment(1, 'app', 'v1', 'input', 'fileset', 'parameters', 'results', 'exp', 1, 1, True)
    assert alert == 'Experiment added successfully'
    assert alert_type == 'alert alert-success'
