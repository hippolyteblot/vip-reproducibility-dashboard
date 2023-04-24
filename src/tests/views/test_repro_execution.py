import plotly.graph_objects as go
from dash import html, dash_table
from views.repro_execution import update_chart, update_metadata
from utils.settings import GVC

from flask import Flask


def test_update_chart(mocker):
    """Test the update_chart callback function"""

    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = '/repro-execution?execution_id=41'
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'repro-execution'

    class MockUser:
        is_authenticated = True
        id = 1
        role = 'admin'

    mocker.patch('flask_login.utils._get_user', return_value=MockUser())

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        # 1. Test the case where all the metabolites are selected
        metabolite = 'All'
        graph = update_chart(metabolite)
        GVC.clean_user_download_folder(MockUser().id)  # Clean the user download folder to avoid errors

        # test if the graph is a plotly figure
        assert isinstance(graph, go.Figure)
        # test if the graph is a box plot
        assert graph.data[0].type == 'box'
        # test if the graph has the correct title
        assert graph.layout.title.text == 'Comparison of metabolites'
        # test if the graph has the correct labels
        assert graph.layout.xaxis.title.text == 'Metabolite'
        assert graph.layout.yaxis.title.text == 'Amplitude'

        # 2. Test the case where a specific metabolite is selected
        metabolite = 'PCh'
        graph = update_chart(metabolite)
        GVC.clean_user_download_folder(MockUser().id)  # Clean the user download folder to avoid errors
        assert isinstance(graph, go.Figure)

        # test if the graph is a box plot
        assert graph.data[0].type == 'scatter'

        # test if the graph has the correct title
        assert graph.layout.title.text == 'Comparison of metabolite ' + metabolite

        # test if the graph has the correct labels
        assert graph.layout.xaxis.title.text == 'Signal'
        assert graph.layout.yaxis.title.text == 'Amplitude'

def test_update_metadata(mocker):
    """Test the update_metadata callback function"""

    class MockGVC:
        def get_parent_metadata(self, id):
            metadata = [{'key': 'value'}]
            id_list = [1, 2, 3]
            return metadata, id_list

    href = '/repro-execution?execution_id=41'
    mocked_metadata = [{'key': 'value'}]

    mocker.patch('models.reproduce.GVC', MockGVC())

    # 1. Test the case where the user url is correct
    expected = html.Div(
        children=[
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in mocked_metadata[0].keys()],
                data=mocked_metadata,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
        ],
        style={'padding': '10px', 'width': '100%'},
    )
    assert str(update_metadata(href)) == str(expected)

    # 2. Test the case where the user url is not correct
    expected = html.P('No metadata available')
    assert str(update_metadata('')) == str(expected)

