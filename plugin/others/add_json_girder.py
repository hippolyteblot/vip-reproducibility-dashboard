import hashlib
import json
import os
import girder_client
import time


gc = girder_client.GirderClient(apiUrl='https://pilot-warehouse.creatis.insa-lyon.fr/api/v1')
gc.authenticate(apiKey='7LLNHgtPuuwifMgI8ALUtdpjTQQuzMlGb9pZqAbF')


def scann_each_results(inputs_folder, outputs_folder):
    experiences = gc.listFolder(outputs_folder['_id'])
    for experience in experiences:
        executions = gc.listFolder(experience['_id'])
        for execution in executions:
            # get all the items in the folder
            items = gc.listItem(execution['_id'])
            # filter items to keep only the file that not end with .json
            output_items = [item for item in items if not item['name'].endswith('.json')]
            output_items_copy = output_items.copy()
            items = gc.listItem(execution['_id'])
            # keep only the json files
            json_items = [item for item in items if item['name'].endswith('.json')]
            # for eachfile, check if there is not already a json file with its name.json
            for output_item in output_items:
                for item in json_items:
                    if item['name'] == output_item['name'] + '.json':
                        # if there is already a json file, remove it
                        output_items_copy.remove(output_item)

            for item in output_items_copy:
                # get the file
                files = gc.listFile(item['_id'])
                for tmp_file in files:
                    file = tmp_file
                output_name = file['name']
                print(output_name)
                output_id = file['_id']
                # get the input file
                gc.downloadFile(output_id, 'download/' + output_name)
                # while the file is not downloaded, wait
                while not os.path.exists('download/' + output_name):
                    time.sleep(0.01)
                output_md5 = md5('download/' + output_name)
                

                input_items = gc.listItem(inputs_folder['_id'])
                input_file = None
                input_id = None

                input_name = output_name.split('--')[0]
                for input_item in input_items:
                    if input_item['name'].startswith(input_name):
                        input_files = gc.listFile(input_item['_id'])
                        for tmp_file in input_files:
                            input_file = tmp_file
                        input_id = input_file['_id']
                        # download the output file
                        gc.downloadFile(input_id, 'download/' + input_name)
                        # while the file is not downloaded, wait
                        while not os.path.exists('download/' + input_name):
                            time.sleep(0.01)
                        input_md5 = md5('download/' + input_name)
                
                        break
                pipeline_id = experience['meta']['pipeline_id']
                param_value = experience['meta']['input_settings']['parameter_file']
                # split to get the part after ':'
                param_id = param_value.split(':')[1]
                param = gc.getFile(param_id)
                param_name = param['name']
                # download the param file
                gc.downloadFile(param_id, 'download/' + param_name)
                # while the file is not downloaded, wait
                while not os.path.exists('download/' + param_name):
                    time.sleep(0.01)
                param_md5 = md5('download/' + param_name)
                add_json(execution['_id'], output_name, output_id, output_md5, input_name, input_id, input_md5, param_name, param_id, param_md5, pipeline_id)

def add_json(path, output_name, output_id, output_md5, input_name, input_id, input_md5, param_name, param_id, param_md5, pipeline_id):
    json_obj = {
        "output" : {
            "file_name" : output_name,
            "md5" : output_md5,
            "girder_id" : output_id
        },
        "input" : {
            "file_name" : input_name,
            "md5" : input_md5,
            "girder_id" : input_id
        },
        "parameters_file" : {
            "file_name" : param_name,
            "md5" : param_md5,
            "girder_id" : param_id
        },
        "string_param" : "hello",
        "pipeline" : pipeline_id
    }
    json_obj = json.dumps(json_obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    # save the json file
    json_file = open('download/' + output_name + '.json', 'w')
    json_file.write(json_obj)
    json_file.close()
    # upload the json file
    gc.uploadFileToFolder(path, 'download/' + output_name + '.json')


def md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# input_folder is data/quest/signals

# To update (1.4)
scann_each_results(gc.getFolder('63c9175a53083756323f757a'), gc.getFolder('6449163285f48d3da0713574'))

# To update experience exp-43 (1.5)
#scann_each_results(gc.getFolder('63c9175a53083756323f757a'), gc.getFolder('644a450e85f48d3da07145e2'))

# To update experience repro-exp (1.3)
#scann_each_results(gc.getFolder('63c9175a53083756323f757a'), gc.getFolder('644a372385f48d3da071405d'))