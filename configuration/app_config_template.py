"""
Template configuration file. 
"""

class GCPConfig:
    GCP_JSON = 'asdfgasdf'
    GCP_STORAGE_BUCKET = 'asdfasdf'
    URI_PREFIX = 'asdfasdf'

class CeleryConfig():
    TEMPSTORAGE = 'asdfasdf'
    BROKER = 'asdfasfd'

class Config(object):
    SECRET_KEY = 'asdfasfd'
    SQLALCHEMY_DATABASE_URI = 'asdfasdfb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'asdfasdfasf'
    ALLOWED_EXTENSIONS = {'js'}
    CLOUD_STORAGE = GCPConfig
    CELERY_CONFIG = CeleryConfig

class TestGCPConfig:
    GCP_JSON = 'asdfasdf'
    GCP_STORAGE_BUCKET = 'asdfasdf'
    URI_PREFIX = 'asdfasdfasdf'

class TestCeleryConfig():
    TEMPSTORAGE = 'asdfasdf'
    BROKER = 'asdfasdf'

class TestConfig(object):
    SECRET_KEY = 'asfdasdf'
    SQLALCHEMY_DATABASE_URI = 'asdfasdfasdf'
    DB_PATH = 'asdfasdfasdf'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'asdfasdf'
    ALLOWED_EXTENSIONS = {'js'}
    CLOUD_STORAGE = TestGCPConfig
    CELERY_CONFIG = TestCeleryConfig
    TEST_FILE = 'aasdfasdfas'


class DatabaseConfig:
    SECRET_KEY = 'asdfasdfasdf'
