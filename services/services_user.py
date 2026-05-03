from bson.objectid import ObjectId
from datetime import datetime

def criar_reserva(db, user_id, produto_id, data_str):
    
    # 1. Converter IDs
    try:
        user_id = ObjectId(user_id)
        produto_id = ObjectId(produto_id)
    except Exception:
        return {"erro": "ID inválido"}
    
    # 2. Buscar produto
    produto = db.produtos.find_one({"_id": produto_id})
    if not produto:
        return {"erro": "Produto não encontrado"}
    
    # 3. Converter data
    try:
        data_retirada = datetime.strptime(data_str, "%Y-%m-%d")
    except Exception:
        return {"erro": "Data inválida"}
    
    # 4. Contar reservas ativas
    reservas_ativas = db.reservas.count_documents({
        "produto_id": produto_id,
        "status": "ativa"
    })
    
    estoque = produto.get("quantidade", 0)
    
    # 5. Verificar estoque
    if reservas_ativas >= estoque:
        return {"erro": "Produto esgotado"}
    
    # 6. Criar reserva
    db.reservas.insert_one({
        "usuario_id": user_id,
        "produto_id": produto_id,
        "quantidade": 1,
        "data_reserva": datetime.utcnow(),
        "data_retirada": data_retirada,
        "status": "ativa"
    })
    
    return {"sucesso": "Reserva criada com sucesso"}


def _serialize_produto(produto):
    if not produto:
        return {
            "id": None,
            "nome": "Produto removido",
            "descricao": None,
            "cor": None,
            "tamanho": None
        }

    return {
        "id": str(produto.get("_id")) if produto.get("_id") else None,
        "nome": produto.get("nome") or produto.get("titulo") or produto.get("descricao") or "Produto",
        "descricao": produto.get("descricao"),
        "cor": produto.get("cor"),
        "tamanho": produto.get("tamanho")
    }


def _serialize_reserva(reserva, produto):
    return {
        "id": str(reserva.get("_id")),
        "produto": _serialize_produto(produto),
        "quantidade": reserva.get("quantidade"),
        "data_reserva": reserva.get("data_reserva").strftime("%Y-%m-%d") if reserva.get("data_reserva") else None,
        "data_retirada": reserva.get("data_retirada").strftime("%Y-%m-%d") if reserva.get("data_retirada") else None,
        "status": reserva.get("status"),
        "notificado": reserva.get("notificado", False)
    }


def buscar_perfil_usuario(db, user_id):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return {"erro": "Usuário inválido"}
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        return {"erro": "Usuário não encontrado"}
    
    reservas = list(db.reservas.find({"usuario_id": user_id}))
    perfil_reservas = []

    for reserva in reservas:
        produto = db.produtos.find_one({"_id": reserva.get("produto_id")})
        perfil_reservas.append(_serialize_reserva(reserva, produto))

    pendentes = [r for r in perfil_reservas if r["status"] == "ativa"]
    historico = [r for r in perfil_reservas if r["status"] != "ativa"]

    return {
        "usuario": {
            "nome": user.get("nome"),
            "email": user.get("email")
        },
        "pendentes": pendentes,
        "historico": historico
    }


def cancelar_reserva(db, user_id, reserva_id):
    try:
        user_id = ObjectId(user_id)
        reserva_id = ObjectId(reserva_id)
    except Exception:
        return {"erro": "ID inválido"}

    reserva = db.reservas.find_one({"_id": reserva_id})
    if not reserva:
        return {"erro": "Reserva não encontrada"}

    if str(reserva.get("usuario_id")) != str(user_id):
        return {"erro": "Reserva não pertence ao usuário"}

    if reserva.get("status") == "cancelada":
        return {"erro": "Reserva já está cancelada"}

    db.reservas.update_one({"_id": reserva_id}, {"$set": {"status": "cancelada"}})
    return {"sucesso": "Reserva cancelada com sucesso"}