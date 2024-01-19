import hashlib
import os
from girder.constants import AccessType
from girder.api.rest import Resource, filtermodel
from girder.models.item import Item
from girder.models.folder import Folder
from girder.models.file import File
from girder.models.assetstore import Assetstore
from girder.models.upload import Upload
from girder.api import access
from girder.models.user import User
from girder.api.describe import Description, autoDescribeRoute
from girder.models.setting import Setting
from bson import ObjectId
from girder.constants import AccessType
from girder.exceptions import AccessException, RestException

import json
import docker
import bson.json_util
import shutil

from .ConversionPluginSettings import ConversionPluginSettings


class ConversionHandler(Resource):

    DEFAULT_USER = 'ANONYMOUS'

    def __init__(self):
        self.settings = Setting().get(ConversionPluginSettings.SETTING_KEY)
        super(ConversionHandler, self).__init__()
        self.resourceName = 'convert'
        self.settings = Setting()
        self.resourceName = 'convert'
        User().exposeFields(level=AccessType.READ, fields={'canConvert'})
        self.route('GET', (), self.launch_execution)

    
    @access.public
    @autoDescribeRoute(
       Description("Launch the execution of a container")
            .param('application', 'The name of the application', required=True, strip=True)
            .param('version', 'The version of the application', required=True, strip=True)
            .param('experimentId', 'The ID of the experiment', required=True, strip=True)
            .param('containerId', 'The ID of the container', required=True, strip=True)
            .errorResponse('ID was invalid')
    )
    def launch_execution(self, application: str, version: str, experimentId: str, containerId: str):
        User().exposeFields(level=AccessType.READ, fields={'canConvert'})
        user = self.getCurrentUser()
        if "canConvert" not in user or user["canConvert"] is False:
            return {
                "message": "The user does not have the rights to convert an experiment",
                "type": "error"
            }
        response = {}
        containers = {
            "cquest-converter:1.0": "converter:1.0",
            "cquest2": "creatis/quest2:latest"
        }
        # get the container name
        containerName = containers[containerId]
        folders = get_folders_from_experiment(experimentId)
        if folders is None:
            response["message"] = "No data found for this experiment ID"
            response["type"] = "error"
        else:
            hashed = hashlib.md5(string=experimentId.encode()).hexdigest()
            # for now, each folder corresponds to a wf
            prepare_files(folders, hashed, experimentId)
            # save the folders in a json file
            os.makedirs("../venv/storage/{}".format(hashed), exist_ok=True)
            parsed = bson.json_util.dumps(folders)
            json.dump(parsed, open("../venv/storage/{}/folders.json".format(hashed), "w"))
            # call the container
            json_output = call_container(containerName, hashed, experimentId)
            if json_output is None:
                response["message"] = "Error during the conversion with the container"
                response["type"] = "error"
            elif insert_result("../venv/storage/{}".format(hashed), json_output, application, version, 
                               self.getCurrentUser()) is None:
                response["message"] = "Error during the insertion of the result in the database"
                response["type"] = "error"
            else:
                response["message"] = "The conversion was successful"
                response["type"] = "success"

        return response


def get_folders_from_experiment(exp_id):
    results = {}
    target_name = Setting().get(ConversionPluginSettings.SETTING_KEY).get("target_name")
    request = {"meta.{}".format(target_name): exp_id}
    params = {
        "limit": 1000,
        "offset": 0,
        "sort": [("name", 1)]
    }
    # list of the ressources that we are looking for
    ressources = {
        "folder": Folder,
        "item": Item,
    }
    for rsc in ressources:
        results[rsc] = []
        cursor = ressources[rsc]().find(request, **params)
        for r in cursor:
            results[rsc].append(r)
    # if there is no folder, return None
    return results if len(results["folder"]) != 0 \
        or len(results["item"]) != 0 else None


def call_container(container_name, hashed, exp_id):
    data_path = Setting().get(ConversionPluginSettings.SETTING_KEY).get("data_path")
    client = docker.from_env()
    # TODO : Lancer le conteneur avec le bon utilisateur
    cc = client.containers.run(
        image=container_name,
        #command="python3 /Resources/convert.py /Resources/{}/folders.json".format(hashed),
        command=hashed + "/",
        # Mount the folder in the container
        volumes={
            data_path: {
                'bind': '/vol',
                'mode': 'rw'
            },
        },
        detach=False
    )
    print(cc)

    output_path = "../venv/storage/{}/{}_processed.json".format(hashed, exp_id)

    return json.load(open(output_path, "r"))
    

def insert_result(path, hierarchy, application, version, creator):
    output_id = Setting().get(ConversionPluginSettings.SETTING_KEY).get("girder_id_outputs")
    # asset
    assetstore = Assetstore().getCurrent()
    # find the folder named application or create it
    app_folder = Folder().findOne({
        "parentId": ObjectId(output_id),
        "name": application
    })
    parent_folder = Folder().findOne({
        "_id": ObjectId(output_id)
    })
    if app_folder is None:
        app_folder = Folder().createFolder(
            parent=parent_folder,
            name=application,
            public=True,
            creator=creator
        )
    # find the folder named version or create it
    vers_folder = Folder().findOne({
        "parentId": ObjectId(app_folder["_id"]),
        "name": version
    })
    if vers_folder is None:
        parent_folder = Folder().findOne({
            "_id": ObjectId(app_folder["_id"])
        })
        vers_folder = Folder().createFolder(
            parent=parent_folder,
            name=version,
            public=True,
            creator=creator
        )
    # create the hierarchy of folders
    return insert_data(hierarchy, vers_folder, creator, path, assetstore)

def insert_data(hierarchy, parent_folder, creator, path, assetstore):
    for key, value in hierarchy.items():
        if isinstance(value, dict):
            # Check if the folder already exists
            i = 0
            folder_name = key
            while Folder().findOne({
                "parentId": ObjectId(parent_folder["_id"]),
                "name": folder_name
            }) is not None:
                i += 1
                folder_name = key + "_(" + str(i) + ")"
            # Create a folder
            folder = Folder().createFolder(
                parent=parent_folder,
                name=folder_name,
                parentType="folder",
                public=True,
                creator=creator
            )
            # Recursively insert data in the subfolder
            insert_data(value, folder, creator, path, assetstore)
        else:
            # Upload the file
            item = Item().createItem(
                name=key,
                creator=creator,
                folder=parent_folder,
                reuseExisting=True,
                description=""
            )
            # Insert the file
            file_path = os.path.join(path, value)
            size = os.path.getsize(file_path)
            name = "data.feather"

            with open(file_path, 'rb') as f:
                Upload().uploadFromFile(f, size, name, 'item', item, creator)
    return True

def prepare_files(folders, hashed, experimentId):
    # for each folder, get the items
    for folder in folders["folder"]:
        items = Item().find({
            "folderId": folder["_id"]
        })
        
        # for each item, get the file
        for item in items:
            os.makedirs("../venv/storage/{}/{}/{}/{}".format(hashed, experimentId, folder["name"], item["name"]), exist_ok=True)
            file = File().findOne({
                "itemId": item["_id"]
            })
            # get the file path
            path = os.path.join("../venv/storage", file["path"])
            # get the file name
            name = file["name"]
            # copy the file in the folder
            shutil.copyfile(path, "../venv/storage/{}/{}/{}/{}/{}".format(hashed, experimentId, folder["name"], 
                                                                          item["name"], name))
