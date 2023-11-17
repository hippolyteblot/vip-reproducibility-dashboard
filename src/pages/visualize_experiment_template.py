import dash

from views.visualize_experiment_template import layout

dash.register_page(
    __name__,
    path='/visualize-experiment-template',
    title='Visualize an experiment',
)

layout = layout()
