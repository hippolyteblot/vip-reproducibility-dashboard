import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from numpy import array_equal

from views.visualize_experiment_cquest import update_chart
from utils.settings import get_GVC

from flask import Flask


@pytest.fixture(autouse=True)
def mock_database_client(mocker):
    return mocker.patch('models.cquest_utils.get_DB')


# Define the test cases using @pytest.mark.parametrize
@pytest.mark.parametrize(
    "metabolite, signal, wf, expected_groups, title, x_label, y_label, graph_type", [
        ('All', 'All', 'None', 1, 'Comparison of metabolites', 'Metabolite', 'Amplitude', 'box'),
        ('All', 'All', 'Rec021_Vox2_quest2', 2, 'Comparison of metabolites', 'Metabolite', 'Amplitude', 'box'),
        ('All', 'Rec021_Vox2_quest2', 'None', 1, 'Comparison of metabolites', 'Metabolite', 'Amplitude', 'box'),
        ('All', 'Rec021_Vox2_quest2', '2023-03-16_17:07:38', 2, 'Comparison of metabolites', 'Metabolite', 'Amplitude',
         'box'),
        ('PCh', 'All', 'None', 1, 'Comparison of metabolite PCh', 'Signal', 'Amplitude', 'box'),
        ('PCh', 'All', '2023-03-16_17:07:38', 2, 'Comparison of metabolite PCh', 'Signal', 'Amplitude', 'box'),
        ('PCh', 'Rec021_Vox2_quest2', 'None', 1, 'Comparison of metabolite PCh', 'Workflow', 'Amplitude', 'scatter'),
        ('PCh', 'Rec021_Vox2_quest2', '2023-03-16_17:07:38', 2, 'Comparison of metabolite PCh', 'Workflow', 'Amplitude',
         'scatter'),
    ])
@patch('views.visualize_experiment_cquest.get_cquest_experiment_data')
def test_update_chart(mock_get_data, metabolite, signal, wf, expected_groups, title, x_label, y_label,
                      graph_type):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = '/visualize-experiment-cquest?execution_id=5&metabolite_name=All&signal_selected=All&' \
                   'workflow_selected=All&normalization=No'
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'visualize-experiment-cquest'

    feather_data = pd.read_feather('src/tests/data/sample_data_exp_cquest.feather')

    mock_get_data.return_value = feather_data

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        graph = update_chart(None, metabolite, signal, wf, 'No')[0]

        assert isinstance(graph, go.Figure)
        assert graph.data[0].type == graph_type
        assert graph.layout.title.text == title
        assert graph.layout.xaxis.title.text == x_label
        assert graph.layout.yaxis.title.text == y_label

        x_list = []
        for i in graph.data:
            for j in i.x:
                x_list.append(j)
        # make it unique and sort it
        x_list = np.unique(x_list).tolist()
        x_list.sort()
        excepted_x_list = feather_data[x_label].unique().tolist()
        # supress water1, water2, water3, ...
        excepted_x_list = [x for x in excepted_x_list if not x.startswith('water')]
        excepted_x_list.sort()
        assert array_equal(x_list, excepted_x_list)

        y_max = graph.data[0].y.max()
        y_min = graph.data[0].y.min()
        for i in graph.data:
            tmp_max = i.y.max()
            tmp_min = i.y.min()
            if tmp_max > y_max:
                y_max = tmp_max
            if tmp_min < y_min:
                y_min = tmp_min

        y_max_expected = feather_data[y_label].max()
        y_min_expected = feather_data[y_label].min()
        assert y_max <= y_max_expected
        assert y_min >= y_min_expected

        assert len(graph.data) == expected_groups
