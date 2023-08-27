import os
import pytest

from collections import UserDict
from faker import Faker

from user_service import models
from user_service.app import create_app

fake = Faker()


@pytest.fixture
def client():
    app = create_app(test_config=True)
    with app.app_context():
        models.db.create_all()

    with app.test_request_context() as context:
        context.push()
        yield app.test_client()
        context.pop()

    with app.app_context():
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
        yield user, credentials

@pytest.fixture
def redis_mock(mocker):
    class CacheDict(UserDict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def set(self, key, val, ttl):
            self.data[key] = val
    cache = CacheDict()
    redis = mocker.patch('user_service.decorators.cache.CACHE_CONNECTION')
    redis.get.side_effect = lambda key: cache
    return redis
