"""
Controller for the compare_exp_cquest page. This page allows the user to compare the results of two cquest experiments.
"""
import dash

from views.compare_exp_cquest import layout


dash.register_page(
    __name__,
    path='/compare-exp-cquest/',
    title='Compare cquest experiments',
)

layout = layout()
