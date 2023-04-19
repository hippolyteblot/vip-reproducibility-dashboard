import os
from dotenv import load_dotenv
from utils.database import Database

cwd = os.getcwd()
dotenv_path = os.path.join(cwd, os.getenv('ENVIRONMENT_FILE', '.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

APP_HOST = os.environ.get('HOST')
APP_PORT = int(os.environ.get('PORT'))
APP_DEBUG = bool(os.environ.get('DEBUG'))
DEV_TOOLS_PROPS_CHECK = bool(os.environ.get('DEV_TOOLS_PROPS_CHECK'))
API_KEY = os.environ.get('API_KEY', None)

# database
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
DB.connect()
