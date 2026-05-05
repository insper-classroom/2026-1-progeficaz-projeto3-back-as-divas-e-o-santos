from flask import request, Blueprint
from services.services_adm import validar_produto, criar_produto, buscar_dashboard_admin
from bson.objectid import ObjectId
from banco import get_db
from flask import request, Blueprint, jsonify
from banco import get_db
from services.services_adm import validar_produto, criar_produto, validar_produto_edicao, serializar_reserva
import cloudinary.uploader
from bson.objectid import ObjectId
from datetime import datetime

adm_bp = Blueprint('admin', __name__)


def produto_para_json(produto):
    return {
        "titulo": produto.get("titulo") or produto.get("nome"),
        "descricao": produto.get("descricao"),
        "quantidade": produto.get("quantidade"),
        "cor": produto.get("cor"),
        "valor": produto.get("valor"),
        "desconto": produto.get("desconto"),
        "tamanho": produto.get("tamanho"),
    }


@adm_bp.route('/cadastro/produto', methods=['POST'])
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

    return {"msg": "Produto criado", "produto": produto}


@adm_bp.route('/admin/produtos', methods=['GET'])
def listar_produtos_admin():
    try:
        db = get_db()
        produtos = list(db.produtos.find())
        return [produto_para_json(produto) for produto in produtos]
    except Exception as e:
        return {"erro": "Erro ao listar produtos"}, 500


@adm_bp.route('/admin/produtos/<produto_id>', methods=['GET'])
def visualizar_produto_admin(produto_id):
    try:
        db = get_db()
        try:
            obj_id = ObjectId(produto_id)
        except Exception:
            return {"erro": "ID de produto inválido"}, 404

        produto = db.produtos.find_one({"_id": obj_id})

        if not produto:
            return {"erro": "Produto não encontrado"}, 404

        return produto_para_json(produto)
    except Exception as e:
        return {"erro": "Erro ao consultar produto"}, 500


@adm_bp.route('/admin/dashboard', methods=['GET'])
def dashboard_admin():
    try:
        db = get_db()
        return buscar_dashboard_admin(db)
    except Exception as e:
        return {"erro": "Erro ao carregar dashboard"}, 500
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

@adm_bp.route('/produto/<produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    db = get_db()

    try:
        obj_id = ObjectId(produto_id)
    except Exception:
        return {"error": "Produto não encontrado"}, 404

    resultado = db.produtos.delete_one({"_id": obj_id})

    if resultado.deleted_count == 0:
        return {"error": "Produto não encontrado"}, 404

    return {"msg": "Produto deletado com sucesso"}, 200



@adm_bp.route('/reservas', methods=['GET'])
def listar_reservas():
    db = get_db()

    status = request.args.get("status")
    filtro = {}

    if status:
        filtro["status"] = status

    reservas = list(db.reservas.find(filtro))

    resultado = []

    for reserva in reservas:
        reserva = serializar_reserva(reserva)

        usuario_id = reserva.get("usuario_id")
        produto_id = reserva.get("produto_id")

        usuario = db.users.find_one({"_id": usuario_id})
        produto = db.produtos.find_one({"_id": produto_id})

        if usuario:
            usuario["_id"] = str(usuario["_id"])
            reserva["usuario"] = {
                "id": usuario["_id"],
                "nome": usuario.get("nome"),
                "email": usuario.get("email")
            }
        else:
            reserva["usuario"] = None

        if produto:
            produto["_id"] = str(produto["_id"])
            reserva["produto"] = {
                "id": produto["_id"],
                "titulo": produto.get("titulo"),
                "valor": produto.get("valor")
            }
        else:
            reserva["produto"] = None

        resultado.append(reserva)

    return jsonify(resultado), 200
