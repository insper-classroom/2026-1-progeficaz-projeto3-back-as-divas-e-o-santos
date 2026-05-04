from urllib import response
from servidor import app
from services.services_user import criar_reserva
from unittest.mock import patch, MagicMock
import pytest   
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import mongomock
from tasks.tasks import verificar_reservas

def test_verificar_reservas_envia_email(monkeypatch):
    client = mongomock.MongoClient()
    db = client["test_db"]

    agora = datetime(2026, 5, 2) 
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    user_id = "user1"
    produto_id = "prod1"

    db.users.insert_one({
        "_id": user_id,
        "email": "teste@email.com"
    })

    db.produtos.insert_one({
        "_id": produto_id,
        "nome": "Notebook"
    })

    db.reservas.insert_one({
        "_id": "res1",
        "user_id": user_id,
        "produto_id": produto_id,
        "data_retirada": inicio,
        "status": "ativa",
        "notificado": False
    })

    chamadas = []

    def fake_delay(email, produto):
        chamadas.append((email, produto))

    monkeypatch.setenv("MONGO_URI", "fake")
    monkeypatch.setenv("MONGO_DB_NAME", "test_db")

    monkeypatch.setattr(
        "tasks.tasks.MongoClient",
        lambda *_: client
    )

    monkeypatch.setattr(
        "tasks.tasks.enviar_email.delay",
        fake_delay
    )

    monkeypatch.setattr(
        "tasks.tasks.datetime",
        type("MockDateTime", (), {
            "utcnow": staticmethod(lambda: agora)
        })
    )

    verificar_reservas()

    assert len(chamadas) == 1
    assert chamadas[0][0] == "teste@email.com"
    assert chamadas[0][1] == "Notebook"

    reserva = db.reservas.find_one({"_id": "res1"})
    assert reserva["notificado"] is True

def test_criar_reserva_sucesso():
    client = mongomock.MongoClient()
    db = client["test_db"]

    user_id = ObjectId()
    produto_id = ObjectId()
    
    db.produtos.insert_one({
        "_id": produto_id,
        "quantidade": 2
    })

    resultado = criar_reserva(
        db=db,
        user_id=str(user_id),
        produto_id=str(produto_id),
        data_str="2026-05-10"
    )

    assert resultado == {"sucesso": "Reserva criada com sucesso"}
    assert db.reservas.count_documents({}) == 1
    
def test_criar_reserva_produto_esgotado():
    client = mongomock.MongoClient()
    db = client["test_db"]

    produto_id = ObjectId()
    user_id = ObjectId()

    db.produtos.insert_one({
        "_id": produto_id,
        "estoque": 0
    })

    resultado = criar_reserva(
        db,
        str(user_id),
        str(produto_id),
        "2026-05-10"
    )

    assert resultado["erro"] == "Produto esgotado"

def test_criar_reserva_sucesso_rota(monkeypatch):

    mongo_client = mongomock.MongoClient()
    db = mongo_client["test_db"]

    monkeypatch.setattr(
        "rotas.user.get_db",
        lambda: db
    )

    user_id = ObjectId()
    produto_id = ObjectId()

    db.produtos.insert_one({
        "_id": produto_id,
        "quantidade": 2
    })
    
    with app.test_client() as client:
        response = client.post("/reservas", json={
            "user_id": str(user_id),
            "produto_id": str(produto_id),
            "data": "2026-05-10"
        })

    assert response.status_code == 200
    assert response.json["sucesso"] == "Reserva criada com sucesso"

def test_obter_reserva_id_inexistente(monkeypatch):

    mongo_client = mongomock.MongoClient()
    db = mongo_client["test_db"]

    monkeypatch.setattr(
        "rotas.user.get_db",
        lambda: db
    )
    

    reserva_id = ObjectId()

    with app.test_client() as client:
        response = client.get(f"/reservas/{reserva_id}")

    
    assert response.status_code == 404
    assert response.json["erro"] == "Reserva não encontrada"


def test_obter_reserva_sucesso(monkeypatch):

    mongo_client = mongomock.MongoClient()
    db = mongo_client["test_db"]

    monkeypatch.setattr(
        "rotas.user.get_db",
        lambda: db
    )
    reserva_id = ObjectId()


    db.reservas.insert_one({
        "_id": reserva_id,
        "user_id": ObjectId(),
        "produto_id": ObjectId(),
        "data_retirada": datetime(2026, 5, 10),
        "status": "ativa",
        "notificado": False
    })
    

    with app.test_client() as client:
        response = client.get(f"/reservas/{reserva_id}")


    assert response.status_code == 200
    assert response.json["_id"] == str(reserva_id)