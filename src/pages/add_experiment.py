import dash

from views.add_experiment import layout
from flask_login import current_user

dash.register_page(
    __name__,
    path='/add-experiment',
    title='Add Experiment'
)

layout = layout()
