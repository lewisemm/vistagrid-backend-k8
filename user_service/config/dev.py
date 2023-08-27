import datetime
import os

from user_service.config.base import CommonConfig


class DevConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        minutes=int(os.environ['JWT_ACCESS_TOKEN_EXPIRES_MINUTES'])
    )
