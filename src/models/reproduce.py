import gzip
import shutil
from time import sleep

import imageio
import numpy as np
import pandas as pd
import plotly.express as px
import os

from flask_login import current_user

from utils.settings import GVC, DB
from utils.quest2_reader import get_quest2


def get_execution_data(execution_id):
    """Get the data of an execution from database or local file"""
    data = px.data.iris()
    return pd.DataFrame(data)


def get_all_execution_data():
    """Get the data of all executions from database or local file"""
    folder = "src/data/spectro/"
    data = pd.DataFrame()
    for group in ["A", "B"]:
        for subfolder in os.listdir(folder + group):
            iter = 0
            for subsubfolder in os.listdir(folder + group + "/" + subfolder):
                file = os.listdir(folder + group + "/" + subfolder + "/" + subsubfolder)[0]
                df = pd.read_feather(folder + group + "/" + subfolder + "/" + subsubfolder + "/" + file)
                df["Group"] = group
                # update each value of "Amplitude" to convert something like 1.2e-5 to 0.000012
                df["Amplitude"] = df["Amplitude"].apply(lambda x: float(x))
                # same for SD
                df["SD"] = df["SD"].apply(lambda x: float(x))
                # Same for the signal (from file name)
                df["Signal"] = iter
                exec = file.split("_")[0].split("Rec")[1]
                # parse the string to int
                exec = int(exec)
                df["Execution"] = exec
                # Same for the voxel
                voxel = file.split("_")[1].split(".")[0].split("Vox")[1]
                # parse the string to int
                voxel = int(voxel)
                df["Voxel"] = voxel
                # Same for the

                # concat the dataframes
                data = pd.concat([data, df])
                iter += 1
    # convert the data to a dataframe and save it as feather use .reset_index(drop=True) to remove the index
    # Voxels values are converted to string to avoid Dash to use a gradient color scale
    data["Voxel"] = data["Voxel"].apply(lambda x: str(x))

    data = pd.DataFrame(data)
    data = data.reset_index(drop=True)
    data.to_feather("src/data/execution_data.feather")

    return data


def get_prebuilt_data():
    return pd.read_feather("src/data/execution_data.feather")


def get_execution_data_from_local(execution_id):
    """Get the data of an execution from local file"""
    folder = "src/data/spectro"
    subfolders = os.listdir(folder + "/" + execution_id)
    data = pd.DataFrame()
    iter = 0
    for subfolder in subfolders:
        file = os.listdir(folder + "/" + execution_id + "/" + subfolder)[0]
        df = pd.read_feather(folder + "/" + execution_id + subfolder + "/" + file)
        # update each value of "Amplitude" to convert something like 1.2e-5 to 0.000012
        df["Amplitude"] = df["Amplitude"].apply(lambda x: float(x))
        # same for SD
        df["SD"] = df["SD"].apply(lambda x: float(x))
        # Same for the signal (from file name)
        signal = int(iter)
        df["Signal"] = signal
        # concat the dataframes
        data = pd.concat([data, df])
        iter += 1
    return data


def get_parameters_for_spectro(data):
    metabolites = data["Metabolite"].unique()
    metabolites = [{'label': metabolite, 'value': metabolite} for metabolite in metabolites]
    metabolites.insert(0, {'label': 'All', 'value': 'All'})

    voxels = data["Voxel"].unique()
    voxels = [{'label': str(voxel), 'value': voxel} for voxel in voxels]
    voxels.insert(0, {'label': 'All', 'value': -1})

    groups = data["Group"].unique()
    groups = [{'label': group, 'value': group} for group in groups]
    groups.insert(0, {'label': 'All', 'value': 'All'})

    return metabolites, voxels, groups


def get_data_from_girder(execution_id, user_id):
    """Get the data of an execution from girder"""
    path = GVC.download_experiment_data(execution_id, user_id)
    # wait for the file to be downloaded
    while not os.path.exists(path):
        sleep(0.1)

    data = pd.read_feather(path)
    # parse column Amplitude to float
    data["Amplitude"] = data["Amplitude"].apply(lambda x: float(x))
    # parse column SD to float
    data["SD"] = data["SD"].apply(lambda x: float(x))

    return data


def get_metadata_from_girder(execution_id):
    """Get the metadata of an execution from girder"""
    return GVC.get_parent_metadata(execution_id)


def get_experiment_data(experiment_id):
    """Get the data of an experiment from database or local file"""
    # first, get the girder_id of the folder containing the experiment
    query = "SELECT girder_id FROM experiment WHERE id = %s"
    girder_id = DB.fetch_one(query, (experiment_id,))['girder_id']

    # then, get the data from girder
    path = GVC.download_feather_data(girder_id)
    # while the file is not downloaded, wait
    while not os.path.exists(path):
        sleep(0.1)

    # finally, read the data from the file
    data = pd.read_feather(path)
    # convert field Amplitude and SD to float (they look like 1.2e-5)
    data["Amplitude"] = data["Amplitude"].apply(lambda x: float(x))
    data["SD"] = data["SD"].apply(lambda x: float(x))
    return data


def get_wf_data(wf_id):
    """Get the data of an experiment from database or local file"""
    # first, get the girder_id of the folder containing the experiment
    query = "SELECT girder_id FROM workflow WHERE id = %s"
    girder_id = DB.fetch_one(query, (wf_id,))['girder_id']

    # then, get the data from girder
    path = GVC.download_feather_data(girder_id)
    # while the file is not downloaded, wait
    while not os.path.exists(path):
        sleep(0.1)

    # finally, read the data from the file
    data = pd.read_feather(path)
    # convert field Amplitude and SD to float (they look like 1.2e-5)
    data["Amplitude"] = data["Amplitude"].apply(lambda x: float(x))
    data["SD"] = data["SD"].apply(lambda x: float(x))
    return data


