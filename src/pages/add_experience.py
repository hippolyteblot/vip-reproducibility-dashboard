import dash

from views.add_experience import layout

dash.register_page(
    __name__,
    path='/add-experience',
    title='Add Experience'
)

layout = layout()
