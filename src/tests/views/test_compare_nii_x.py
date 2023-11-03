from unittest.mock import patch

import numpy as np
import plotly.graph_objects as go
import pytest

from views.compare_nii_x import show_frames

from flask import Flask


@pytest.mark.parametrize(
    "max_slice, slider_value, axe",
    [
        (240, 0, 'x'),
        (240, 100, 'x'),
        (155, 50, 'z'),
        (240, 0, 'y'),
        (240, 100, 'y'),
        (155, 200, 'z')
    ]
)
@patch('views.compare_nii_x.get_processed_data_from_niftis_folder')
def test_update_chart(mock_get_data, max_slice, slider_value, axe):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = ('/compare-nii-11?id1=c153e123fb89cf4c73aad014ebb60889&id2=03098b59da9df1edc0f20604ff97b9d2&axe=z&'
                    'mode=pixel&slice=138&K1=0.001&K2=1&sigma=1&colorscale=abs')
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-11'

    diff_matrix = np.load('src/tests/data/diff_matrix.npy')

    mock_get_data.return_value = [diff_matrix, max_slice]

    ctx = app.test_request_context()

    with (ctx):
        ctx.request = MockRequest()
        graph, min_slider, max_slider, value_slider = show_frames(slider_value, axe, 'no')
        assert isinstance(graph, go.Figure)
        assert isinstance(min_slider, int)
        assert isinstance(max_slider, int)
        assert isinstance(value_slider, int)
        assert min_slider == 0
        assert max_slider == max_slice
        if slider_value > max_slice:
            assert value_slider == max_slice
        else:
            assert value_slider == slider_value
