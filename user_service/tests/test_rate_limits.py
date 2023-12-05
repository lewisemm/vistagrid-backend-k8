import json

from flask import url_for
from faker import Faker

from user_service.tests.fixtures.common import (
    client,
    credentials,
    existing_user,
)

def test_login_route_rate_limit(client, existing_user, credentials):
    """
    Tests that successful requests to `/login` route are limited to two per 15
    minute window.
    """
    with client.application.app_context():
        url = url_for('user-auth')
        # accepts only two requests to user-auth within a 15 minute window.
        for _ in range(2):
            res = client.post(
                url,
                data=json.dumps(credentials),
                content_type='application/json'
            )
            assert res.status_code == 200
            assert 'access_token' in res.json
        # third request is denied
        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 429
