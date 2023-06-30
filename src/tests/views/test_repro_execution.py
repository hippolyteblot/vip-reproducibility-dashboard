import plotly.graph_objects as go
from views.visualize_experiment_cquest import update_chart
from utils.girder_vip_client import GVC

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
