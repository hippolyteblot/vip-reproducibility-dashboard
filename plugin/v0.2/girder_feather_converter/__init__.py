# -*- coding: utf-8 -*-
import hashlib
import io
import json
import os
import warnings

import pandas as pd
import docker
from bson import json_util, ObjectId, datetime

from girder import events
from girder.plugin import GirderPlugin
from girder.models.item import Item
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.user import User

from .utils import get_quest2


class FeatherConverterPlugin(GirderPlugin):
    DISPLAY_NAME = 'Feather Converter'

    def load(self, info):
        # Add a listener to the data.process event (data upload)
        events.bind('data.process', 'feather_converter', self.check_file_for_conversion)

    def check_file_for_conversion(self, event):
        file_name = event.info['file']['name']
        # if the file name end with _quest2.txt, then convert it to feather
        if file_name.endswith('_quest2.txt'):
            #convert_to_feather(event.info['file'])
            hierarchy = get_files_to_aggregate(event.info['file'])
            print()
            print(hierarchy)
            print()
            data_to_insert = call_aggregation_container(hierarchy, str(event.info['file']['_id']))
            insert_from_json(data_to_insert, event.info['file']['assetstoreId'])


def convert_to_feather(file_info) -> None:
    quest2_path = file_info['path']
    file_name = file_info['name']
    item_id = file_info['itemId']
    assetstore_id = file_info['assetstoreId']

    # get the data from the quest2 file
    data = get_quest2(quest2_path, verbose=False)
    file_name = file_name.split('.')[0] + '.feather'
    # use a buffer to store the converted data
    buffer = io.BytesIO()
    data.to_feather(buffer)

    item_manager = Item()

    original_item = item_manager.load(item_id, force=True)

    # encapsulation of the folder id in a dict
    folder = {
        "_id": original_item["folderId"],
    }
    # anon user
    creator = {
        "_id": "0",
    }

    item = item_manager.createItem(name=file_name, creator=creator, folder=folder)

    file_manager = File()
    assetstore = {
        "_id" : assetstore_id,
    }

    # generate the file withouth saving it (we need to add more info to it)
    file = file_manager.createFile(
        creator=creator, 
        item=item, 
        name=file_name, 
        size=buffer.getbuffer().nbytes, 
        assetstore=assetstore, 
        saveFile=False)

    # path is composed of the first to char of the sha512 hash of the file name / the 3th and 4th char / the entire hash
    sha512 = hashlib.sha512(file_name.encode()).hexdigest()
    path = hashlib.sha512(sha512.encode()).hexdigest()[0:2] + "/" + hashlib.sha512(sha512.encode()).hexdigest()[2:4] + "/" + hashlib.sha512(sha512.encode()).hexdigest()
    
    # add the path and the sha512 to the file
    file["path"] = path
    file["sha512"] = sha512
    # save the file with the new info
    file_manager.save(file)

    # build the path to the file
    while not os.path.exists("venv/storage/" + os.path.dirname(path)):
        # each loop create the next folder in the path
        os.makedirs("venv/storage/" + os.path.dirname(path))

    # write the buffer to the file
    with open("venv/storage/" + path, "wb") as f:
        f.write(buffer.getvalue())
    
