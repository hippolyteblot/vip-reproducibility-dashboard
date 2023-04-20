import dash

from views.repro_experiment import layout


dash.register_page(
    __name__,
    path='/repro-experiment',
    title='Reproduce an experiment'
)

layout = layout()
