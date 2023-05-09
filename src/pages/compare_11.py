import dash

from views.compare_11 import layout

dash.register_page(
    __name__,
    path='/compare-11',
    title='Compare files',
)

layout = layout()
