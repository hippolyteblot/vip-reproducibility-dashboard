from time import sleep

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


def read_user_file(file_uuid):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    user_id = current_user.id
    path = os.path.join("src", "tmp", "user_compare", str(user_id), str(file_uuid) + ".txt")
    data = get_quest2(path)
    return data


def read_user_folder(folder, file):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    user_id = current_user.id
    path = os.path.join("src", "tmp", "user_compare", str(user_id), str(folder), str(file))
    data = get_quest2(path)
    return data


def get_files_in_folder(folder_id):
    """Get the files in a folder from user's folder in local"""
    user_id = current_user.id
    path = os.path.join("src", "tmp", "user_compare", str(user_id), str(folder_id))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    return files
