from urllib import response
from servidor import *
from unittest.mock import patch, MagicMock
from routs.auth import *
import pytest
import json
import requests

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch("routs.auth.valida_informacoes")
def test_registro_sucesso(mock_valida, client):
    mock_user = MagicMock()
    mock_user.inserted_id = "123"

    mock_valida.return_value = (mock_user, None)

    response = client.post("/auth/registro", data={
        "nome": "João",
        "email": "joao@al.insper.edu.br",
        "pwd": "12345678"
    })

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


@patch("task.enviar_email.delay")
@patch("routs.auth.valida_informacoes")
def test_registro_envia_email_2fatores(mock_valida, mock_email_delay, client):
    mock_user = MagicMock()
    mock_user.inserted_id = "123"

    def fake_valida(*args, **kwargs):
        from task import enviar_email
        enviar_email.delay("joao@al.insper.edu.br", "codigo123")
        return mock_user, None

    mock_valida.side_effect = fake_valida

    response = client.post("/auth/registro", data={
        "nome": "João",
        "email": "joao@al.insper.edu.br",
        "pwd": "12345678"
    })

    # redirect esperado
    assert response.status_code == 302

    # verifica que o email foi enviado
    mock_email_delay.assert_called_once()


@patch("task.enviar_email.delay")
@patch("routs.auth.valida_informacoes")
def test_registro_falha_nao_envia_email(mock_valida, mock_email_delay, client):
    # Erro na validação 
    mock_valida.return_value = (None, "Erro de validação")

    response = client.post("/auth/registro", data={
        "nome": "João",
        "email": "joao@al.insper.edu.br",
        "pwd": "12345678"
    })

    assert response.status_code == 400

    # não deve enviar de email
    mock_email_delay.assert_not_called()

def test_registro_falha_campos_vazios(client):
    response = client.post("/auth/registro", data={
        "nome": "",
        "email": "",
        "pwd": ""
    })

    assert response.status_code == 400