from unittest.mock import MagicMock

import numpy as np
import pytest

from utils.settings import DB, GVC
from models import brats_utils


@pytest.fixture
def mock_database():
    mock_db = MagicMock(spec=DB)
    return mock_db


@pytest.fixture
def mock_girder_client():
    mock_girder_client = MagicMock(spec=GVC)
    return mock_girder_client


def test_compute_psnr_foreach_slice(mock_database):
    """Test the add_experiment_to_db function"""
    array1 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    array2 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])

    axe = 'z'
    psnr = brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    assert np.array_equal(psnr, np.array([np.inf, np.inf, np.inf]))
    axe = 'y'
    psnr = brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    assert np.array_equal(psnr, np.array([np.inf, np.inf, np.inf]))
    axe = 'x'
    psnr = brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    assert np.array_equal(psnr, np.array([np.inf, np.inf, np.inf]))
    axe = 'a'
    with pytest.raises(ValueError):
        brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    array1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    array2 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    axe = 'z'
    with pytest.raises(IndexError):
        brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    array1 = np.array([[[9, 8, 7], [6, 5, 4], [3, 2, 1]],
                       [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
                       [[9, 8, 7], [6, 5, 4], [3, 2, 1]]])
    array2 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    axe = 'z'
    psnr = brats_utils.compute_psnr_foreach_slice(array1, array2, axe)
    psnr = np.round(psnr, 8)
    assert np.array_equal(psnr, np.array([33.87111629, 33.87111629, 33.87111629]))


def test_compute_psnr():
    array1 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    array2 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    psnr = brats_utils.compute_psnr(array1, array2, authorize_str=False)
    assert psnr == np.inf
    psnr = brats_utils.compute_psnr(array1, array2, authorize_str=True)
    assert psnr == 'Infinite'
    array1 = np.array([[[9, 8, 7], [6, 5, 4], [3, 2, 1]],
                       [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
                       [[9, 8, 7], [6, 5, 4], [3, 2, 1]]])
    array2 = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                       [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    psnr = brats_utils.compute_psnr(array1, array2)
    assert psnr == 33.87111628595629


def test_equal_with_tolerance():
    val1 = 1
    val2 = 1
    tolerance = 0.1
    assert brats_utils.equal_with_tolerance(val1, val2, tolerance)
    val1 = 1
    val2 = 1.1
    tolerance = 0.1
    assert brats_utils.equal_with_tolerance(val1, val2, tolerance)
    val1 = 1
    val2 = 1.1
    tolerance = 0.05
    assert not brats_utils.equal_with_tolerance(val1, val2, tolerance)


""" Write a test for this function :
def build_difference_image(img_rgb1: np.ndarray, img_rgb2: np.ndarray, tolerance: float = 0.0) -> np.ndarray:
    min_shape0 = min(img_rgb1.shape[0], img_rgb2.shape[0])
    min_shape1 = min(img_rgb1.shape[1], img_rgb2.shape[1])
    img_mask3 = np.zeros(img_rgb1.shape)
    for i in range(min_shape0):
        for j in range(min_shape1):
            if equal_with_tolerance(img_rgb1[i, j], img_rgb2[i, j], tolerance):
                # img_mask3[i, j] = img_rgb1[i, j]
                img_mask3[i, j] = 0
            else:
                # absolute difference
                img_mask3[i, j] = (img_rgb1[i, j] - img_rgb2[i, j])

    return img_mask3
    """


def test_build_difference_image():
    image1 = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]])
    image2 = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]])
    image3 = brats_utils.build_difference_image(image1, image2)
    assert np.array_equal(image3, np.zeros(image1.shape))
    image1 = np.array([
        [9, 2, 3],
        [4, 5, 6],
        [7, 8, 9]])
    result = np.array([
        [8, 0, 0],
        [0, 0, 0],
        [0, 0, 0]])
    image3 = brats_utils.build_difference_image(image1, image2)
    assert np.array_equal(image3, result)
