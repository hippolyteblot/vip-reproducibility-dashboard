from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest
from flask import Flask

from views.compare_exp_cquest import update_exp_chart_bland_altman


@pytest.mark.parametrize(
    'graph_type, expected_graph_type, signal, x_label, y_label', [
        ('bland-altman', 'scatter', 'Rec021_Vox2_quest2', 'Mean', 'Difference'),
        ('box', 'box', 'Rec021_Vox2_quest2', 'Signal', 'Amplitude'),
    ])
@patch('views.compare_exp_cquest.get_cquest_experiment_data')
def test_update_chart(mock_get_data, graph_type, expected_graph_type, signal, x_label, y_label):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = ('/compare-exp-cquest?exp1=6&exp2=7&metabolite_name=PCh&signal_selected=Rec021_Vox2_quest2&'
                    'normalization=False&graph_type=bland-altman')
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-exp-cquest'

    feather_data = pd.read_feather('src/tests/data/sample_data_exp_cquest_cmp.feather')

    mock_get_data.return_value = feather_data.copy()

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        graph = update_exp_chart_bland_altman(None, 'PCh', signal,
                                              'None', graph_type)[0]
        assert isinstance(graph, go.Figure)
        assert graph.data[0].type == expected_graph_type
        assert graph.layout.xaxis.title.text == x_label
        assert graph.layout.yaxis.title.text == y_label
