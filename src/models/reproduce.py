"""
Home model
"""
from utils.settings import DB


def get_experiment_name(exp_id):
    """Get the name of the experiment with the given id"""
    query = "SELECT name FROM experiment WHERE id = %s"
    return DB.fetch_one(query, (exp_id,))['name']


def get_girder_id_of_wf(wf_id):
    """Get the girder id of the workflow with the given id"""
    query = "SELECT girder_id FROM workflow WHERE id = %s"
    return DB.fetch_one(query, (wf_id,))['girder_id']


def parse_url(url):
    """Parse the url and return the parameters"""
    parameters = url.split('?')[1].split('&')
    parameters = [parameter.split('=')[1] for parameter in parameters]
    return parameters
