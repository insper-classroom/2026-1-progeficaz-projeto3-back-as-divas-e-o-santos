from urllib import response
from servidor import *
from unittest.mock import patch, MagicMock
from services.services_auth import alterar_senha

import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

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

@patch("rotas.user.get_db")
def test_produto_id(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

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

    response = client.get("/user/produto/1")

    assert response.status_code == 200

    data = response.get_json()
    assert data["titulo"] == "Camiseta"
    assert data["valor"] == 59.9
    assert data["quantidade"] == 10


@patch("rotas.user.get_db")
def test_produto_id_inexistente(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_db.produtos.find_one.return_value = None

    response = client.get("/user/produto/-1")
    data = response.get_json()
    assert response.status_code == 404
    assert data['erro'] == "Produto não encontrado"

@patch("rotas.auth.get_db")
def test_alterar_senha_sucesso(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # usuário existe
    mock_db.users.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",

        "email": "nicole@al.insper.edu.br"
    }

    response = client.post("/auth/senha", data={   
        "email": "nicole@al.insper.edu.br"
    })

    assert response.status_code == 200


@patch("rotas.auth.get_db")
def test_alterar_senha_email_inexistente(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # usuário NÃO existe
    mock_db.users.find_one.return_value = None

    response = client.post("/auth/senha", data={
        "email": "inexistente@al.insper.edu.br"
    })

    assert response.status_code == 404

    data = response.get_json()
    assert data == None    

@patch("rotas.user.get_db")
def test_get_produtos_sucesso(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    mock_db.produtos.find.return_value = [
        {
            "_id": "1",
            "titulo": "Camiseta",
            "valor": 59.9,
            "quantidade": 10
        },
        {
            "_id": "2",
            "titulo": "Calça",
            "valor": 120.0,
            "quantidade": 5
        }
    ]

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["titulo"] == "Camiseta"
    assert data[1]["titulo"] == "Calça"