import json

from flask import url_for
from faker import Faker

from user_service.tests.fixtures.common import (
    client,
    existing_user,
    credentials,
    redis_mock
)


def test_create_refresh_token(client, existing_user, credentials):
    """
    Tests that a refresh token is created on login.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 200
        assert 'refresh_token' in res.json

def test_revoke_refresh_token_via_logout(
        client, existing_user, credentials, redis_mock
    ):
    """
    Tests that refresh token can be revoked via call to logout endpoint.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 200
        assert 'refresh_token' in res.json
        refresh_token = res.json['refresh_token']
        # refresh token can generate new access tokens before revocation
        refresh_url = url_for('refresh')
        res = client.post(
            refresh_url,
            content_type='application/json',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        assert res.status_code == 200
        assert 'access_token' in res.json
        # revoke refresh token
        logout_url = url_for('api_user_logout')
        res = client.post(
            logout_url,
            headers={'Authorization': f'Bearer {refresh_token}'},
            content_type='application/json'
        )
        assert res.status_code == 200
        # refresh token cannot generate new access tokens after revocation
        res = client.post(
            refresh_url,
            content_type='application/json',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        assert res.status_code == 401
