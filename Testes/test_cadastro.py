from urllib import response
import os
from unittest.mock import patch, MagicMock
import pytest

os.environ.setdefault('SECRET_KEY', 'test_secret_key')

from servidor import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch("rotas.auth.valida_informacoes")
@patch("rotas.auth.get_db")
def test_registro_sucesso(mock_get_db, mock_valida, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_user = MagicMock()
    mock_user.inserted_id = "123"
    mock_valida.return_value = (mock_user, None)

    response = client.post("/auth/registro", data={
        "nome": "João",
        "email": "joao@al.insper.edu.br",
        "pwd": "12345678"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")