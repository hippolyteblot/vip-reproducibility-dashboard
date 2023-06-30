import dash

from views.add_experiment import layout

dash.register_page(
    __name__,
    path='/add-experiment',
    title='Add Experiment'
)

layout = layout()
