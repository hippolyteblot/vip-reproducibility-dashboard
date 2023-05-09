import dash

from views.repro_workflow import layout

dash.register_page(
    __name__,
    path='/repro-workflow',
    title='Reproduce an execution',
)

layout = layout()
