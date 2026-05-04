from urllib import response
from servidor import *
from unittest.mock import patch, MagicMock
from datetime import datetime
from bson.objectid import ObjectId
from services.services_auth import alterar_senha

import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

@patch("rotas.user.get_db")
def test_produto_id(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    produto_id = ObjectId()

    mock_db.produtos.find_one.return_value = {
        "_id": produto_id,
        "titulo": "Camiseta",
        "descricao": "Camiseta preta básica",
        "quantidade": 10,
        "cor": "preto",
        "valor": 59.9,
        "desconto": 10,
        "tamanho": "M"
    }

    response = client.get(f"/user/produto/{produto_id}")

    assert response.status_code == 200

    data = response.get_json()
    assert data["titulo"] == "Camiseta"
    assert data["valor"] == 59.9
    assert data["quantidade"] == 10
    assert data["cor"] == "preto"
    assert data["valor"] == 59.9
    assert data["desconto"] == 10
    assert data["tamanho"] == "M"


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


@patch("rotas.user.buscar_perfil_usuario")
def test_perfil_usuario_nao_autenticado(mock_buscar, client):
    response = client.get("/user/perfil")

    assert response.status_code == 401
    assert response.get_json()["erro"] == "Usuário não autenticado"


@patch("rotas.user.buscar_perfil_usuario")
def test_perfil_usuario_com_reservas(mock_buscar, client):
    mock_buscar.return_value = {
        "usuario": {
            "nome": "Nicole",
            "email": "nicole@al.insper.edu.br"
        },
        "pendentes": [
            {
                "id": "507f1f77bcf86cd799439033",
                "produto": {
                    "id": "507f1f77bcf86cd799439022",
                    "nome": "Camiseta",
                    "descricao": "Preta",
                    "cor": "preto",
                    "tamanho": "M"
                },
                "quantidade": 1,
                "data_reserva": "2026-05-02",
                "data_retirada": "2026-05-03",
                "status": "ativa",
                "notificado": False
            }
        ],
        "historico": []
    }

    user_id = ObjectId("507f1f77bcf86cd799439011")

    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)

    response = client.get("/user/perfil")
    data = response.get_json()

    assert response.status_code == 200
    assert data["usuario"]["nome"] == "Nicole"
    assert data["usuario"]["email"] == "nicole@al.insper.edu.br"
    assert len(data["pendentes"]) == 1
    assert data["pendentes"][0]["produto"]["nome"] == "Camiseta"
    assert data["pendentes"][0]["data_retirada"] == "2026-05-03"
    assert data["historico"] == []


@patch("rotas.user.cancelar_reserva")
@patch("rotas.user.get_db")
def test_cancelar_reserva_usuario(mock_get_db, mock_cancelar, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_cancelar.return_value = {"sucesso": "Reserva cancelada com sucesso"}

    user_id = ObjectId("507f1f77bcf86cd799439011")
    reserva_id = ObjectId("507f1f77bcf86cd799439044")

    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)

    response = client.post(f"/user/reserva/{reserva_id}/cancelar")
    data = response.get_json()

    assert response.status_code == 200
    assert data["sucesso"] == "Reserva cancelada com sucesso"
    mock_cancelar.assert_called_once_with(mock_db, str(user_id), str(reserva_id))
    


@patch("rotas.adm.get_db")
@patch("rotas.adm.validar_produto_edicao")
def test_editar_produto_sucesso(mock_validar, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_validar.return_value = (
        {
            "nome": "Camiseta Nova",
            "descricao": "Camiseta preta atualizada",
            "cor": "preto",
            "tamanho": "M",
            "valor": 79.9,
            "quantidade": 8,
            "desconto": 10,
            "sku": "CAM-PRE-M",
            "file": None
        },
        None
    )

    mock_update_result = MagicMock()
    mock_update_result.matched_count = 1
    mock_db.produtos.update_one.return_value = mock_update_result

    mock_db.produtos.find_one.return_value = {
        "_id": "123456789012345678901234",
        "titulo": "Camiseta Nova",
        "descricao": "Camiseta preta atualizada",
        "cor": "preto",
        "tamanho": "M",
        "valor": 79.9,
        "quantidade": 8,
        "desconto": 10,
        "sku": "CAM-PRE-M"
    }

    response = client.put("/produto/123456789012345678901234")

    assert response.status_code == 200
    data = response.get_json()
    assert data["msg"] == "Produto atualizado"
    assert data["produto"]["titulo"] == "Camiseta Nova"
    
    
@patch("rotas.adm.get_db")
def test_delete_produto_sucesso(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 1
    mock_db.produtos.delete_one.return_value = mock_delete_result

    response = client.delete("/produto/123456789012345678901234")

    assert response.status_code == 200
    assert response.get_json() == {"msg": "Produto deletado com sucesso"}
    
    
    
@patch("rotas.adm.get_db")
@patch("rotas.adm.validar_produto_edicao")
def test_editar_produto_nao_encontrado(mock_validar, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_validar.return_value = (
        {
            "nome": "Camiseta Nova",
            "descricao": "Camiseta preta atualizada",
            "cor": "preto",
            "tamanho": "M",
            "valor": 79.9,
            "quantidade": 8,
            "desconto": 10,
            "sku": "CAM-PRE-M",
            "file": None
        },
        None
    )

    mock_update_result = MagicMock()
    mock_update_result.matched_count = 0
    mock_db.produtos.update_one.return_value = mock_update_result

    response = client.put("/produto/123456789012345678901234")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Produto não encontrado"}

    
    

@patch("rotas.adm.get_db")
def test_delete_produto_nao_encontrado(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # simula que não deletou nada
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 0
    mock_db.produtos.delete_one.return_value = mock_delete_result

    response = client.delete("/produto/123456789012345678901234")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Produto não encontrado"}
    
    

    
@patch("rotas.adm.get_db")
def test_listar_reservas_sucesso(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_db.reservas.find.return_value = [
        {
            "_id": "res1",
            "usuario_id": 5,
            "produto_id": 13,
            "quantidade": 1,
            "data_reserva": "2026-04-28T09:00:00Z",
            "data_retirada": "2026-04-30T09:00:00Z",
            "status": "ativa"
        }
    ]

    mock_db.users.find_one.return_value = {
        "_id": 5,
        "nome": "Maria",
        "email": "maria@email.com"
    }

    mock_db.produtos.find_one.return_value = {
        "_id": 13,
        "titulo": "Camiseta",
        "valor": 59.9
    }

    response = client.get("/reservas")

    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["usuario_id"] == 5
    assert data[0]["produto_id"] == 13
    assert data[0]["usuario"]["nome"] == "Maria"
    assert data[0]["produto"]["titulo"] == "Camiseta"
    
    
    
@patch("rotas.adm.get_db")
def test_listar_reservas_erro_banco(mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_db.reservas.find.side_effect = Exception("Erro no banco")

    with pytest.raises(Exception):
        client.get("/reservas")