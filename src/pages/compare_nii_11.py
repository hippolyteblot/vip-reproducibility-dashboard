import dash

from views.compare_nii_11 import layout

dash.register_page(
    __name__,
    path='/compare-nii-11',
    title='Compare NIfTI files',
)

layout = layout()
