import os
import time

import pandas as pd
import docker

from utils import get_quest2


class Aggregator:

    def __init__(self, path):
        """
        self.aggregate_workflow('Resources/cquest/1.3/repro-exp/2023-03-16_17:26:37')
        self.aggregate_workflow('Resources/cquest/1.4/exp-41/2023-03-16_17:07:38')
        self.aggregate_workflow('Resources/cquest/1.4/exp-42/2023-03-16_16:34:46')
        self.aggregate_workflow('Resources/cquest/1.4/exp-42/2023-03-16_16:34:54')
        self.aggregate_workflow('Resources/cquest/1.5/large-repro-test/2023-03-17_15:02:01')
        
        self.aggregate_experiment('Resources/cquest/1.3/repro-exp/2023-03-16_17:26:37')
        self.aggregate_experiment('Resources/cquest/1.4/exp-41/2023-03-16_17:07:38')
        self.aggregate_experiment('Resources/cquest/1.4/exp-42/2023-03-16_16:34:46')
        self.aggregate_experiment('Resources/cquest/1.4/exp-42/2023-03-16_16:34:54')
        self.aggregate_experiment('Resources/cquest/1.5/large-repro-test/2023-03-17_15:02:01')
        """
        
        self.path = path
        self.folders = get_sheet_folders(path)
        self.watchers = []
        for f in self.folders:
            self.watchers.append({
                'path': path + f,
                'old_state': os.listdir(path + f)
            })
        print('Watchers stored')
        while(True):
            for watcher in self.watchers:
                watcher['old_state'] = watch_folders(watcher, self, watcher['old_state'])
            time.sleep(0.1)
            
    
    def update(self, watcher, new_files=None):
        if new_files:
            # Check if one of the new files end with _quest2.txt
            for f in new_files:
                if f.endswith('_quest2.txt'):
                    # If yes, aggregate the workflow
                    # get the parent folder of the workflow
                    parent = watcher['path'][:-len(watcher['path'].split('/')[-1])]
                    # get all the workflow folders
                    workflows = [f for f in os.listdir(parent) if os.path.isdir(os.path.join(parent, f))]
                    print("Workflows : ", workflows)
                    for w in workflows:
                        self.aggregate_workflow(watcher['path'][:-len(watcher['path'].split('/')[-1])] + w)
                    self.aggregate_experiment(watcher['path'])
        
    
    def aggregate_workflow(self, path):
        print('Start aggregating')
        # get all the file ending with _quest2.txt in the folder
        print('Path : ', path)
        files = [f for f in os.listdir(path) if f.endswith('_quest2.txt')]
        # get quest2 while adding a column named 'Iteration' with the iteration number
        data_list = []
        for f in files:
            df = get_quest2(path + '/' + f)
            df['Workflow'] = path.split('/')[-1]
            df['Signal'] = f.split('.')[0]
            data_list.append(df)
            print('Workflow : ', path.split('/')[-1], ' Signal : ', f.split('.')[0])
        
        # concatenate all the dataframes
        data = pd.concat(data_list, ignore_index=True)
        # save the dataframe as a feather file
        data.to_feather(path + '/data.feather')
        print('Aggregation done')
    
    def aggregate_experiment(self, workflow_path):
        experiment_path = workflow_path[:-len(workflow_path.split('/')[-1])]
        # get all the workflow folders
        workflows = [f for f in os.listdir(experiment_path) if os.path.isdir(os.path.join(experiment_path, f))]
        # get all the data.feather files
        data_list = []
        for w in workflows:
            data_list.append({
                'Workflow': w,
                'Data': pd.read_feather(experiment_path + w + '/data.feather')
            })
            data_list[-1]['Data']['Workflow'] = w
        # concatenate all the dataframes
        df = pd.concat([d['Data'] for d in data_list], ignore_index=True)
        # save the dataframe as a feather file
        df.to_feather(experiment_path + 'data.feather')
        print('Experiment aggregation done')
    

def get_sheet_folders(path):
    sheets = []
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    while folders != []:
        sub_folders = []
        for f in os.listdir(path + folders[0]):
            if os.path.isdir(os.path.join(path + folders[0], f)):
                sub_folders.append(folders[0] + '/' + f)
        if len(sub_folders) == 0:
            sheets.append(folders[0])
            folders.remove(folders[0])
        else:
            folders += [f for f in sub_folders]
            folders.remove(folders[0])
    return sheets


def watch_folders(watcher, subscriber: Aggregator, old_state=None):
    # check every 0.1 second if there is a new folder on a thread
    new_state = os.listdir(watcher['path'])
    if old_state != new_state:
        print('New content in folder ' + watcher['path'])
        new_file = [f for f in new_state if f not in old_state]
        subscriber.update(watcher, new_file)
    return new_state


ag = Aggregator('Resources/')

# function that will check recusrively each folder of a path and unzips the files in .tgz format
def unzip(path):
    folders = get_folders_recursively(path)
    # for each folder, check if there is a .tgz file
    for f in folders:
        files = [f for f in os.listdir(path + f) if f.endswith('.tgz')]
        # if there is a .tgz file, unzip it
        for file in files:
            os.system('tar -xzf ' + path + f + '/' + file + ' -C ' + path + f + '/')
            os.system('rm ' + path + f + '/' + file)


def get_folders_recursively(path):
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    if len(folders) == 0:
        return []
    else:
        sub_folders = []
        for f in folders:
            sub_folders += [f + '/' + sub for sub in get_folders_recursively(path + f + '/')]
        return folders + sub_folders
