import os
import pytest
import tempfile

os.environ['USER_SERVICE_CONFIG_MODULE'] = 'user_service.config.test.TestConfig'

from user_service import models
from user_service.api import api


@pytest.fixture
def client():
    db_fd, temp_path = tempfile.mkstemp()
    api.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_path}'
    models.db.create_all()

    with api.app.test_client() as client:
        # with api.app.app_context():
        #     api.init_db()
        yield client
    os.close(db_fd)
    os.unlink(temp_path)
