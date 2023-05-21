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

def test_identify_user_from_jwt_no_authorization_header(client):
    """
    Test functionality to identify request owner from request when
    `Authorization` header is missing.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.get(
            url,
            content_type='application/json',
            headers={}
        )
        assert res.status_code == 401

def test_identify_user_from_jwt_valid_authorization_header(
        client, existing_user, credentials):
    """
    Test functionality to identify request owner from request when valid
    `Authorization` header is provided.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        data = json.dumps({
            'username': credentials['username'],
            'password': credentials['password']
        })
        auth_res = client.post(url, data=data, content_type='application/json')
        assert auth_res.status_code == 200
        token = auth_res.json['access_token']
        res = client.get(
            url,
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 200
        user_id = int(res.json['user_id'] )
        assert user_id == existing_user.user_id

def test_identify_user_from_jwt_invalid_authorization_header(client):
    """
    Test functionality to identify request owner from request when invalid
    `Authorization` header is provided.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        token = "random_text_1.random_text_2.random_text_3"
        res = client.get(
            url,
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert res.status_code == 422
