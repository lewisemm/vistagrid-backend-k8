import os

from user_service.config.base import CommonConfig

class TestConfig(CommonConfig):
    TESTING = True
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = os.environ['SERVER_NAME']
