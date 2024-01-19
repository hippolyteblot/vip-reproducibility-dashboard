from unittest.mock import patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from numpy import array_equal
import imageio

from views.compare_nii_11 import show_frames, build_gradient, update_one_time
from utils.settings import GVC

from flask import Flask


@pytest.mark.parametrize("index_slider, mode, axe, expected_psnr_slice, expected_ssim, k1, k2, sigma", [
    (0, 'pixel', 'x', 36.9229, 0.9999999999999999, 0.001, 1, 1),
    (100, 'pixel', 'y', 27.2858, 0.9999999999999999, 0.001, 1, 1),
    (0, 'pixel', 'z', 36.9229, 0.9999999999999999, 0.001, 1, 1),
    (120, 'pixel', 'x', 26.7964, 0.9999999999999999, 0.001, 1, 1),
    (150, 'ssim', 'x', 'Infinite', 0.9986, 0.25, 0.9, 0.6),
    (40, 'ssim', 'z', 25.9824, 0.9592, 0.75, 0.01, 1)
])
@patch('views.compare_nii_11.get_processed_data_from_niftis')
def test_update_chart(mock_get_data, index_slider, mode, axe, expected_psnr_slice, expected_ssim, k1, k2, sigma):
    # Configuration of the environment
    app = Flask(__name__)

    class MockRequest:
        referrer = ('/compare-nii-11?id1=c153e123fb89cf4c73aad014ebb60889&id2=03098b59da9df1edc0f20604ff97b9d2&axe=z&'
                    'mode=pixel&slice=138&K1=0.001&K2=1&sigma=1&colorscale=abs')
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-11'

    mock_get_data.return_value = get_processed_data_from_niftis(axe, index_slider)

    ctx = app.test_request_context()

    with (ctx):
        ctx.request = MockRequest()
        img_1, img_cmp, img2, min_slider, min_slider, value_slider, param_ssim, value_ssim, psnr_slice, description, url = show_frames(
            index_slider, axe, mode, k1, k2, sigma, 'abs')
        if mode == 'ssim':
            assert value_ssim == expected_ssim
        assert isinstance(img_1, go.Figure)
        assert isinstance(img_cmp, go.Figure)
        assert isinstance(img2, go.Figure)
        assert isinstance(min_slider, int)
        assert isinstance(min_slider, int)
        assert isinstance(value_slider, int)
        assert isinstance(param_ssim, dict)
        assert isinstance(value_ssim, int | float)
        assert psnr_slice == expected_psnr_slice
        assert isinstance(psnr_slice, float | str)
        assert isinstance(description, str)
        assert isinstance(url, str)


@pytest.mark.parametrize("axe, slider_value, nb_colors", [
    ('x', 0, 241),
    ('y', 100, 241),
    ('z', 0, 156),
    ('x', 120, 241),
    ('x', 150, 241),
    ('z', 40, 156)
])
@patch('views.compare_nii_11.get_processed_data_from_niftis')
def test_update_one_time(mock_get_data, axe, slider_value, nb_colors):
    app = Flask(__name__)

    class MockRequest:
        referrer = ('/compare-nii-11?id1=c153e123fb89cf4c73aad014ebb60889&id2=03098b59da9df1edc0f20604ff97b9d2&axe=z&'
                    'mode=pixel&slice=138&K1=0.001&K2=1&sigma=1&colorscale=abs')
        environ = {'HTTP_HOST': 'localhost'}
        blueprints = 'compare-11'

    mock_get_data.return_value = get_processed_data_from_niftis(axe, slider_value)

    ctx = app.test_request_context()

    with (ctx):
        ctx.request = MockRequest()
        gradient, vol_psnr = update_one_time(1, axe, slider_value)
        assert isinstance(gradient, dict)
        assert isinstance(vol_psnr, float)
        assert len(gradient) == 4
        assert len(gradient['background'].split('rgb')) == nb_colors
        assert vol_psnr == 27.7729


@pytest.mark.parametrize("psnr_values", [
    (np.array([0, 0, 0, 0, 0])),
    (np.array([np.inf, np.inf, np.inf, np.inf, np.inf])),
    (np.array(([0, np.inf, 0, np.inf, 0]))),
])
def test_build_gradient(psnr_values):
    gradient = build_gradient(psnr_values)
    assert isinstance(gradient, str)
    assert len(gradient.split('rgb')) == len(psnr_values) + 1


def get_processed_data_from_niftis(axe: str, slider_value: int) -> np.ndarray and np.ndarray and \
                                                                   int and imageio.core.util.Image and imageio.core.util.Image:
    data1 = "src/tests/data/03098b59da9df1edc0f20604ff97b9d2.nii"
    data2 = "src/tests/data/c153e123fb89cf4c73aad014ebb60889.nii"

    vol1 = imageio.volread(data1)
    vol2 = imageio.volread(data2)

    np.max(vol1)
    np.max(vol2)

    # build an image using the slider value
    if axe == 'z':
        img_mask1 = vol1[slider_value, :, :]
        img_mask2 = vol2[slider_value, :, :]
    elif axe == 'y':
        img_mask1 = vol1[:, slider_value, :]
        img_mask2 = vol2[:, slider_value, :]
    else:
        img_mask1 = vol1[:, :, slider_value]
        img_mask2 = vol2[:, :, slider_value]

    axe_index = 2
    if axe == 'y':
        axe_index = 1
    elif axe == 'z':
        axe_index = 0

    maximum = 0
    maximums = [img_mask1.max(), img_mask2.max(), img_mask1.min(), img_mask2.min()]
    for i in maximums:
        if maximum < i:
            maximum = i

    return img_mask1, img_mask2, vol1.shape[axe_index], vol1, vol2, maximum
