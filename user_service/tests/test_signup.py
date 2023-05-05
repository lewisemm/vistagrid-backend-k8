import json
import pytest

from flask import url_for
from faker import Faker

from user_service import models
from user_service.tests.fixtures.common import (
    client,
    credentials
)

fake = Faker()


def test_signup(client, credentials):
    with client.application.app_context():
        url = url_for('user-list')
        res = client.post(
            url,
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
    with client.application.app_context():
        url = url_for('user-list')
        data = {
            'password': fake.password()
        }
        res = client.post(
            url, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 400
        # assert that database has remained unchanged
        saved_user = models.User.query.all()
        assert len(saved_user) == 0


def test_signup_missing_password(client):
    with client.application.app_context():
        url = url_for('user-list')
        data = {
            'username': fake.user_name()
        }
        res = client.post(
            url, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 400
        # assert that database has remained unchanged
        saved_user = models.User.query.all()
        assert len(saved_user) == 0


def test_signup_missing_username_and_password(client):
    with client.application.app_context():
        url = url_for('user-list')
        data = {
            'fake_field1': fake.word(),
            'fake_field2': fake.word()
        }
        res = client.post(
            url, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 422
        # assert that database has remained unchanged
        saved_user = models.User.query.all()
        assert len(saved_user) == 0


def test_signup_when_user_already_exists(client, credentials):
    with client.application.app_context():
        url = url_for('user-list')
        existing_user = models.User(**credentials)
        models.db.session.add(existing_user)
        models.db.session.commit()

        res = client.post(
            url,
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert res.status_code == 409
