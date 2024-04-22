from unittest.mock import patch

from dash.html import Div
from dash_bootstrap_components import Row, Button

from views.home import toggle_modal_exp, get_list_structure


@patch('views.home.load_exp_from_db')
@patch('views.home.get_available_applications')
def test_toggle_modal_exp(mock_load_exp_from_db, mock_get_available_applications):
    """Test the toggle_modal_exp callback function"""
    mock_load_exp_from_db.return_value = [{'id': 1, 'name': 'app'}]
    mock_get_available_applications.return_value = [{'id': 1, 'application_name': 'exp', 'name': 'exp'}]
    outputs = toggle_modal_exp(0, 0, True)

    # Check the output
    assert outputs[0] is True
    assert outputs[1] == []

    outputs = toggle_modal_exp(1, 0, True)

    # Check the output
    assert outputs[0] is False
    assert not outputs[1] == []


def test_get_list_structure():
    """Test the get_list_structure callback function"""
    data_list = [
        {
            'name': 'elemA',
            'id': '1',
        },
        {
            'name': 'elemB',
            'id': '2',
        },
    ]
    href = '/reproducibility'

    result = Row(
        children=[
            Div(
                [
                    Row(
                        children=[
                            Button(
                                children='elemA',
                                id='repro-execution',
                                className='mr-1',
                                href='/reproducibility?experiment=1',
                                style={'width': 'fit-content'}
                            )
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'}
                    ),
                    Row(
                        children=[
                            Button(
                                children='elemB',
                                id='repro-execution',
                                className='mr-1',
                                href='/reproducibility?experiment=2',
                                style={'width': 'fit-content'}
                            )
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'}
                    )
                ]
            )
        ],
        style={'flexDirection': 'row'})

    outputs = get_list_structure(data_list, href)

    assert str(outputs) == str(result)
