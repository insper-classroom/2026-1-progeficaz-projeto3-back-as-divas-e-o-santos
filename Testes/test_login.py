from unittest.mock import patch, MagicMock
import pytest
from servidor import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch("routs.auth.autenticar_usuario")
def test_login_sucesso(mock_auth, client):
    mock_user = {"_id": "123"}
    mock_auth.return_value = (mock_user, None)

    response = client.post("/auth/login", data={
        "email": "teste@al.insper.edu.br",
        "pwd": "12345678"
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert sess["user_id"] == "123"


@patch("routs.auth.render_template")
@patch("routs.auth.autenticar_usuario")
def test_login_falha(mock_auth, mock_render, client):
    mock_auth.return_value = (None, "Email ou senha inválidos.")
    mock_render.return_value = "login page"

    client.post("/auth/login", data={
        "email": "teste@al.insper.edu.br",
        "pwd": "errada"
    })

    with client.session_transaction() as sess:
        assert "user_id" not in sess

    mock_auth.assert_called_once()


@patch("routs.auth.render_template")
def test_login_campos_vazios(mock_render, client):
    mock_render.return_value = "login page"

    response = client.post("/auth/login", data={
        "email": "",
        "pwd": ""
    })

    assert response.status_code == 200
    mock_render.assert_called_once_with("login.html")

    with client.session_transaction() as sess:
        assert "user_id" not in sess


@patch("routs.auth.autenticar_usuario")
def test_login_limpa_sessao(mock_auth, client):
    mock_auth.return_value = ({"_id": "novo_id"}, None)

    with client.session_transaction() as sess:
        sess["user_id"] = "antigo_id"

    response = client.post("/auth/login", data={
        "email": "teste@al.insper.edu.br",
        "pwd": "12345678"
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert sess["user_id"] == "novo_id"