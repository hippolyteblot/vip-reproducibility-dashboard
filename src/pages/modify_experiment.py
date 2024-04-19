import dash

from views.modify_experiment import layout
from flask_login import current_user


def admin_access_control(**kwargs):
    print(current_user)
    print("test")
    if not current_user.is_admin:
        return False
    return True


dash.register_page(
    __name__,
    path='/modify-experiment',
    title='Modify Experiment',
)

# check if the user is admin

layout = layout()
