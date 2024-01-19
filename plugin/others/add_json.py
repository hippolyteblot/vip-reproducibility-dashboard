import hashlib
import os



def add_json(path):
    # list each folders, not files
    folders_list = os.listdir(path)
    folders_list = [folder for folder in folders_list if os.path.isdir(path + '/' + folder)]
    for subfolder in folders_list:
        # add the name of the folder to the list
        for subsubfolder in os.listdir(path + '/' + subfolder):
            # in this subfolder, add a new file named 'data.json'
            json_file = open(path + '/' + subfolder + '/' + subsubfolder + '/data.json', 'w')
            json_file.write('{\n')
            json_file.write('    "output" : {\n')
            json_file.write('        "file_name" : ' + subfolder + '_quest2.txt",\n')
            json_file.write('        "girder_id" : "5b7b1a9e8d777f0001f2e2a1"\n')
            json_file.write('    },\n')
            json_file.write('    "input" : {\n')
            json_file.write('        "file_name" : ' + subfolder + '.mrui",\n')
            json_file.write('        "md5" : ' + md5(get_input_file(path, subfolder)) + ',\n')
            json_file.write('        "girder_id" : "5b7b1a9e8d777f0001f2e2a2"\n')
            json_file.write('    },\n')
            json_file.write('    "parameters_file" : {\n')
            json_file.write('        "file_name" : "params1.txt",\n')
            json_file.write('        "md5" : ' + md5(get_parameters_file(path, subfolder)) + ',\n')
            json_file.write('        "girder_id" : "5b7b1a9e8d777f0001f2e2a3"\n')
            json_file.write('    },\n')
            json_file.write('    "string_param" : "hello",\n')
            json_file.write('    "pipeline" : "CQUEST/1.4"\n')
            json_file.write('}')
            json_file.close()
            print('Created ' + path + '/' + subfolder + '/' + subsubfolder + '/data.json')

def md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_input_file(path, subfolder):
    pass

def get_parameters_file(path, subfolder):
    pass


add_json('data/A')
add_json('data/B')