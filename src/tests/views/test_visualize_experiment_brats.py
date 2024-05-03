from unittest.mock import patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from numpy import array_equal

from views.visualize_experiment_brats import update_chart
from utils.settings import GVC

from flask import Flask


@pytest.mark.parametrize(
    "file, expected_groups, title", [
        ('All', 12, 'Significant digits mean per step for each file'),
        ('_rai_n4.nii.gz', 4, 'Significant digits mean per step for file _rai_n4.nii.gz'),
        ('_to_SRI.nii.gz', 4, 'Significant digits mean per step for file _to_SRI.nii.gz'),
    ])
@patch('views.visualize_experiment_brats.get_global_brats_experiment_data')
@patch('views.visualize_experiment_brats.get_experiment_descriptions')
def test_update_chart(mock_get_description, mock_get_data, file, expected_groups, title):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = '/visualize-experiment-brats?id=10'
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'visualize-experiment-brats'

    class MockUser:
        is_authenticated = True
        id = 1
        role = 'admin'

    feather_data = pd.read_feather('src/tests/data/sample_data_exp_brats.feather')

    mock_get_data.return_value = feather_data

    mock_get_description.return_value = {
        'experiment_description': 'Description',
        'inputs_description': 'Inputs',
        'outputs_description': 'Outputs'
    }

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        graph = update_chart(None, file)[0]
        print(graph)
        assert isinstance(graph, go.Figure)
        assert graph.data[0].type == 'box'
        assert len(graph.data) == expected_groups
        assert graph.layout.title.text == title
        assert graph.layout.xaxis.title.text == 'File'
        assert graph.layout.yaxis.title.text == 'Significant digits mean'
