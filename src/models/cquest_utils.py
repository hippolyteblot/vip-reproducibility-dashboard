"""
Provide functions to work with cquest data.
"""
import os
from time import sleep

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import html
from pandas import DataFrame

from utils.settings import GVC
from utils.quest2_reader import get_quest2
from utils.settings import DB


def get_cquest_experiment_data(experiment_id: int) -> pd.DataFrame:
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
    data["Amplitude"] = data["Amplitude"].apply(float)
    data["SD"] = data["SD"].apply(float)
    return data


def read_cquest_file(file_uuid: str) -> DataFrame:
    """Read the file uploaded by the user using the uuid and return a dataframe"""
    path = os.path.join("src", "tmp", "user_compare", str(file_uuid) + ".txt")
    data = get_quest2(path)
    return data


def get_metadata_cquest(exp_id: int) -> list:
    """Get the metadata of an experiment from database"""
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


def get_files_in_folder(folder_id):
    """Get the files in a folder from user's folder in local"""
    path = os.path.join("src", "tmp", "user_compare", str(folder_id))
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".txt")]
    return files


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
    data.reset_index(drop=True, inplace=True)
    return data


def normalize(data):
    """Normalize the data using the formula : (x - mean) / std"""
    data['Amplitude'] = pd.to_numeric(data['Amplitude'], errors='coerce')
    data.dropna(subset=['Amplitude'], inplace=True)

    means = data.groupby('Metabolite')['Amplitude'].transform('mean')
    stds = data.groupby('Metabolite')['Amplitude'].transform('std')

    data['Amplitude'] = (data['Amplitude'] - means) / stds


def filter_and_normalize_data(wf_data, signal, normalization):
    """Filter the data and normalize it if needed"""
    wf_data = wf_data.sort_values(by=['Metabolite'])
    wf_data = wf_data[~wf_data['Metabolite'].str.contains('water')]

    if normalization == 'Yes':
        normalize(wf_data)

    if signal != 'All':
        wf_data = wf_data[wf_data['Signal'] == signal]

    return wf_data


def get_description_and_label(signal, workflow, metabolite):
    """Get the description and the label of the chart depending on the signal, workflow and metabolite"""
    description = ''
    if signal != 'All':
        label = 'Workflow to highlight'
        description = (f"This chart shows the amplitude of the signal {signal} for each metabolite. Results are "
                       f"computed by cQUEST and their provenance is shown in the table below.")
    else:
        label = 'Signal to highlight'
        if workflow == 'None' and metabolite == 'All':
            label = 'Signal to highlight'
            description = ("This chart shows the amplitude of each signal for each metabolite. Results are computed by "
                           "cQUEST and their provenance is shown in the table below.")

    return label, description


def create_workflow_group_column(wf_data, workflow):
    """Create a column 'Workflow group' with the value of workflow"""
    wf_data['Workflow group'] = wf_data['Workflow'].apply(
        lambda x: str(workflow) if x == workflow else 'Other'
    )


def create_signal_group_column(wf_data, signal):
    """Create a column 'Signal group' with the value of signal"""
    wf_data['Signal group'] = np.where(wf_data['Signal'] == signal, signal, 'Other')


def generate_box_plot(wf_data: pd.DataFrame, x_column, y_column, title, color_column=None):
    """Generate a box plot with the data"""
    # if there is less than 4 values per column, we use a scatter plot
    if wf_data.groupby(x_column).count()[y_column].max() < 4:
        graph = px.scatter(
            x=wf_data[x_column],
            y=wf_data[y_column],
            title=title,
            labels={'x': x_column, 'y': y_column},
            data_frame=wf_data,
            hover_data=['Signal'],
            color=wf_data[color_column] if color_column is not None else None,
        )
        return graph
    if color_column is not None:
        wf_data = wf_data.sort_values(by=[x_column, color_column])
    graph = px.box(
        x=wf_data[x_column],
        y=wf_data[y_column],
        title=title,
        labels={'x': x_column, 'y': y_column},
        data_frame=wf_data,
        hover_data=['Signal'],
        color=wf_data[color_column] if color_column is not None else None,
    )

    return graph


def filter_and_get_unique_values(wf_data):
    """Filter the data and get the unique values of metabolites and signals"""
    metabolites = wf_data['Metabolite'].unique()
    metabolites = [metabolite for metabolite in metabolites if 'water' not in metabolite]
    signals = wf_data['Signal'].unique()
    return metabolites, signals


def create_dropdown_options(values, all_label):
    """Create the options for a dropdown"""
    options = [{'label': str(value), 'value': value} for value in values]
    options.sort(key=lambda x: x['label'])
    options.insert(0, {'label': all_label, 'value': all_label})
    return options


def create_metadata_structure(metadata):
    """Create a table with the metadata of the experiment"""
    metadata_structure = [
        dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th('Signal'),
                            html.Th('Input name'),
                            html.Th('Outputs name'),
                            html.Th('Outputs number'),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(i),
                                html.Td(metadata[i]['input_name']),
                                html.Td(metadata[i]['output_name']),
                                html.Td(metadata[i]['count']),
                            ]
                        )
                        for i in range(len(metadata))
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
        )
    ]
    return metadata_structure


def preprocess_cquest_data_compare(data1, data2):
    """Preprocess the data for the comparison"""
    data1 = data1[~data1['Metabolite'].str.contains('water')].copy()
    data2 = data2[~data2['Metabolite'].str.contains('water')].copy()

    data1['Amplitude'] = data1['Amplitude'].apply(float)
    data2['Amplitude'] = data2['Amplitude'].apply(float)

    data1['File'] = 'File 1'
    data2['File'] = 'File 2'

    return data1, data2

def generate_url(wf_id, metabolite_name, signal_selected, workflow_selected, normalization='Yes'):
    """Generate the url to be used in the callback"""
    url = "?execution_id=" + str(wf_id) + "&metabolite_name=" + str(metabolite_name) + "&signal_selected=" + \
          str(signal_selected) + "&workflow_selected=" + str(workflow_selected) + "&normalization=" + \
          str(normalization)
    return url
