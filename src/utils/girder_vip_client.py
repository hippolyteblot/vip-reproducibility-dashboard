"""
This file contains the GirderVIPClient class, which is used to interact with Girder.
"""

import os
import time

import requests.exceptions
from girder_client import GirderClient, AuthenticationError


class GirderVIPClient:
    """This class is used to interact with Girder"""
    def __init__(self, raw_folder, processed_folder, cache_folder, url=None, key=None):
        self.client = GirderClient(apiUrl=url + "/api/v1")
        self.url = url
        try:
            if url != 'test':
                self.client.authenticate(apiKey=key)
        except AuthenticationError as e:
            print("Authentication failed: " + str(e))
        except requests.exceptions.ConnectTimeout as e:
            print("Connection timeout: " + str(e))
        except requests.exceptions.ConnectionError as e:
            print("Connection error: " + str(e))
        except requests.exceptions.HTTPError as e:
            print("HTTP error: " + str(e))

        self.raw_folder = raw_folder
        self.processed_folder = processed_folder
        self.download_folder = cache_folder
        self.log_request = []
        self.downloading_files = []

    def get_parent_metadata(self, experiment_id):
        """Return the metadata of the parent folder of the experiment"""
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

    def clean_user_download_folder(self, user_id):
        """Clean the user download folder by removing the folder with the user id"""
        if os.path.exists(self.download_folder + str(user_id)):
            os.system('rm -rf ' + self.download_folder + str(user_id))
            return True
        return False
    def download_file_by_extension(self, item, extension):
        """Download the file with the given extension in the item"""
        for file in self.client.listFile(item['_id']):
            if file['name'].endswith(extension):
                self.client.downloadFile(file['_id'], self.download_folder + '/process_jsons/' + file['name'])
                return self.download_folder + '/process_jsons/' + file['name']
        return None

    def get_folders(self, folder_id):
        """Return the folders in the folder with the given id"""
        return self.client.listFolder(folder_id)

    def start_download_inspection(self):
        """Start the download inspection thread"""
        while len(self.downloading_files) > 0:
            # check if a file in self.downloading_files is in the folder
            for file in self.downloading_files:
                if file in os.listdir(self.download_folder + '/process_jsons/'):
                    self.downloading_files.remove(file)
            time.sleep(0.1)

    def download_feather_data(self, folder_id):
        """Download the feather file named data.feather in the folder if not already downloaded"""
        # check if the file is already downloaded
        if folder_id in os.listdir(self.download_folder) and 'data.feather' in os.listdir(
                self.download_folder + folder_id):
            date = os.path.getmtime(self.download_folder + folder_id + '/data.feather')
            if time.time() - date < 60 * 60:
                return self.download_folder + folder_id + '/data.feather'
        items = self.client.listItem(folder_id)
        for item in items:
            if item['name'] == 'data.feather':
                for file in self.client.listFile(item['_id']):
                    if file['name'] == 'data.feather':
                        self.client.downloadFile(file['_id'], self.download_folder + folder_id + '/data.feather')
                        print('File downloaded')
                        return self.download_folder + folder_id + '/data.feather'
        return None

    def download_file_by_name(self, folder_id, file_name):
        """Download the feather file named 'data.feather' in the folder"""
        items = self.client.listItem(folder_id)
        for item in items:
            if item['name'] == file_name:
                file = next(self.client.listFile(item['_id']))
                self.client.downloadFile(file['_id'], self.download_folder + folder_id + '/' + file_name)
                return self.download_folder + folder_id + '/' + file_name
        return None
