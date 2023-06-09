import dash

from views.compare_exp_cquest import layout


dash.register_page(
    __name__,
    path='/compare-exp-cquest/',
    title='Compare cquest experiments',
)

layout = layout()
