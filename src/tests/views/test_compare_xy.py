from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest
from flask import Flask

from views.compare_cquest_xy import update_chart


@pytest.mark.parametrize(
    "aggregate1, aggregate2, title", [
        (None, None, 'Mean of the significant digits mean per step for each file'),
        ('yes', None, 'Mean of the significant digits mean per step for each file'),
        (None, 'yes', 'Mean of the significant digits mean per step for each file'),
        ('yes', 'yes', 'Mean of the significant digits mean per step for each file'),
    ])
@patch('views.compare_xy.read_folder')
@patch('views.compare_xy.read_file_in_folder')
def test_update_chart(mock_get_data, mock_read_folder, aggregate1, aggregate2, title):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = '/compare-11?id1=364e3fe7f3575e60c2775fdf1143b883&id2=3b8384f74837e5ed77bee7b23b7c1a1a'
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-11'

    feather_data = pd.read_feather('src/tests/data/sample_data_file_cquest_cmp.feather')
    folder_feather_data = pd.read_feather('src/tests/data/sample_data_folder_cquest_cmp.feather')

    mock_get_data.return_value = feather_data.copy()
    mock_read_folder.return_value = folder_feather_data.copy()

    ctx = app.test_request_context()

    with ctx:
        ctx.request = MockRequest()
        graph = update_chart('file1', 'file2', aggregate1, aggregate2, 'No')[0]
        assert isinstance(graph, go.Figure)
        assert graph.layout.xaxis.title.text == 'Metabolite'
        assert graph.layout.yaxis.title.text == 'Amplitude'
        print(graph.data)
        assert graph.data[0].name == 'File 1'
        assert graph.data[1].name == 'File 2'
        # count_waters represents the number of metabolites with water that are not taken into account
        count_waters = 3
        if aggregate1:
            # multiply by 4 because there are 4 files in the "folder" (in the mocked data)
            counter_1 = folder_feather_data.shape[0] - count_waters * 4
        else:
            counter_1 = feather_data.shape[0] - count_waters
        if aggregate2:
            counter_2 = folder_feather_data.shape[0] - count_waters * 4
        else:
            counter_2 = feather_data.shape[0] - count_waters

        assert len(graph.data[0].x) == counter_1
        assert len(graph.data[1].x) == counter_2
        assert len(graph.data[0].y) == counter_1
        assert len(graph.data[1].y) == counter_2
