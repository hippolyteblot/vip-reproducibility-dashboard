from unittest.mock import patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from numpy import array_equal

from views.compare_cquest_11 import bind_charts
from utils.settings import GVC

from flask import Flask


@patch('views.compare_exp_cquest.get_cquest_experiment_data')
@patch('models.cquest_utils.get_quest2')
def test_update_chart(mock_get_data, mock_get_cquest_data):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = '/compare-11?id1=de1a3fdf2cd942de466b21ef59b27aa9&id2=a6725471c4f6f9401e91a46bf21b9e8c'
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-11'

    feather_data = pd.read_feather('src/tests/data/sample_data_exp_cquest.feather')

    mock_get_data.return_value = feather_data.copy()
    mock_get_cquest_data.return_value = feather_data.copy()

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        graph = bind_charts(None, 'no')
        assert isinstance(graph, go.Figure)
        assert graph.data[0].type == 'scattergl'
        assert graph.layout.xaxis.title.text == 'Metabolite'
        assert graph.layout.yaxis.title.text == 'Amplitude'
        assert len(graph.data) == 2
