from servidor import *
from unittest.mock import patch, MagicMock
import pytest
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client
        

@patch("controller.encontra_emails_admin")
@patch("task.enviar_email_sugestao")
def test_sugestao_email_enviado(mock_task, mock_admins, client):
    mock_admins.return_value = ["admin@teste.com"]

    response = client.post(
        "/api/sugestoes",
        json={"message": "Sugestão válida"}
    )
    mock_task.delay.assert_called_once_with("Sugestão válida", ["admin@teste.com"])

    assert response.status_code == 201


@patch("controller.encontra_emails_admin")
@patch("task.enviar_email_sugestao")
def test_sugestao_email_falha(mock_task, mock_admins, client):
    mock_admins.return_value = ["admin@teste.com"]
    mock_task.delay.side_effect = Exception("Erro no envio")

    response = client.post(
        "/api/sugestoes",
        json={"message": "Sugestão válida"}
    )

    assert response.status_code == 500