def read_file(file_uuid):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    path = os.path.join("src", "tmp", "user_compare", str(file_uuid) + ".txt")
    data = get_quest2(path)
    return data


def read_file_in_folder(folder, file):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    path = os.path.join("src", "tmp", "user_compare", str(folder), str(file))
    data = get_quest2(path)
    return data


def read_folder(folder):
    """Read all the files in a folder and return a dataframe containing all the data"""
    path = os.path.join("src", "tmp", "user_compare", str(folder))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    data = pd.DataFrame()
    for file in files:
        df = read_file_in_folder(folder, file)
        data = pd.concat([data, df])
    return data


def get_files_in_folder(folder_id):
    """Get the files in a folder from user's folder in local"""
    path = os.path.join("src", "tmp", "user_compare", str(folder_id))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    return files


def read_nii_file(file):
    pass


def get_processed_data_from_niftis(id1, id2, slider_value, axe):
    data1 = "src/tmp/user_compare/" + id1 + ".nii"
    data2 = "src/tmp/user_compare/" + id2 + ".nii"

    vol1 = imageio.volread(data1)
    vol2 = imageio.volread(data2)
    max_vol1 = np.max(vol1)
    max_vol2 = np.max(vol2)

    # build an image using the slider value
    if axe == 'z':
        img_mask1 = vol1[slider_value, :, :]
        img_mask2 = vol2[slider_value, 3:, 5:]
    elif axe == 'y':
        img_mask1 = vol1[:, slider_value, :]
        img_mask2 = vol2[4:, slider_value, 5:]
    else:
        img_mask1 = vol1[:, :, slider_value]
        img_mask2 = vol2[4:, 3:, slider_value]

    img_rgb1 = np.stack([img_mask1 / max_vol1, img_mask1 / max_vol1, img_mask1 / max_vol1], axis=-1)
    img_rgb2 = np.stack([img_mask2 / max_vol2, img_mask2 / max_vol2, img_mask2 / max_vol2], axis=-1)

    axe_index = 2
    if axe == 'y':
        axe_index = 1
    elif axe == 'z':
        axe_index = 0

    return img_rgb1, img_rgb2, vol1.shape[axe_index]


def get_processed_data_from_niftis_folder(folder_id, slider_value, axe, only_mask):
    """Get the data from the niftis folder"""
    path = os.path.join("src", "tmp", "user_compare", str(folder_id))
    files = os.listdir(path)

    # list .nii.gz files
    files = [file for file in files if file.endswith(".nii.gz")]
    # uncompress them
    for file in files:
        with gzip.open(os.path.join(path, file), 'rb') as f_in:
            with open(os.path.join(path, file[:-3]), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(os.path.join(path, file))

    files = os.listdir(path)
    files = [file for file in files if file.endswith(".nii")]
    data = []
    max_vol = 0
    max_value = 0
    for file in files:
        path = "src/tmp/user_compare/" + str(folder_id) + "/" + file
        vol = imageio.volread(path)
        tmp_max = np.max(vol)
        if axe == 'z':
            max_vol = vol.shape[0]
            img_mask = vol[slider_value, :, :]
        elif axe == 'y':
            max_vol = vol.shape[1]
            img_mask = vol[:, slider_value, :]
            tmp_max = np.max(img_mask)
        else:
            max_vol = vol.shape[2]
            img_mask = vol[:, :, slider_value]
            tmp_max = np.max(img_mask)
        if tmp_max > max_value:
            max_value = tmp_max
        data.append(img_mask)

    print("max value: ", max_value)
    # new frame is the mean of all the pixel of the loaded niftis
    new_frame = np.mean(data, axis=0)
    # convert to rgb

    img_rgb = np.stack([(new_frame / max_value) * 255, (new_frame / max_value) * 255, (new_frame / max_value) * 255],
                       axis=-1)

    diff_mask = np.zeros_like(new_frame)

    for i in range(diff_mask.shape[0]):
        for j in range(diff_mask.shape[1]):
            values = []
            for k in range(len(data)):
                values.append(data[k][i, j])
            unique = np.unique(values)
            diff_mask[i, j] = (len(unique) - 1) * 4

    diff_mask /= len(data)
    diff_mask /= max_value
    diff_mask *= 255
    diff_mask = np.stack([diff_mask, np.zeros(diff_mask.shape), np.zeros(diff_mask.shape)], axis=-1)

    if only_mask:
        img_rgb = diff_mask
    else:
        img_rgb += diff_mask

    img_rgb = np.clip(img_rgb, 0, 255)

    return img_rgb, max_vol


def build_difference_image(img_rgb1, img_rgb2):
    min_shape0 = min(img_rgb1.shape[0], img_rgb2.shape[0])
    min_shape1 = min(img_rgb1.shape[1], img_rgb2.shape[1])
    img_mask3 = np.zeros(img_rgb1.shape)
    for i in range(min_shape0):
        for j in range(min_shape1):
            if img_rgb1[i, j, 0] == img_rgb2[i, j, 0]:
                img_mask3[i, j] = img_rgb1[i, j]
            else:
                img_mask3[i, j] = [255, 0, 0]

    return img_mask3
