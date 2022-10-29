import json
import pytest

from flask import url_for
from faker import Faker

from user_service.tests.fixtures.common import (
    client,
    credentials,
    existing_user
)
from user_service import models

fake = Faker()

def test_jwt_auth(client, existing_user, credentials):
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 200
        assert 'access_token' in res.json

def test_jwt_auth_missing_username(client, existing_user, credentials):
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps({
                'password': credentials['password']
            }),
            content_type='application/json'
        )
        assert res.status_code == 400
        assert 'username field is required.' in res.data.decode('utf-8')

def test_jwt_auth_missing_password(client, existing_user, credentials):
    with client.application.app_context():
        url = url_for('user-auth')
        credentials.pop('password')
        res = client.post(
            url,
            data=json.dumps({
                'username': credentials['username']
            }),
            content_type='application/json'
        )
        assert res.status_code == 400
        assert 'password field is required.' in res.data.decode('utf-8')

def test_jwt_auth_non_existent_user(client, credentials):
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 404
        assert f'User {credentials["username"]} does not exist.' in \
            res.data.decode('utf-8')

def test_jwt_auth_wrong_password(client, existing_user, credentials):
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps({
                'username': credentials['username'],
                'password': fake.password()
            }),
            content_type='application/json'
        )
        assert res.status_code == 401
        assert f'Invalid password for user {credentials["username"]}' in \
            res.data.decode('utf-8')
