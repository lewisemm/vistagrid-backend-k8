import json
import pytest

from flask import url_for
from faker import Faker

from user_service import models
from user_service.tests.fixtures.common import (
    client,
    credentials,
    existing_user,
    redis_mock
)


fake = Faker()


@pytest.fixture
def logged_in_user(client, existing_user):
    with client.application.app_context():
        url = url_for('user-auth')
        _, credentials = existing_user
        res = client.post(
            url,
            content_type='application/json',
            data=json.dumps(credentials)
        )
        return res.json['access_token'], existing_user


def test_get_user_details(client, existing_user, redis_mock):
    with client.application.app_context():
        user, credentials = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        res = client.get(url)
        assert res.status_code == 401
        token = login_user(client, credentials)
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 200
        assert user.username in res.data.decode('utf-8')


def test_get_user_details_404(client, existing_user, redis_mock):
    with client.application.app_context():
        _, credentials = existing_user
        url = url_for('user-detail', user_id=42)
        res = client.get(url)
        assert res.status_code == 401
        token = login_user(client, credentials)
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 404



def test_delete_user(client, existing_user, redis_mock):
    user, credentials = existing_user
    user_id = user.user_id
    with client.application.app_context():
        assert user != None
        url = url_for('user-detail', user_id=user_id)
        res = client.delete(url)
        assert res.status_code == 401
        token = login_user(client, credentials)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 204
        user_in_db = models.User.query.get(user_id)
        assert user_in_db == None


def test_delete_user_404(client, existing_user, redis_mock):
    user, credentials = existing_user
    with client.application.app_context():
        url = url_for('user-detail', user_id=42)
        res = client.delete(url)
        assert res.status_code == 401
        token = login_user(client, credentials)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 404


def test_edit_user_details(client, existing_user, redis_mock):
    with client.application.app_context():
        user, credentials = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        data = {'password': fake.password()}
        assert user.verify_password(credentials['password']) is True
        assert user.verify_password(data['password']) is False
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 401
        token = login_user(client, credentials)
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 200
        user_in_db = models.User.query.get(user.user_id)
        # assert that the password in the data dictionary above is the new
        # password
        assert user_in_db.verify_password(data['password']) is True
        assert user_in_db.verify_password(credentials['password']) is False


def test_edit_user_details_404(client, existing_user, redis_mock):
    with client.application.app_context():
        url = url_for('user-detail', user_id=42)
        data = {'password': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 401
        _, credentials = existing_user
        token = login_user(client, credentials)
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 404


def test_edit_user_details_missing_password_field(client, existing_user):
    with client.application.app_context():
        user, _ = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        data = {'random_field': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 422
