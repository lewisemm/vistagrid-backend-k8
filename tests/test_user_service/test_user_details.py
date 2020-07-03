import pytest

from faker import Faker

from user_service import models
from tests.client_fixture import client


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
    # import pdb; pdb.set_trace()
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
