import bcrypt
from utils.settings import DB


def check_user(username, password):
    """Check if the username and password are correct"""
    query = 'SELECT * FROM USERS WHERE USERNAME = %s AND PASSWORD = %s'
    hashed_password = hash_password(password)
    user = DB.fetch_one(query, (username, hashed_password))
    return user


def hash_password(password):
    """Hash the password"""
    """TODO: Implement a proper hashing algorithm"""
    hashed_password = password
    return hashed_password


# To use if we manage by ourselves the authentication system
def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)
