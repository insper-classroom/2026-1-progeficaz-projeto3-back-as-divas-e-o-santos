from urllib import response
from servidor import *
from unittest.mock import patch, MagicMock
from services import alterar_senha
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

@patch("routs.auth.valida_informacoes")
def test_registro_sucesso(mock_valida, client):
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

def test_produto(client):
    with patch("routs.auth.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Simula o produto retornado pelo banco
        mock_db.produtos.find_one.return_value = {
            "_id": "1",
            "titulo": "Camiseta",
            "descricao": "Camiseta preta básica",
            "quantidade": 10,
            "cor": "preto",
            "valor": 59.9,
            "desconto": 10,
            "tamanho": "M"
        }

        response = client.get("/auth/produto/1")

        assert response.status_code == 200

        #testa se está retornando corretamente cada item
        data = response.get_json()
        assert data["titulo"] == "Camiseta"
        assert data["valor"] == 59.9
        assert data["quantidade"] == 10

def test_produto_inexistente(client):
    #Testa se o produto existe
    with patch("routs.auth.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_db.produtos.find_one.return_value = None
        response = client.get("/auth/produto/1")

    assert response.status_code == 404

    data = response.get_json()
    assert "produto" in data
    assert data["erro"] == "Produto não encontrado"

def test_produto_id_inexistente(client):
    #Testa a ação de buscar um id inexistente
    with patch("routs.auth.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.produtos.find_one.return_value = None
        response = client.get("/auth/produto/-1")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Produto não encontrado"}

def test_alterar_senha(client):
    with patch("routs.auth.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Simula usuário existente no banco
        mock_db.users.find_one.return_value = {
            "email": "nicole@al.insper.edu.br",
            "senha_hash": "senha_antiga_hash"
        }

        response = client.get("/auth/alterar_senha", json={
            "email": "nicole@al.insper.edu.br"
        })

        assert response.status_code == 200

        data = response.get_json()
        assert data["senha_hash"] != "senha_antiga_hash"


def test_alterar_senha_email_inexistente(client):
    with patch("routs.auth.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Simula usuário não encontrado
        mock_db.users.find_one.return_value = None

        response = client.get("/auth/alterar_senha", json={
            "email": "inexistente@al.insper.edu.br"
        })

        assert response.status_code == 404

        data = response.get_json()
        assert data["erro"] == "Este email não está cadastrado."