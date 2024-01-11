"""
This file contains all the settings of the application. Constants must be defined as environment variables.
"""
import os
from dotenv import load_dotenv

from utils.database_client import DatabaseClient

cwd = os.getcwd()
dotenv_path = os.path.join(cwd, os.getenv('ENVIRONMENT_FILE', '.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

# server config
APP_HOST = os.environ.get('HOST')
APP_PORT = int(os.environ.get('PORT'))
APP_DEBUG = bool(os.environ.get('DEBUG'))
CACHE_FOLDER = os.environ.get('CACHE_FOLDER')
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


"""
APP_HOST = 'localhost'
APP_PORT = 8050
APP_DEBUG = True
DEV_TOOLS_PROPS_CHECK = True
API_KEY = None

# database
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Tester1234!'
DB_NAME = 'TEST'

DB = DatabaseClient(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
DB.connect()

# girder credentials
GIRDER_API_URL = 'https://pilot-warehouse.creatis.insa-lyon.fr'
GIRDER_API_KEY = '7LLNHgtPuuwifMgI8ALUtdpjTQQuzMlGb9pZqAbF'
GIRDER_SOURCE_FOLDER = '63b6e0b14d15dd536f0484bc'
GIRDER_RAW_FOLDER = '63b6e29b4d15dd536f0484c2'
GIRDER_PROCESSED_FOLDER = '6440fb06f4b48945bc6dfd89'

GVC = GirderVIPClient(GIRDER_RAW_FOLDER, GIRDER_PROCESSED_FOLDER, GIRDER_SOURCE_FOLDER, GIRDER_API_URL, GIRDER_API_KEY)
"""
