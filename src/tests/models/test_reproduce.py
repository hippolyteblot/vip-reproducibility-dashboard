import pandas as pd

from models.reproduce import get_cquest_data_from_girder, get_parameters_for_spectro
from utils.settings import GVC


def test_get_data_from_girder():
    execution_id = "42"
    user_id = "1"
    data = get_cquest_data_from_girder(execution_id, user_id)
    assert isinstance(data, pd.DataFrame)
    assert data["Amplitude"].dtype == float
    assert data["SD"].dtype == float

    GVC.clean_user_download_folder(user_id)


def test_get_parameters_for_spectro():
    data = pd.DataFrame({'Metabolite': ['metabolite1', 'metabolite2'], 'Voxel': [1, 2], 'Group': ['group1', 'group2']})
    metabolites, voxels, groups = get_parameters_for_spectro(data)

    # For each wanted metabolite, check if it present in the returned list, never mind the order
    wanted_metabolites = [{'label': 'metabolite1', 'value': 'metabolite1'},
                          {'label': 'metabolite2', 'value': 'metabolite2'}, {'label': 'All', 'value': 'All'}]

    for metabolite in metabolites:
        assert metabolite in wanted_metabolites
        wanted_metabolites.remove(metabolite)

    # Same for voxels
    wanted_voxels = [{'label': '1', 'value': 1}, {'label': '2', 'value': 2}, {'label': 'All', 'value': -1}]

    for voxel in voxels:
        assert voxel in wanted_voxels
        wanted_voxels.remove(voxel)

    # Same for groups
    wanted_groups = [{'label': 'group1', 'value': 'group1'}, {'label': 'group2', 'value': 'group2'},
                     {'label': 'All', 'value': 'All'}]

    for group in groups:
        assert group in wanted_groups
        wanted_groups.remove(group)

    assert len(wanted_metabolites) == 0
    assert len(wanted_voxels) == 0
    assert len(wanted_groups) == 0
