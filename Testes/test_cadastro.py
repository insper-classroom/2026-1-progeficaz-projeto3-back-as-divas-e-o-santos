from urllib import response
from servidor import *
from unittest.mock import patch, MagicMock
import pytest
import json
import requests

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client