import dash

from views.compare_xy import layout

# not used for now (allow to compare few nifti files)
dash.register_page(
    __name__,
    path='/compare-xy',
    title='Compare workflows',
)

layout = layout()
