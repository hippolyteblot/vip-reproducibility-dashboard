import pandas as pd


def read_file(filename):
    """Read a file"""
    ext = filename.split('.')[-1]
    if ext == 'feather':
        data = pd.read_feather('src/tmp/' + filename)
    elif ext == 'xlsx':
        data = pd.read_excel('src/tmp/' + filename)
    else:
        data = pd.read_csv('src/tmp/' + filename)
    return data
