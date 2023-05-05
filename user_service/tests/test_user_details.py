import json
import pytest

from flask import url_for
from faker import Faker

from user_service import models
from user_service.tests.fixtures.common import (
    client,
    credentials,
    existing_user
)


fake = Faker()


def test_get_user_details(client, existing_user):
    with client.application.app_context():
        url = url_for('user-detail', user_id= existing_user.user_id)
        res = client.get(url)
        assert res.status_code == 200
        assert existing_user.username in res.data.decode('utf-8')


def test_get_user_details_404(client):
    with client.application.app_context():
        url = url_for('user-detail', user_id= 42)
        res = client.get(url)
        assert res.status_code == 404


def test_delete_user(client, existing_user):
    user_id = existing_user.user_id
    with client.application.app_context():
        user = models.User.query.get(user_id)
        assert user != None
        url = url_for('user-detail', user_id=user_id)
        res = client.delete(url)
        assert res.status_code == 204
        user = models.User.query.get(user_id)
        assert user == None


def test_delete_user_404(client):
    with client.application.app_context():
        url = url_for('user-detail', user_id=42)
        res = client.delete(url)
        assert res.status_code == 404


def test_edit_user_details(client, existing_user):
    with client.application.app_context():
        url = url_for('user-detail', user_id=existing_user.user_id)
        data = {'password': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 200

        # refresh existing_user from database.
        # cannot use models.db.session.refresh(existing_user) because
        # existing_user was yielded from a fixture that uses different model
        # session. Because of this, an sqlalchemy.orm.exc.DetachedInstanceError
        # will be raised.
        user = models.User.query.get(existing_user.user_id)

        # assert that the password in the data dictionary above is the new
        # password
        assert user.verify_password(data['password']) is True


def test_edit_user_details_404(client):
    with client.application.app_context():
        url = url_for('user-detail', user_id=42)
        data = {'password': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 404


def test_edit_user_details_missing_password_field(client, existing_user):
    with client.application.app_context():
        url = url_for('user-detail', user_id= existing_user.user_id)
        data = {'random_field': fake.password()}
        res = client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert res.status_code == 422
