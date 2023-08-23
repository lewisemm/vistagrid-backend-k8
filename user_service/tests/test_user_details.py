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


def test_get_user_details(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, _ = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 200
        assert user.username in res.data.decode('utf-8')


def test_get_user_details_404(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, _ = logged_in_user
        url = url_for('user-detail', user_id=42)
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 403


def test_delete_user(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, _ = existing_user
        assert user != None
        url = url_for('user-detail', user_id=user.user_id)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 204
        user_in_db = models.db.session.scalar(
            models.db.select(models.User).where(
                models.User.user_id==user.user_id
            )
        )
        assert user_in_db == None


def test_delete_user_404(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, _ = logged_in_user
        url = url_for('user-detail', user_id=42)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 403


def test_edit_user_details(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, credentials = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        data = {'password': fake.password()}
        assert user.verify_password(credentials['password']) is True
        assert user.verify_password(data['password']) is False
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 200
        user_in_db = models.db.session.scalar(
            models.db.select(models.User).where(
                models.User.user_id==user.user_id
            )
        )
        # assert that the password in the data dictionary above is the new
        # password
        assert user_in_db.verify_password(data['password']) is True
        assert user_in_db.verify_password(credentials['password']) is False


def test_edit_user_details_404(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, _ = logged_in_user
        url = url_for('user-detail', user_id=42)
        data = {'password': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 403


def test_edit_user_details_missing_password_field(client, logged_in_user):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, _ = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        data = {'random_field': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 422


def test_delete_user_not_owner(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, _ = logged_in_user
        url = url_for('user-detail', user_id=42)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 403


def test_get_user_details_not_owner(client, redis_mock, logged_in_user):
    with client.application.app_context():
        token, _ = logged_in_user
        url = url_for('user-detail', user_id=42)
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 403


def test_put_user_details_not_owner(client, redis_mock, logged_in_user):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, credentials = existing_user
        url = url_for('user-detail', user_id=42)
        data = {'password': fake.password()}
        assert user.verify_password(credentials['password']) is True
        assert user.verify_password(data['password']) is False
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 403

def test_delete_user_token_not_reusable(client, logged_in_user, redis_mock):
    with client.application.app_context():
        token, existing_user = logged_in_user
        user, credentials = existing_user
        url = url_for('user-detail', user_id=user.user_id)
        res = client.delete(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 204
        # once user is deleted, JWT token cannot be used anymore
        res = client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 401
