import os

from utils.settings import DB


def get_users():
    """Get the users from the database"""
    query = 'SELECT * FROM USERS'
    users = DB.fetch(query)
    return users


def load_exec_from_local() -> list:
    """Load the executions from the local folder"""
    folder = "src/data/spectro/"
    exec_list = []
    for group in ["A", "B"]:
        for subfolder in os.listdir(folder + group):
            # add to list : group - subfolder - index
            # TODO : Correct the name of the execution (remove the white space of each .feather file)

            voxel = subfolder.split("_Vox")[1]
            exec_number = int(subfolder.split("_")[0].split("Rec")[1])

            execution = {
                "path": group + "/" + subfolder + "/",
                "name": "parameters " + group + ", voxel " + voxel + ", execution " + str(exec_number)
            }
            exec_list.append(execution)
    return exec_list


def load_exp_from_db():
    """Load the experiments from the local folder"""
    query = 'SELECT * FROM EXPERIMENTS INNER JOIN USERS U ON EXPERIMENTS.user_id = U.id WHERE EXPERIMENTS.single = 0'
    return build_json_from_db(query)


def load_exec_from_db():
    """Load the experiments from the local folder"""
    query = 'SELECT EXPERIMENTS.id, EXPERIMENTS.application_name, EXPERIMENTS.application_version, U.username ' \
            'FROM EXPERIMENTS INNER JOIN USERS U ON EXPERIMENTS.user_id = U.id WHERE EXPERIMENTS.single = 1'

    return build_json_from_db(query)


def build_json_from_db(query):
    results = DB.fetch(query)
    exp_list = []
    for result in results:
        exp_list.append({
            "id": result.get("id"),
            "name": result.get("application_name") + " " + result.get("application_version") + " "
            + "(par : " + result.get("username") + ")",
        })
    return exp_list
