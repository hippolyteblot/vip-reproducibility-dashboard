"""
Controller for the login page.
"""
import dash

from views.login import layout

dash.register_page(__name__)

layout = layout()
