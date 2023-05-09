import json
import os
import threading
import time

from girder_client import GirderClient


class GirderVIPClient:
    def __init__(self, raw_folder, processed_folder, source_folder, url=None, key=None):
        self.client = GirderClient(apiUrl=url+"/api/v1")
        self.url = url
        self.client.authenticate(apiKey=key)
        self.raw_folder = raw_folder
        self.processed_folder = processed_folder
        self.source_folder = source_folder
        self.download_folder = 'src/tmp/'
        self.log_request = []
        self.downloading_files = []

    def get_parent_metadata(self, experiment_id):
        # First, get the folder
        folder = self.client.getFolder(self.raw_folder)
        # Then, get all subfolders
        subfolders = self.client.listFolder(folder['_id'])

        # Then, get all subfolders
        subsubfolders = [self.client.listFolder(subfolder['_id']) for subfolder in subfolders]

        # Then, get all items in the subsubfolders
        items = [item for subsubfolder in subsubfolders for subfolder in subsubfolder
                 for item in self.client.listItem(subfolder['_id'])]

        # Finally, filter the items by experiment id
        experiments = [item for item in items if
                       item['meta'] and int(item['meta'].get('experiment_id')) == experiment_id]

        # for each item, get the parent folder and add it to the list
        parent_folders = [self.client.getFolder(experiment['folderId']) for experiment in experiments]
        metadata = [parent_folder['meta'] for parent_folder in parent_folders]
        id_list = [parent_folder['_id'] for parent_folder in parent_folders]

        return metadata, id_list

    def download_experiment_data(self, experiment_id, user_id=-1):
        local_file = self.get_file_from_local(experiment_id, user_id)
        if user_id is None:
            user_id = -1
        if local_file:
            self.download_folder + str(user_id) + "/" + str(experiment_id) + '/' + self.get_name_from_id(experiment_id)
        folder = self.client.getFolder(self.processed_folder)
        # get the id of its subfolder named "cquest"
        subfolder = [subfolder for subfolder in self.client.listFolder(folder['_id'])
                     if subfolder['name'] == 'cquest'][0]
        # get the id of its subfolder named "execution"
        subsfolder = [subsubfolder for subsubfolder in self.client.listFolder(subfolder['_id'])
                      if subsubfolder['name'] == 'executions'][0]
        # then, list the items in the folder
        items = self.client.listItem(subsfolder['_id'])
        # filter the items by experiment id
        filtered_items = []
        for item in items:
            if item['meta'] and item['meta'].get('experiment_id') and \
                    int(item['meta'].get('experiment_id')) == int(experiment_id):
                filtered_items.append(item)

        first_item = None
        for item in filtered_items:
            if item['name'].endswith('.feather'):
                first_item = item
                break

        self.client.downloadItem(first_item['_id'], self.download_folder + str(user_id), str(experiment_id))
        self.log_request.append((experiment_id, user_id, time.time(), first_item['name']))
        path = self.download_folder + str(user_id) + "/" + str(experiment_id) + '/' + first_item['name']
        return path

    def get_name_from_id(self, experiment_id):
        for request in self.log_request:
            if request[0] == experiment_id:
                return request[3]

    def get_file_path(self, experiment_id, user_id):
        return self.download_folder + str(user_id) + "/" + str(experiment_id) + '/' \
            + os.listdir(self.download_folder + "/" + str(user_id) + '/' + str(experiment_id))[0]

    def get_file_from_local(self, experiment_id, user_id):
        if os.path.exists(self.download_folder + str(user_id) + "/" + str(experiment_id)):
            return self.get_file_path(experiment_id, user_id)
        else:
            return None

    def clean_user_download_folder(self, user_id):
        if os.path.exists(self.download_folder + str(user_id)):
            os.system('rm -rf ' + self.download_folder + str(user_id))

    def download_json(self, src_results_folder):
        folder = self.client.getFolder(src_results_folder)
        # get the id of its subfolder named "cquest"
        subfolder = [subfolder for subfolder in self.client.listFolder(folder['_id'])
                     if subfolder['name'] == 'cquest'][0]
        # get the id of all subfolders
        versions = [subsubfolder for subsubfolder in self.client.listFolder(subfolder['_id'])]
        # for each version folder, get every folder (this is an experiment)
        experiments = [self.client.listFolder(version['_id']) for version in versions]
        # for each experiment, get every item
        items = []
        for experiment in experiments:
            for subexperiment in experiment:
                execs = self.client.listFolder(subexperiment['_id'])
                for execution in execs:
                    items.append(self.client.listItem(execution['_id']))
        # for each item, get the json
        json_items = []
        for item in items:
            for subitem in item:
                if subitem['name'].endswith('.json'):
                    json_items.append(subitem)
        # launch the previous function on a thread

        counter = 0
        for json_item in json_items:
            json_file = None
            for file in self.client.listFile(json_item['_id']):
                if file['name'].endswith('.json'):
                    json_file = file
                    break
            self.client.downloadFile(json_file['_id'], 'src/tmp/process_jsons/' + json_file['name'])
            self.downloading_files.append(json_file['name'])
            counter += 1

        print('Downloading ' + str(counter) + ' files')
        thread = threading.Thread(target=self.start_download_inspection, args=())
        thread.start()
        return 'src/tmp/process_jsons/'

    def get_folders(self, folder_id):
        return self.client.listFolder(folder_id)

    def start_download_inspection(self):
        print('Downloading ' + str(len(self.downloading_files)) + ' files')
        while len(self.downloading_files) > 0:
            # check if a file in self.downloading_files is in the folder
            for file in self.downloading_files:
                if file in os.listdir('src/tmp/process_jsons/'):
                    self.downloading_files.remove(file)
            time.sleep(0.1)
        print('All files downloaded')

    def finished_download(self):
        return len(self.downloading_files) == 0

    def get_jsons(self, folder_id):
        """Return the data contained in the jsons of the folder"""
        items = self.client.listItem(folder_id)
        pending_files = []
        json_items = []
        for item in items:
            if item['name'].endswith('.json'):
                json_items.append(item)
        jsons = []
        for json_item in json_items:
            json_file = None
            for file in self.client.listFile(json_item['_id']):
                if file['name'].endswith('.json'):
                    json_file = file
                    break
            self.client.downloadFile(json_file['_id'], 'src/tmp/process_jsons/' + json_file['name'])
            pending_files.append(json_file['name'])
        while len(pending_files) > 0:
            for file in pending_files:
                if file in os.listdir('src/tmp/process_jsons/'):
                    pending_files.remove(file)
            time.sleep(0.1)
        for file in os.listdir('src/tmp/process_jsons/'):
            with open('src/tmp/process_jsons/' + file, 'r') as f:
                jsons.append(json.load(f))
        return jsons

    def get_jsons_from_local(self, folder_id):
        jsons = []
        for file in os.listdir('src/tmp/process_jsons/'):
            with open('src/tmp/process_jsons/' + file, 'r') as f:
                jsons.append(json.load(f))
        return jsons

    def get_folders_in_folder(self, folder_id="63b6e2d34d15dd536f0484c3"):
        """Return the folders contained in the folder"""
        folders = self.client.listFolder(folder_id)
        return folders

    def get_items_in_folder(self, folder_id):
        """Return the items contained in the folder"""
        items = self.client.listItem(folder_id)
        return items

    def download_feather_data(self, folder_id):
        """Download the feather file nammed data.feather in the folder"""
        items = self.client.listItem(folder_id)
        for item in items:
            if item['name'] == 'data.feather':
                for file in self.client.listFile(item['_id']):
                    if file['name'] == 'data.feather':
                        self.client.downloadFile(file['_id'], 'src/tmp/' + folder_id + '/data.feather')
                        return 'src/tmp/' + folder_id + '/data.feather'

        return None
