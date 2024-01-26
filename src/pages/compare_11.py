"""
Controller for the compare-11 page. Allows to compare the results of two executions of cQUEST.
"""
import dash

from views.compare_11 import layout

dash.register_page(
    __name__,
    path='/compare-11',
    title='Compare files',
)

layout = layout()
