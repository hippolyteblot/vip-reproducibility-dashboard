import dash

from views.repro_experiment_cquest import layout


dash.register_page(
    __name__,
    path='/repro-experiment-cquestaaaaaaaaaa',
    title='Reproduce an experiment'
)

layout = layout()
