"""
This file contains the functions used to compare niftis files and more generally to compare the results of BraTS
"""
import base64
import gzip
import math
import os
import shutil
from plotly import express as px
from time import sleep

import cv2
import imageio
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity

from models.home import save_file_for_comparison
from utils.settings import GVC
from utils.settings import DB, CACHE_FOLDER


def uncompress_nifti_files(folder_path):
    """Uncompresses .nii.gz files in the given folder."""
    files = [file for file in os.listdir(folder_path) if file.endswith(".nii.gz")]

    for file in files:
        with gzip.open(os.path.join(folder_path, file), 'rb') as f_in:
            with open(os.path.join(folder_path, file[:-3]), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(os.path.join(folder_path, file))


def get_nifti_files(folder_path):
    """Returns a list of .nii files in the given folder."""
    return [file for file in os.listdir(folder_path) if file.endswith(".nii")]


def read_nifti_volume(file_path):
    """Reads the NIfTI volume from the given file path."""
    return imageio.volread(file_path)


def extract_image_slice(vol, slider_value, axe):
    """Extracts a 2D image slice based on the specified axis and slider value."""
    if axe == 'z':
        return vol[slider_value, :, :]
    if axe == 'y':
        return vol[:, slider_value, :]
    return vol[:, :, slider_value]


def process_image_slices(files, folder_id, axe, slider_value):
    """Processes the image slices and returns a list of images and the maximum volume."""
    data = []
    max_value = 0
    max_vol = 0

    for file in files:
        file_path = os.path.join(CACHE_FOLDER, "user_compare", str(folder_id), file)
        vol = read_nifti_volume(file_path)
        img_mask = extract_image_slice(vol, slider_value, axe)
        tmp_max = np.max(img_mask)

        if tmp_max > max_value:
            max_value = tmp_max

        data.append(img_mask)

        if axe == 'z':
            max_vol = vol.shape[0]
        elif axe == 'y':
            max_vol = vol.shape[1]
        else:
            max_vol = vol.shape[2]

    return data, max_value, max_vol


def calculate_new_frame(data, max_value):
    """Calculates the new frame as the mean of all pixel values."""
    new_frame = np.mean(data, axis=0)
    img_rgb = np.stack([(new_frame / max_value) * 255, (new_frame / max_value) * 255, (new_frame / max_value) * 255],
                       axis=-1)
    return img_rgb


def calculate_diff_mask(data, max_value):
    """Calculates the difference mask based on the input data."""
    diff_mask = np.zeros_like(data[0])

    for i in range(diff_mask.shape[0]):
        for j in range(diff_mask.shape[1]):
            values = [data[k][i, j] for k in range(len(data))]
            unique = np.unique(values)
            diff_mask[i, j] = (len(unique) - 1) * 4

    diff_mask /= len(data)
    diff_mask /= max_value
    diff_mask *= 255

    return np.stack([diff_mask, np.zeros(diff_mask.shape), np.zeros(diff_mask.shape)], axis=-1)


def get_processed_data_from_niftis_folder(folder_id, slider_value, axe, only_mask):
    """Get the processed data from the NIfTI folder."""
    path = os.path.join(CACHE_FOLDER, "user_compare", str(folder_id))

    # Uncompress NIfTI files
    uncompress_nifti_files(path)

    # Get list of .nii files
    files = get_nifti_files(path)

    # Process image slices
    data, max_value, max_vol = process_image_slices(files, folder_id, axe, slider_value)

    if max_value == 0:
        max_value = 1

    # Calculate new frame
    img_rgb = calculate_new_frame(data, max_value)

    # Calculate difference mask
    diff_mask = calculate_diff_mask(data, max_value)

    if only_mask:
        img_rgb = diff_mask
    else:
        img_rgb += diff_mask

    img_rgb = np.clip(img_rgb, 0, 255)
    return img_rgb, max_vol


# Tested
def build_difference_image(img_rgb1: np.ndarray, img_rgb2: np.ndarray, tolerance: float = 0.0) -> np.ndarray:
    """Build the difference image using the absolute difference"""
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


# Tested
def equal_with_tolerance(val1: int or float, val2: int or float, tolerance: float) -> bool:
    """Check if two values are equal with a tolerance"""
    value = abs(val1 - val2)
    # round to the same number of decimals as the tolerance
    if tolerance != 0:
        value = round(value, int(math.log10(1 / tolerance)))
    return value <= tolerance


def get_global_brats_experiment_data(experiment_id: int) -> pd.DataFrame and list:
    """Get the data of a brats experiment from database or local file"""
    # first, get the girder_id of the folder containing the experiment
    query = "SELECT girder_id FROM experiment WHERE id = %s"
    girder_id = DB.fetch_one(query, (experiment_id,))['girder_id']

    # then, get the data from girder
    path = GVC.download_feather_data(girder_id)

    # while the file is not downloaded, wait
    while not os.path.exists(path):
        sleep(0.1)

    data = pd.read_feather(path)

    return data


def download_brats_file(execution_number, file, patient_id, experiment_id):
    """Download a file from a brats experiment"""
    # This function finds in the database the girder_id of the file to download
    # and downloads it in the tmp folder
    query = "SELECT id FROM workflow WHERE experiment_id = %s and timestamp = %s"
    workflow_id = DB.fetch_one(query, (experiment_id, execution_number))['id']
    query = "SELECT girder_id FROM output WHERE workflow_id = %s AND name = %s"
    girder_id = DB.fetch_one(query, (workflow_id, patient_id))['girder_id']
    path = GVC.download_file_by_name(girder_id, file + ".nii.gz")
    while not os.path.exists(path):
        sleep(0.01)

    # read the file and get the data as b64
    with open(path, "rb") as f:
        data = f.read()

    data = base64.b64encode(data).decode('utf-8')

    md5 = save_file_for_comparison(data, patient_id + ".nii.gz")
    return md5


def build_difference_image_ssim(img1: any, img2: any, k1: float = 0.01, k2: float = 0.03, sigma: float = 1.5) -> \
        np.ndarray and float:
    """Build the difference image using the structural similarity index"""
    (score, diff) = structural_similarity(img1, img2, full=True, K1=k1, K2=k2, data_range=550,
                                          gaussian_weights=True, sigma=sigma, use_sample_covariance=False,
                                          multichannel=True)
    diff = (diff * 255).astype("uint8")

    heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)

    # convert to grayscale
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY)

    return heatmap, score


