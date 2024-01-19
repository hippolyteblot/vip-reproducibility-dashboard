"""
Controller for the compare_xy page. Allows to compare the results of two zipped workflows of cQUEST.
"""
import dash

from views.compare_xy import layout

dash.register_page(
    __name__,
    path='/compare-xy',
    title='Compare workflows',
)

layout = layout()
