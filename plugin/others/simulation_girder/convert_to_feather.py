import hashlib
import io
import json
import os
import sys

import pandas as pd



def get_quest2(quest2_path, verbose=False) -> tuple[pd.DataFrame, str]:
    """ A home-made function to import data from CQuest result files : *_quest2.txt"""
    
    class __LineInfo():
        """A finite state machine to control each step while reading the result file"""

        def __init__(self):
            self.state = "Newline"
            self.index = 0

        def refresh(self, input) -> None:
            """input = first element of a new line (sep='\t') in the result file""" 
            self.index += 1
            if not input: # Current line is empty
                # Case : Expected New line --> Nothing to do
                if self.state in ["Newline", "Record", "Warning"] : 
                    self.state = "Newline"
                # Case : End of metabolite block --> Record metabolite data
                elif self.state == "Values" : 
                    self.state = "Record" 
                # Case : Unexpected New Line --> Error State
                else:
                    self.state = "Error"
            # Case : Metabolite name
            elif input == 'Metabolite:' and self.state == "Newline" : 
                self.state = "Metabolite"
            # Case : Parameter names
            elif input.split()[0].isalpha() and self.state == "Metabolite" : 
                self.state = "Parameters" 
            # Case : Parameter values
            elif input.isnumeric() and self.state == "Parameters" : 
                self.state = "Values" 
            # Case : Warning message (seen on several files)
            elif input.split()[0] == 'WARNING!' and self.state == "Newline" : 
                self.state = "Warning"
            # Case : Unexpected 1st word --> Error state
            else:
                self.state = "Error"
    # End of the finite state machine

    # Main program 
    # Create an empty data frame 
    data = pd.DataFrame()
    # Read the result file
    with open(quest2_path, 'r') as f:
        # Initiate the finite state machine to control each line of the result file
        line_info = __LineInfo()
        # Read each line
        for line in f:
            # Split the line and read 1st word
            words = line[:-1].split('\t')
            # Update the line state according to the 1st word
            line_info.refresh(words[0])
            # Case : Metabolite name
            if line_info.state == 'Metabolite': 
                # Create new frame for this metabolite
                frame = {
                    "Metabolite": words[1].split("_")[0] # Short name
                }
                params = []
                values = []
            # Case : Parameter names
            elif line_info.state == "Parameters":
                # List of parameters, excluding "Pixel Position"
                params = [ '_'.join(param_str.split(' ')) for param_str in words[1:] if param_str ]
            # Case : Parameter values
            elif line_info.state == "Values":
                # List of parameter values, excluding Pixel & Position
                values = [ val_str for val_str in words[2:] if val_str ]
            # Case : Record parameter values after metabolite block
            elif line_info.state == "Record":
                # Update the frame
                frame.update( dict(zip(params, values)) )
                # Add line_info frame to the data
                data = pd.concat([ data, pd.DataFrame([frame]) ], ignore_index=True )
            # Case : Error state
            elif line_info.state == 'Error': 
                raise Exception( "Error while importing Quest results !\n\
                    File: {}\n\t In line N°{}: '{}'.\n\
                    Check data format.".format(quest2_path, line_info.index, line[:-1]) )
            else: # Case : New line 
                # Nothing to to
                pass
    # Return
    return data


def aggregate_workflow(path):
    print('Aggregating workflow')
    # get all the file ending with _quest2.txt in the folder
    files = [f for f in os.listdir(path) if f.endswith('_quest2.txt')]
    # get quest2 while adding a column named 'Iteration' with the iteration number
    i = 0
    data_list = []
    for f in files:
        df = get_quest2(path + '/' + f)
        df['Iteration'] = i
        data_list.append(df)
        i += 1
        
    # concatenate all the dataframes
    data = pd.concat(data_list, ignore_index=True)
    # save the dataframe as a feather file
    data.to_feather(path + '/data.feather')
    print('Workflow aggregation done')


def aggregate_workflow_without_folder_logic(files):
    print('Aggregating workflow')
    # get quest2 while adding a column named 'Iteration' with the iteration number
    i = 0
    data_list = []
    for f in files:
        df = get_quest2(f)
        df['Iteration'] = i
        data_list.append(df)
        i += 1
        
    # concatenate all the dataframes
    data = pd.concat(data_list, ignore_index=True)
    # save the dataframe into a feather fortmat on a bytes variable
    buffer = io.BytesIO()
    data.to_feather(buffer)
    # get the md5 hash of the buffer
    md5 = hashlib.md5(buffer.getvalue()).hexdigest()
    path = md5[:2] + '/' + md5[2:4] + '/' + md5
    # save the buffer into the path in local storage
    with open(path, 'wb') as f:
        f.write(buffer.getvalue())
    print('Workflow aggregation done')
    return path


def aggregate_experiment_without_folder_logic(files_list):
    # files list is a list of paths to feather files
    print('Aggregating experiment')
    # aggregate all the feather files into a single dataframe
    data_list = []
    for f in files_list:
        data_list.append(pd.read_feather(f))
    # concatenate all the dataframes
    data = pd.concat(data_list, ignore_index=True)
    # save the dataframe into a feather fortmat on a bytes variable
    buffer = io.BytesIO()
    data.to_feather(buffer)
    # get the md5 hash of the buffer
    md5 = hashlib.md5(buffer.getvalue()).hexdigest()
    path = md5[:2] + '/' + md5[2:4] + '/' + md5
    # save the buffer into the path in local storage
    with open(path, 'wb') as f:
        f.write(buffer.getvalue())
    print('Experiment aggregation done')
    return path

    
def aggregate_experiment(workflow_path):
    print('Aggregating experiment')
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


def process_hierarchy(hierarchy):
    out_json = {}
    files_list = []
    # Read the json file
    with open(hierarchy, 'r') as f:
        hierarchy = json.load(f)
        
    experiment_id = list(hierarchy.keys())[0]
    for workflow in hierarchy[experiment_id]:
        # Get the workflow id
        workflow_id = list(workflow.keys())[0]
        path = aggregate_workflow_without_folder_logic([f['path'] for f in workflow[workflow_id]])
        out_json[workflow_id] = path
        files_list.append(path)
    
    # aggregate the experiment
    path = aggregate_experiment_without_folder_logic(files_list)
    out_json[experiment_id] = path

    # save the json file
    with open(hierarchy.split('.')[0] + '_processed.json', 'w') as f:
        json.dump(out_json, f)
    


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("This program takes one argument as input (path to the json describing the hierarchy of the experiment)")
        exit()
    hierarchy = sys.argv[1]
    process_hierarchy(hierarchy)
