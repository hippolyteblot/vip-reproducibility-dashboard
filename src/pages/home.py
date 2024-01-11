"""
Controller for the home page.
"""
import dash

from views.home import layout

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Home',
)
layout = layout()