# Tested
def compute_psnr(array1: np.ndarray, array2: np.ndarray, authorize_str=True) -> float or str:
    """Compute the PSNR between two arrays"""
    img1 = array1.astype(np.float64) / 255.
    img2 = array2.astype(np.float64) / 255.
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        if authorize_str:
            return "Infinite"
        return np.inf
    return 10 * math.log10(1. / mse)


# Tested
def compute_psnr_foreach_slice(array1: np.ndarray, array2: np.ndarray, axe: str) -> np.ndarray:
    """Compute the PSNR for each slice of the given axe"""
    if axe == 'z':
        slices = array1.shape[0]
    elif axe == 'y':
        slices = array1.shape[1]
    elif axe == 'x':
        slices = array1.shape[2]
    else:
        raise ValueError("axe must be z, y or x")

    psnr = np.zeros(slices)
    for i in range(slices):
        if axe == 'z':
            psnr[i] = compute_psnr(array1[i, :, :], array2[i, :, :], authorize_str=False)
        elif axe == 'y':
            psnr[i] = compute_psnr(array1[:, i, :], array2[:, i, :], authorize_str=False)
        elif axe == 'x':
            psnr[i] = compute_psnr(array1[:, :, i], array2[:, :, i], authorize_str=False)
    return psnr


def get_processed_data_from_niftis(id1: str, id2: str, axe: str, slider_value: int) -> (np.ndarray and np.ndarray and
                                                                                        int and imageio.core.util.Image
                                                                                        and imageio.core.util.Image):
    """Get the data from the niftis files in the cache folder"""
    data1 = CACHE_FOLDER + "/user_compare/" + id1 + ".nii"
    data2 = CACHE_FOLDER + "/user_compare/" + id2 + ".nii"

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

    # maximum is the max value between img_mask1 and img_mask2
    maximums = [img_mask1.max(), img_mask2.max(), img_mask1.min(), img_mask2.min()]
    maximum = max(maximums)

    max_slide = vol1.shape[axe_index]
    if max_slide > vol2.shape[axe_index]:
        max_slide = vol2.shape[axe_index]

    return img_mask1, img_mask2, max_slide-1, vol1, vol2, maximum

def create_box_plot(sorted_experiments, unique_file=False):
    """Create a box plot with the given data"""
    if unique_file:
        title = f"Significant digits mean per step for file {sorted_experiments['File'].iloc[0]}"
    else:
        title = "Significant digits mean per step for each file"
    figure = px.box(sorted_experiments, x="File", y="Mean_sigdigits",
                    title=title, color='Experiment')
    figure.update_layout(
        xaxis_title="File",
        yaxis_title="Significant digits mean",
        legend_title="Patient",
    )

    return figure

def sort_experiment_data(experiment_data1, experiment_data2):
    """Sort the experiment data by file"""
    sorted_experiments = pd.DataFrame()
    files_to_check = ['_raw.nii.gz', '_rai.nii.gz', '_rai_n4.nii.gz', '_to_SRI.nii.gz', '_to_SRI_brain.nii.gz']

    dfs_to_concat = []

    for file_to_check in files_to_check:
        for _, row in experiment_data1.iterrows():
            if file_to_check in row['File']:
                dfs_to_concat.append(row)

        for _, row in experiment_data2.iterrows():
            if file_to_check in row['File']:
                dfs_to_concat.append(row)

    if dfs_to_concat:
        sorted_experiments = pd.concat(dfs_to_concat, axis=1).T

    sorted_experiments.reset_index(drop=True, inplace=True)

    return sorted_experiments


def get_experiment_data(exec_id, file):
    """Get the data of a brats experiment from database or local file"""
    experiment_data = get_global_brats_experiment_data(exec_id)
    files = experiment_data['File'].unique().tolist()
    if file != 'All':
        experiment_data = experiment_data[experiment_data['File'] == file]

    experiment_data = experiment_data[~experiment_data['File'].str.contains('T1CE')]

    return experiment_data, files

def build_gradient(psnr_values):
    """Build the gradient for the psnr values to indicate where the differences are"""
    minimum = min(psnr_values)
    # for each psnr value, add a color to the gradient
    gradient = 'linear-gradient(to right, '
    for i in range(psnr_values.size):
        if psnr_values[i] == np.inf:
            value = 0
        else:
            value = 1 - ((psnr_values[i] - (minimum * 0.8)) * 0.05)
        gradient += f'rgba(255, 0, 0, {value}) '
        if i != psnr_values.size - 1:
            gradient += ', '
    gradient += ')'
    return gradient
