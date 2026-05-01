import os
import pytest
from servidor import app

os.environ.setdefault('SECRET_KEY', 'test_secret_key')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client
