import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
    BASE_URL = 'https://api.themoviedb.org/3/'
    BASE_URL_END = '?api_key=' + API_KEY
    SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@localhost:5432/imdb'
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
