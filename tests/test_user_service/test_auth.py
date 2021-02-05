import json
import pytest

from faker import Faker

from tests.fixtures.common import (
    client,
    credentials,
    existing_user
)
from user_service import models

fake = Faker()

def test_jwt_auth(client, existing_user, credentials):
    res = client.post(
        '/api/user/auth',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert res.status_code == 200
    assert 'access_token' in res.json

def test_jwt_auth_missing_username(client, existing_user, credentials):
    res = client.post(
        '/api/user/auth',
        data=json.dumps({
            'password': credentials['password']
        }),
        content_type='application/json'
    )
    assert res.status_code == 400
    assert 'username field is required.' in res.data.decode('utf-8')

def test_jwt_auth_missing_password(client, existing_user, credentials):
    credentials.pop('password')
    res = client.post(
        '/api/user/auth',
        data=json.dumps({
            'username': credentials['username']
        }),
        content_type='application/json'
    )
    assert res.status_code == 400
    assert 'password field is required.' in res.data.decode('utf-8')

def test_jwt_auth_non_existent_user(client, credentials):
    res = client.post(
        '/api/user/auth',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert res.status_code == 404
    assert f'User {credentials["username"]} does not exist.' in \
        res.data.decode('utf-8')

def test_jwt_auth_wrong_password(client, existing_user, credentials):
    res = client.post(
        '/api/user/auth',
        data=json.dumps({
            'username': credentials['username'],
            'password': fake.password()
        }),
        content_type='application/json'
    )
    assert res.status_code == 401
    assert f'Invalid password for user {credentials["username"]}' in \
        res.data.decode('utf-8')
