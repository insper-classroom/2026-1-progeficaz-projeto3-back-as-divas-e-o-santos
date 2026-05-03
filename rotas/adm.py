from flask import request, Blueprint
from banco import get_db
from services.services_adm import validar_produto, criar_produto, validar_produto_edicao
import cloudinary.uploader
from bson.objectid import ObjectId

adm_bp = Blueprint('admin', __name__)

@adm_bp.route('/produto', methods=['POST'])
def cadastro_de_produtos():
    data, error = validar_produto(request)

    if error:
        return error

    result = cloudinary.uploader.upload(data["file"])

    produto = criar_produto({
        **data,
        "image_url": result["secure_url"]
    })

    return {"msg": "Produto criado", "produto": produto}, 201


@adm_bp.route('/produto/<produto_id>', methods=['PUT'])
def editar_produto(produto_id):
    data, error = validar_produto_edicao(request)

    if error:
        return error

    db = get_db()

    try:
        obj_id = ObjectId(produto_id)
    except Exception:
        return {"error": "Produto não encontrado"}, 404

    update_data = {
        "titulo": data["nome"],
        "descricao": data["descricao"],
        "cor": data["cor"],
        "tamanho": data["tamanho"],
        "valor": data["valor"],
        "quantidade": data["quantidade"],
        "desconto": data["desconto"],
        "sku": data["sku"],
    }

    if data.get("file"):
        result = cloudinary.uploader.upload(data["file"])
        update_data["image_url"] = result["secure_url"]

    resultado = db.produtos.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if resultado.matched_count == 0:
        return {"error": "Produto não encontrado"}, 404

    produto_atualizado = db.produtos.find_one({"_id": obj_id})
    if produto_atualizado:
        produto_atualizado["_id"] = str(produto_atualizado["_id"])

    return {"msg": "Produto atualizado", "produto": produto_atualizado}, 200