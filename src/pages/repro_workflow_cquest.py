import dash

from views.repro_workflow_cquest import layout

dash.register_page(
    __name__,
    path='/repro-workflow-cquest',
    title='Reproduce an execution',
)

layout = layout()
