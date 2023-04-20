import os
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

    def download_experiment_data(self, experiment_id, user_id=None):
        local_file = self.get_file_from_local(experiment_id, user_id)
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
