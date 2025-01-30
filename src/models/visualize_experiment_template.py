"""
This file contains functions that are used to visualize the results of an experiment.
"""

import pandas as pd

from utils.settings import CACHE_FOLDER


def read_file(filename):
    """Read a file from the tmp folder. The file can be a csv, xlsx or feather file."""
    ext = filename.split('.')[-1]

    if ext == 'feather':
        data = pd.read_feather(CACHE_FOLDER + filename)
    elif ext == 'xlsx':
        data = pd.read_excel(CACHE_FOLDER + filename)
    else:
        data = pd.read_csv(CACHE_FOLDER + filename)
    return data
