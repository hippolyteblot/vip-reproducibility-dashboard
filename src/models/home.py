"""
Home page model
"""
import gzip
import hashlib
import io
import os
import base64
import shutil
import zipfile
from dash import html
import dash_bootstrap_components as dbc

from utils.settings import get_DB, CACHE_FOLDER


def load_exec_from_local() -> list:
    """Load the executions from the local folder"""
    folder = "src/data/spectro/"
    exec_list = []
    for group in ["A", "B"]:
        for subfolder in os.listdir(folder + group):
            voxel = subfolder.split("_Vox")[1]
            exec_number = int(subfolder.split("_")[0].split("Rec")[1])

            execution = {
                "path": group + "/" + subfolder + "/",
                "name": "parameters " + group + ", voxel " + voxel + ", execution " + str(exec_number)
            }
            exec_list.append(execution)
    return exec_list


def load_exp_from_db():
    """Load the experiments from the local folder"""
    # query = 'SELECT * FROM EXPERIMENTS INNER JOIN USERS U ON EXPERIMENTS.user_id = U.id WHERE EXPERIMENTS.single = 0'
    # return build_json_from_db(query)
    query = 'SELECT *, application.name as application_name, experiment.id as experiment_id, ' \
            'experiment.name as experiment_name, version_id as version_id ' \
            'FROM experiment ' \
            'INNER JOIN app_version ON experiment.version_id = app_version.id ' \
            'INNER JOIN application ON app_version.application_id = application.id'
    return build_json_from_db2(query)


def build_json_from_db(query):
    """Build the json from the database"""
    DB = get_DB()
    results = DB.fetch(query)
    exp_list = []
    for result in results:
        exp_list.append({
            "id": result.get("id"),
            "name": result.get("application_name") + " " + result.get("application_version") + " "
                    + "(par : " + result.get("username") + ")",
        })
    return exp_list


def build_json_from_db2(query):
    """Build the json from the database"""
    DB = get_DB()
    results = DB.fetch(query)
    exp_list = []
    for result in results:
        exp_list.append({
            "id": result.get("experiment_id"),
            "name": result.get("experiment_name"),
            "application_name": result.get("application_name"),
            "application_version": result.get("number"),
            "application_id": result.get("application_id"),
            "version_id": result.get("version_id"),
        })
    return exp_list


def get_available_applications():
    """Get the available applications from the database"""
    DB = get_DB()
    query = 'SELECT * FROM application'
    applications = DB.fetch(query)
    return applications


def get_available_versions(application_id):
    """Get the available versions from the database"""
    DB = get_DB()
    if application_id == -1:
        return []
    query = 'SELECT * FROM app_version WHERE application_id = %s'
    versions = DB.fetch(query, (application_id,))
    return versions


def load_wf_from_db():
    """Load the workflows from girder"""
    DB = get_DB()
    query = 'SELECT workflow.id as workflow_id, workflow.timestamp as workflow_name, ' \
            'application.name as application_name, app_version.number as application_version, ' \
            'app_version.id as version_id, application.id as application_id, experiment.name as experiment_name ' \
            'FROM workflow ' \
            'INNER JOIN experiment ON workflow.experiment_id = experiment.id ' \
            'INNER JOIN app_version ON experiment.version_id = app_version.id ' \
            'INNER JOIN application ON app_version.application_id = application.id'

    results = DB.fetch(query)
    return build_wf_json_from_db(results)


def load_app_wf_from_db(app_id):
    """Load the workflows from girder for a specific application"""
    DB = get_DB()
    query = 'SELECT workflow.id as workflow_id, workflow.timestamp as workflow_name, ' \
            'application.name as application_name, app_version.number as application_version, ' \
            'app_version.id as version_id, application.id as application_id, experiment.name as experiment_name ' \
            'FROM workflow ' \
            'INNER JOIN experiment ON workflow.experiment_id = experiment.id ' \
            'INNER JOIN app_version ON experiment.version_id = app_version.id ' \
            'INNER JOIN application ON app_version.application_id = application.id ' \
            'WHERE application.id = %s'
    results = DB.fetch(query, (app_id,))
    return build_wf_json_from_db(results)


