"""
Controller for the page that allows to compare the results of a two BraTS experiments.
"""
import dash

from views.compare_exp_brats import layout


dash.register_page(
    __name__,
    path='/compare-exp-brats',
    title='Reproduce an experiment'
)

layout = layout()
