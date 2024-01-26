"""
Controller for the 404 page.
"""
import dash
from views.not_found_404 import layout

dash.register_page(
    __name__,
    path='/404',
    title='404 - Page not found',
)

layout = layout()
