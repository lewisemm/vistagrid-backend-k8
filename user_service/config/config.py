import os


class CommonConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    # JWT_SECRET_KEY = 'super secret'
