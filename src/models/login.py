"""
Model for the login system
"""
import bcrypt
from flask_login import UserMixin

from utils.settings import DB


class User(UserMixin):
    """User class for the login system"""
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, user_id, username, role='user'):
        self.id = user_id
        self.username = username
        self.role = role


def check_user(username, password):
    """Check if the username and password are correct"""
    user = None
    query = 'SELECT * FROM users WHERE username = %s'
    check = DB.fetch_one(query, [username])
    if check and check_password(password, check['password']):
        user = User(check['id'], check['username'], check['role'])

    return user


# To use if we manage by ourselves the authentication system
def get_hashed_password(plain_text_password):
    """Hash the password using bcrypt with salt"""
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    """Check if the password is correct"""
    encoded_plain_text_password = plain_text_password.encode('utf-8')
    encoded_hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(encoded_plain_text_password, encoded_hashed_password)
