"""
Controller for the page that allows to visualize the results of a BraTS experiment.
"""
import dash

from views.visualize_experiment_brats import layout


dash.register_page(
    __name__,
    path='/visualize-experiment-brats',
    title='Reproduce an experiment'
)

layout = layout()
