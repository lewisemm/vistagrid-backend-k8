import os

class TestConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESING=True
    JWT_SECRET_KEY = 'super secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = os.environ['SERVER_NAME']