def get_files_to_aggregate(file_info):
    print("step 1")
    hierarchy = {}
    print(file_info)
    item_id = file_info["itemId"]
    item = Item().load(item_id, force=True)
    workflow_id = item["folderId"]
    workflow = Folder().load(workflow_id, force=True)
    folder_manager = Folder()
    item_manager = Item()
    user_manager = User()

    all_users = user_manager.getAdmins()
    admin1 = all_users[0]

    print("step 1.5")

    experiment = folder_manager.load(workflow["parentId"], force=True)

    hierarchy[experiment['_id']] = {}

    print("step 2")
    # get all the workflows in the experiment
    workflows = folder_manager.childFolders(
        parent=experiment,
        parentType="folder",
        limit=0,
        user=admin1
    )
    # for each workflow get the files
    for workflow in workflows:
        print("step 3")
        # get all the items in the workflow
        items = folder_manager.childItems(
            folder=workflow,
            limit=0,
        )
        # keep only the itmes ending with _quest2.txt
        items = [item for item in items if item["name"].endswith("_quest2.txt")]
        # get the first file of each item
        files = []
        for item in items:
            print("step 3.1")
            items = item_manager.childFiles(
                item=item,
                limit=0,
            )
            print(items)
            first_file = list(items)[0]
            print(first_file)
            files.append(first_file)
        print("step 3.5")
        # add the workflow
        hierarchy[experiment['_id']][workflow['_id']] = files
    
    print("step 4")
    print(hierarchy)
    hierarchy = str(hierarchy)
    hierarchy = build_json_from_str(hierarchy)
    print(hierarchy)
    print("step 5")
    return hierarchy


def build_json_from_str(string: str):
    string = string.replace("ObjectId(", "")
    string = string.replace("')", "'")
    string = string.replace("datetime.datetime(", "\"")
    string = string.replace("0)", "0\"")
    string = string.replace("'", "\"")
    return json.loads(string)


def call_aggregation_container(hierarchy, file_id: str):
    # save the hierarchy in a temporary json file
    print("step 6")
    print("venv/storage/" + file_id + ".json")
    # create the file
    file = open("venv/storage/" + file_id + ".json", "w")
    print("step 7")
    # write the json with indentation
    json.dump(hierarchy, file, indent=4)
    file.close()

    print("step 8")
    client = docker.from_env()
    print("step 9")
    # run the container with the json file as argument
    cc = client.containers.run(
        image='convert_to_feather',
        command=file_id+".json",
        # Mount the folder in the container
        volumes={
            '/home/blot/Documents/girderServer/venv/storage': {
                'bind': '/Resources',
                'mode': 'rw'
            },
        },
        detach=False
    )
    print(cc)
    print("step 10")

    # remove the json file
    os.remove("venv/storage/" + file_id + ".json")
    # open the json file named file_id + processed
    file = open("venv/storage/" + file_id + "_processed.json", "r")
    # read the json file as a json
    output = json.load(file)
    # remove the json file
    os.remove("venv/storage/" + file_id + "_processed.json")
    # return the json
    return output

def insert_from_json(data: json, assetstore_id: str):
    item_manager = Item()
    file_manager = File()
    creator = {
        "_id": "0",
    }
    assetstore = {
        "_id" : assetstore_id,
    }
    # for each line of the json
    for line in data:
        # folder id is the key of the line
        folder = {
            "_id": line,
        }
        # if there is already an item with the same name, delete it with its file
        old_item = item_manager.findOne({"name": "data.feather", "folderId": ObjectId(line)})
        if old_item is not None:
            old_file = file_manager.findOne({"name": "data.feather", "itemId": old_item["_id"]})
            file_manager.remove(old_file)
            item_manager.remove(item_manager.findOne({"name": "data.feather", "folderId": ObjectId(line)}))
            
        item = item_manager.createItem(name="data.feather", creator=creator, folder=folder)
        # open the file
        file = open("venv/storage/" + data[line], "rb")
        # get the file size
        file_size = os.path.getsize("venv/storage/" + data[line])
        # close the file
        file.close()
        # insert the file
        file = file_manager.createFile(
            creator=creator,
            item=item,
            name="data.feather",
            size=file_size,
            assetstore=assetstore,
            saveFile=False
        )
        path = data[line]
        # add the path and the sha512 to the file
        file["path"] = path
        file["sha512"] = path.split("/")[-1]
        # save the file with the new info
        file_manager.save(file)
        # create an empty file named file["sha512"] + .deleteLock
        open("venv/storage/" + file["path"] + ".deleteLock", "w").close()

    print("step 11")


        

