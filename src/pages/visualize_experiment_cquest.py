"""
Controller for the page that allows to visualize the results of a cQUEST experiment.
"""
import dash

from views.visualize_experiment_cquest import layout

dash.register_page(
    __name__,
    path='/visualize-experiment-cquest',
    title='Reproduce an execution',
)

layout = layout()
