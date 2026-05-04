from urllib import response
import os
from unittest.mock import patch, MagicMock
import pytest
from bson.objectid import ObjectId
from servidor import app
import mongomock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@patch("rotas.user.get_db")
def test_configuracoes_usuario_nao_autenticado(mock_get_db, client):
    user_id = str(ObjectId("507f1f77bcf86cd799439044"))

    response = client.post(f"/configuracoes/{user_id}")

    assert response.status_code == 401
    assert response.get_json()["erro"] == "Usuário não autenticado"

@patch("rotas.user.get_db")
def test_configuracoes_dados_nao_encontrados(mock_get_db, client):
    user_id = str(ObjectId("507f1f77bcf86cd799439044"))
    
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(f"/configuracoes/{user_id}")

    assert response.status_code == 400
    assert response.get_json()["erro"] == "Dados não encontrados"



@patch("rotas.user.get_db")
def test_configuracoes_dados_nao_encontrados(mock_get_db, client):
    user_id = str(ObjectId("507f1f77bcf86cd799439044"))

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        f"/configuracoes/{user_id}",
        data="",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Dados não encontrados"}

@patch("rotas.user.get_db")
def test_configuracoes_sucesso(mock_get_db, client):
    # banco fake
    mongo_client = mongomock.MongoClient()
    db = mongo_client["test_db"]
    mock_get_db.return_value = db

    user_id = ObjectId("507f1f77bcf86cd799439011")

    # cria usuário
    db.users.insert_one({
        "_id": user_id,
        "notificacoes_push": False,
        "promocoes_email": False
    })

    # seta session (ESSENCIAL)
    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)

    response = client.post(
        f"/configuracoes/{user_id}",
        json={
            "notificacoes_push": True,
            "promocoes_email": True
        }
    )

    assert response.status_code == 200
    assert response.get_json()["sucesso"] == "Dados atualizado com sucesso"

    # valida atualização no banco
    user = db.users.find_one({"_id": user_id})
    assert user["notificacoes_push"] is True
    assert user["promocoes_email"] is True