import json
import pytest

from faker import Faker

from user_service import models
from user_service.tests.fixtures.common import (
    client,
    existing_user
)


fake = Faker()


@pytest.fixture
def existing_user():
    credentials = {
        'username': fake.user_name(),
        'password': fake.password()
    }
    user = models.User(**credentials)
    models.db.session.add(user)
    models.db.session.commit()
    return user


def test_get_user_details(client, existing_user):
    res = client.get(f'/api/user/{existing_user.user_id}')
    assert res.status_code == 200
    assert existing_user.username in res.data.decode('utf-8')


def test_get_user_details_404(client):
    res = client.get('/api/user/42')
    assert res.status_code == 404


def test_delete_user(client, existing_user):
    res = client.delete(f'/api/user/{existing_user.user_id}')
    assert res.status_code == 204


def test_delete_user_404(client):
    res = client.delete(f'/api/user/42')
    assert res.status_code == 404


def test_edit_user_details(client, existing_user):
    data = {'password': fake.password()}
    res = client.put(
        f'/api/user/{existing_user.user_id}',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert res.status_code == 200
    # assert that the password in the data dictionary above is the new password
    assert existing_user.verify_password(data['password']) is True


def test_edit_user_details_404(client):
    data = {'password': fake.password()}
    res = client.put(
        '/api/user/42',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert res.status_code == 404


def test_edit_user_details_missing_password_field(client, existing_user):
    data = {'random_field': fake.password()}
    res = client.put(
        f'/api/user/{existing_user.user_id}',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert res.status_code == 400
