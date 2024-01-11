"""
Controller for the Compare NIfTI files page that allows the user to compare few NIfTI files at the same time.
"""
import dash

from views.compare_nii_x import layout

dash.register_page(
    __name__,
    path='/compare-nii-x',
    title='Compare NIfTI files',
)

layout = layout()
