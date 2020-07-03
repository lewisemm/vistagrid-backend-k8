import json
import pytest

from faker import Faker

from user_service import models
from tests.client_fixture import client

fake = Faker()


@pytest.fixture
def credentials():
    return {
        'username': fake.user_name(),
        'password': fake.password()
    }


def test_signup(client, credentials):
    res = client.post(
        '/api/user',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert res.status_code == 201
    # assert that user has been persisted in the database
    saved_user = models.User.query.all()[0]
    assert saved_user.username == credentials['username']
    # assert that the password has not been persisted in plain-text form
    assert saved_user.password != credentials['password']


def test_signup_missing_username(client):
    data = {
        'password': fake.password()
    }
    res = client.post(
        '/api/user', data=json.dumps(data), content_type='application/json')
    assert res.status_code == 400
    # assert that database has remained unchanged
    saved_user = models.User.query.all()
    assert len(saved_user) == 0


def test_signup_missing_password(client):
    data = {
        'username': fake.user_name()
    }
    res = client.post(
        '/api/user', data=json.dumps(data), content_type='application/json')
    assert res.status_code == 400
    # assert that database has remained unchanged
    saved_user = models.User.query.all()
    assert len(saved_user) == 0


def test_signup_missing_username_and_password(client):
    data = {
        'fake_field1': fake.word(),
        'fake_field2': fake.word()
    }
    res = client.post(
        '/api/user', data=json.dumps(data), content_type='application/json')
    assert res.status_code == 400
    # assert that database has remained unchanged
    saved_user = models.User.query.all()
    assert len(saved_user) == 0


def test_signup_when_user_already_exists(client, credentials):
    existing_user = models.User(**credentials)
    models.db.session.add(existing_user)
    models.db.session.commit()

    res = client.post(
        'api/user',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert res.status_code == 409
