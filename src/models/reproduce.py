from utils.settings import DB


def get_experiment_name(exp_id):
    query = "SELECT name FROM experiment WHERE id = %s"
    return DB.fetch_one(query, (exp_id,))['name']


def get_girder_id_of_wf(wf_id):
    query = "SELECT girder_id FROM workflow WHERE id = %s"
    return DB.fetch_one(query, (wf_id,))['girder_id']


def parse_url(url):
    # get all the parameters in the url and return them as a list
    parameters = url.split('?')[1].split('&')
    parameters = [parameter.split('=')[1] for parameter in parameters]
    return parameters
