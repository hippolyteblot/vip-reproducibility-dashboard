"""
Controller for the visualize experiment template page. Provide to the user a way to visualize tabular data with its
own graph.
"""
import dash

from views.visualize_experiment_template import layout

dash.register_page(
    __name__,
    path='/visualize-experiment-template',
    title='Visualize an experiment',
)

layout = layout()
