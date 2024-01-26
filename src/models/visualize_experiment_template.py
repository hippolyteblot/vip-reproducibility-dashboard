"""
This file contains functions that are used to visualize the results of an experiment.
"""

import pandas as pd


def read_file(filename):
    """Read a file from the tmp folder. The file can be a csv, xlsx or feather file."""
    ext = filename.split('.')[-1]
    if ext == 'feather':
        data = pd.read_feather('src/tmp/' + filename)
    elif ext == 'xlsx':
        data = pd.read_excel('src/tmp/' + filename)
    else:
        data = pd.read_csv('src/tmp/' + filename)
    return data
