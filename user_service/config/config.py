import os


class CommonConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
