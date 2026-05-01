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
    
    estoque = produto.get("estoque", 0)
    
    # 5. Verificar estoque
    if reservas_ativas >= estoque:
        return {"erro": "Produto esgotado"}
    
    # 6. Criar reserva
    db.reservas.insert_one({
        "user_id": user_id,
        "produto_id": produto_id,
        "data_retirada": data_retirada,
        "status": "ativa",
        "notificado": False
    })
    
    return {"sucesso": "Reserva criada com sucesso"}