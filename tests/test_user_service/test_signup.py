import json
import os
import pytest
import tempfile

from faker import Faker

from user_service.api import api
from user_service import models

fake = Faker()


@pytest.fixture
def client():
    db_fd, temp_path = tempfile.mkstemp()
    api.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_path}'
    api.app.config['TESTING'] = True
    models.db.create_all()

    with api.app.test_client() as client:
        # with api.app.app_context():
        #     api.init_db()
        yield client
    os.close(db_fd)
    os.unlink(temp_path)


def test_signup(client):
    data = {
        'username': fake.user_name(),
        'password': fake.password()
    }
    res = client.post(
        '/api/user', data=json.dumps(data), content_type='application/json')
    assert res.status_code == 201
    # assert that user has been persisted in the database
    saved_user = models.User.query.all()[0]
    assert saved_user.username == data['username']
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
