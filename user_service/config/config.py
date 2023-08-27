import os
import datetime


class CommonConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        minutes=int(os.environ['JWT_ACCESS_TOKEN_EXPIRES_MINUTES'])
    )


class TestConfig(CommonConfig):
    TESING = True
    JWT_SECRET_KEY = 'super secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = os.environ['SERVER_NAME']
