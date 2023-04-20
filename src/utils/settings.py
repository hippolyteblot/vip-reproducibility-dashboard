import os
from dotenv import load_dotenv

from utils.girder_vip_client import GirderVIPClient
from utils.database_client import DatabaseClient

cwd = os.getcwd()
dotenv_path = os.path.join(cwd, os.getenv('ENVIRONMENT_FILE', '.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

# server config
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
DB = DatabaseClient(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
DB.connect()

# girder credentials
GIRDER_API_URL = os.environ.get('GIRDER_API_URL')
GIRDER_API_KEY = os.environ.get('GIRDER_API_KEY')
GIRDER_RAW_FOLDER = os.environ.get('GIRDER_RAW_FOLDER')
GIRDER_PROCESSED_FOLDER = os.environ.get('GIRDER_PROCESSED_FOLDER')
GIRDER_SOURCE_FOLDER = os.environ.get('GIRDER_SOURCE_FOLDER')

GVC = GirderVIPClient(GIRDER_RAW_FOLDER, GIRDER_PROCESSED_FOLDER, GIRDER_SOURCE_FOLDER, GIRDER_API_URL, GIRDER_API_KEY)
