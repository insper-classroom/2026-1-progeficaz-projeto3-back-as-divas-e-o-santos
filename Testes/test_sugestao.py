from servidor import app
from unittest.mock import patch
from tasks.tasks import enviar_email_sugestao
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client
        

@patch("tasks.tasks.enviar_email_sugestao")
def test_sugestao_email_sucesso(mock_task, client, monkeypatch):
    monkeypatch.setenv("CONTACT_EMAIL", "admin@teste.com")

    response = client.post(
        "/api/sugestoes",
        json={"message": "Sugestão válida"}
    )

    mock_task.delay.assert_called_once_with("Sugestão válida", "admin@teste.com")
    assert response.status_code == 202


@patch("tasks.tasks.EmailMessage")
@patch("tasks.tasks.get_app")
def test_sugestao_email_falha(mock_get_app, mock_email):
    mock_app = mock_get_app.return_value
    mock_app.app_context.return_value.__enter__.return_value = mock_app

    mock_email.return_value.send.side_effect = Exception("Erro SMTP")

    with pytest.raises(Exception, match="Erro SMTP"):
        enviar_email_sugestao("Mensagem de teste", "admin@teste.com")