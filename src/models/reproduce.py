import pandas as pd
import plotly.express as px
import os


def get_execution_data(execution_id):
    """Get the data of an execution from database or local file"""
    data = px.data.iris()
    return pd.DataFrame(data)


def get_all_execution_data():
    """Get the data of all executions from database or local file"""
    folder = "src/data/spectro/"
    # print where are positioned the programs
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
        print(subfolder)
        file = os.listdir(folder + "/" + execution_id + "/" + subfolder)[0]
        print(file)
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
    voxels = sorted(voxels, key=lambda k: k['value'])

    groups = data["Group"].unique()
    groups = [{'label': group, 'value': group} for group in groups]
    groups.insert(0, {'label': 'All', 'value': 'All'})

    return metabolites, voxels, groups
