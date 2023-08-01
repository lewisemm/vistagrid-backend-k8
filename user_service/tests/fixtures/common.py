import os
import pytest

from faker import Faker

os.environ['USER_SERVICE_CONFIG_MODULE'] = 'user_service.config.test.TestConfig'

from user_service import models
from user_service.api import api

fake = Faker()


@pytest.fixture
def client():
    with api.app.app_context():
        models.db.create_all()

    with api.app.test_request_context() as context:
        context.push()
        yield api.app.test_client()
        context.pop()

    with api.app.app_context():
        models.db.drop_all()

@pytest.fixture
def credentials():
    return {
        'username': fake.user_name(),
        'password': fake.password()
    }

@pytest.fixture
def existing_user(client, credentials):
    with client.application.app_context():
        user = models.User(**credentials)
        models.db.session.add(user)
        models.db.session.commit()
        yield user

@pytest.fixture
def redis_mock(mocker):
    cache = {}
    def setter(key, value):
        cache[key] = value
        return True
    def getter(key):
        return cache.get(key, None)
    redis = mocker.patch('user_service.api.redis_conn')
    redis.set.side_effect = lambda key, value, exp: setter(key, value)
    redis.get.side_effect = lambda key: getter(key)
    return redis