def build_wf_json_from_db(results):
    """Build the json from the database"""
    exp_list = []
    for result in results:
        exp_list.append({
            "id": result.get("workflow_id"),
            "name": result.get("workflow_name"),
            "application_name": result.get("application_name"),
            "experiment_name": result.get("experiment_name"),
            "application_version": result.get("application_version"),
            "application_id": result.get("application_id"),
            "version_id": result.get("version_id")
        })
    return exp_list


def save_file_for_comparison(content, name):
    """Save the file for comparison"""
    path = CACHE_FOLDER + "/user_compare/"
    if not os.path.exists(path):
        os.makedirs(path)

    uuid = hashlib.md5(content.encode()).hexdigest()
    # remove the head
    content = content.replace(content.split(",")[0] + ",", "")
    # get the extension
    extension = name.split(".")[-1]
    # decode the content
    content = decode_base64(content)
    if extension != "zip":
        with open(path + str(uuid) + "." + extension, "wb") as f:
            f.write(content)

        if extension == "gz":
            with gzip.open(path + str(uuid) + "." + extension, 'rb') as f:
                file_content = f.read()
                with open(path + str(uuid) + "." + name.split(".")[-2], "wb") as f2:
                    f2.write(file_content)
    else:
        # create the folder if not exists
        if not os.path.exists(path + str(uuid)):
            os.makedirs(path + str(uuid))
            # save files contained in the zip
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                z.extractall(path + str(uuid))
                flatten_folder(path + str(uuid))

    return uuid


def decode_base64(string: str) -> bytes:
    """Decode a base64 string"""
    return base64.b64decode(string)


def flatten_folder(path):
    """Flatten the folder by moving the files to the top level"""
    nodes = os.listdir(path)
    while nodes:
        node = nodes.pop()
        if os.path.isdir(os.path.join(path, node)):
            for subnode in os.listdir(os.path.join(path, node)):
                nodes.append(os.path.join(node, subnode))
        else:
            shutil.move(os.path.join(path, node), path)

    # remove the subfolders
    for root, dirs, _ in os.walk(path):
        for actual_dir in dirs:
            shutil.rmtree(os.path.join(root, actual_dir))


def check_type(data_type, name, app):
    """Check if the uploaded file is of the right type"""
    ext = name.split('.')[-1]
    if data_type == '1-1' and app == 'cquest':
        return ext == 'txt'
    if data_type == '1-1' and app == 'nifti':
        return (ext == 'nii') or (name.split('.')[-2] == 'nii' and ext == 'gz')
    if data_type in ('x-y', 'x'):
        return ext == 'zip'
    return False


def get_list_structure(exp_list, href):
    """Get the list structure for the workflows"""
    return dbc.Row(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                exp.get("application_name") + '/' + exp.get("application_version") + ' - ' +
                                exp.get("name"),
                                id='repro-execution',
                                className="mr-1",
                                href=href + "-" + str(exp.get("application_name").lower()) + '?id=' + str(
                                    exp.get("id")),
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'},
                    )
                    for exp in exp_list
                ],
            )
        ],
        style={'flexDirection': 'row'},
    )


def get_list_structure_for_comparison(exp_list, href):
    """Get the list structure for the experiments"""
    return dbc.Row(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Button(
                                exp.get("application_version") + " - " + exp.get("name"),
                                id='repro-execution',
                                className="mr-1",
                                href=href + '?experiment=' + str(exp.get("id")),
                                style={'width': 'fit-content'},
                            ),
                        ],
                        className='card-body',
                        style={'justifyContent': 'center', 'gap': '10px', 'width': 'fit-content'},
                    )
                    for exp in exp_list
                ],
            )
        ],
        style={'flexDirection': 'row'},
    )
