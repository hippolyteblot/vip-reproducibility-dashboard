import dash

from views.repro_experience import layout


dash.register_page(
    __name__,
    path='/repro-experience',
    title='Reproduce an experience'
)

layout = layout()
