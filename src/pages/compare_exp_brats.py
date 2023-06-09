import dash

from views.compare_exp_brats import layout


dash.register_page(
    __name__,
    path='/compare-exp-brats',
    title='Reproduce an experiment'
)

layout = layout()
