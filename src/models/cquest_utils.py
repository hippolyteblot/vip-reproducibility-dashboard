import os
from time import sleep

import pandas as pd

from utils.quest2_reader import get_quest2
from utils.settings import GVC, DB


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


def get_cquest_data_from_girder(execution_id, user_id):
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


def get_cquest_experiment_data(experiment_id):
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


def read_cquest_file(file_uuid):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    path = os.path.join("src", "tmp", "user_compare", str(file_uuid) + ".txt")
    data = get_quest2(path)
    return data


def read_cquest_file_in_folder(folder, file):
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    path = os.path.join("src", "tmp", "user_compare", str(folder), str(file))
    data = get_quest2(path)
    return data


def read_cquest_folder(folder):
    """Read all the files in a folder and return a dataframe containing all the data"""
    path = os.path.join("src", "tmp", "user_compare", str(folder))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    data = pd.DataFrame()
    for file in files:
        df = read_cquest_file_in_folder(folder, file)
        data = pd.concat([data, df])
    return data


def get_txt_files_in_folder(folder_id):
    """Get the txt files in a folder from user's folder in local"""
    path = os.path.join("src", "tmp", "user_compare", str(folder_id))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    return files



def get_metadata_cquest(exp_id):
    query = "SELECT id FROM workflow WHERE experiment_id = %s"
    wf_ids = DB.fetch(query, (exp_id,))
    array_wf_ids = [wf_ids[i]['id'] for i in range(len(wf_ids))]

    query = "SELECT input.name as input_name, output.name as output_name, count(output.id) as count " \
            "FROM output INNER JOIN input ON output.input_id = input.id " \
            "WHERE output.workflow_id = %s "
    for i in range(len(wf_ids) - 1):
        query += "OR output.workflow_id = %s "
    query += "GROUP BY input.name, output.name ORDER BY input.name, output.name"

    outputs = DB.fetch(query, array_wf_ids)

    # Return an array of metadata with every output with their name and their id and their input (also with name and id)
    metadata = []
    for output in outputs:
        metadata.append({'input_name': output['input_name'], 'output_name': output['output_name'],
                         'count': output['count']})
    return metadata