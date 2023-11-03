import json


json_output = {
        "folder1": {
            "folder2": {
                "data.feather": "file1.feather",
            },
            "folder3": {
                "data.feather": "file2.feather",
            },
            "data.feather": "file3.feather",
        },
    }
print(json.dumps(json_output, indent=4))