import dash

from views.reproducibility import layout

dash.register_page(
    __name__,
    path='/reproducibility',
    title='Reproducibility'
)

layout = layout()
