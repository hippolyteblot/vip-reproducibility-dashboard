import dash

from views.repro_execution import layout

dash.register_page(
    __name__,
    path='/repro-execution',
    title='Reproduce an execution',
)

layout = layout()
