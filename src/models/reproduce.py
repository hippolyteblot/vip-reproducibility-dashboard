from utils.settings import DB


def get_experiment_name(exp_id):
    query = "SELECT name FROM experiment WHERE id = %s"
    return DB.fetch_one(query, (exp_id,))['name']


