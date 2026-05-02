from flask import Blueprint, jsonify, session
from banco import get_db
from bson.objectid import ObjectId
from services.services_user import buscar_perfil_usuario, cancelar_reserva

user_bp = Blueprint('user', __name__)
sugestao_bp = Blueprint('sugestao', __name__)

@user_bp.route('/', methods=['GET'])
def homepage():
    db = get_db()

    produtos = list(db.produtos.find())

    for p in produtos:
        p["_id"] = str(p["_id"])

    return jsonify(produtos)


@user_bp.route('/user/produto/<produto_id>', methods=['GET'])
def produto(produto_id):
    db = get_db()

    try:
        obj_id = ObjectId(produto_id)
    except Exception:
        return {"erro": "Produto não encontrado"}, 404

    produto = db.produtos.find_one({"_id": obj_id})

    if not produto:
        return {"erro": "Produto não encontrado"}, 404

    produto["_id"] = str(produto["_id"])

    return jsonify(produto)


@user_bp.route('/user/perfil', methods=['GET'])
def perfil_usuario():
    user_id = session.get('user_id')
    if not user_id:
        return {"erro": "Usuário não autenticado"}, 401

    db = get_db()
    perfil = buscar_perfil_usuario(db, user_id)

    if "erro" in perfil:
        return perfil, 404

    return jsonify(perfil)


@user_bp.route('/user/reserva/<reserva_id>/cancelar', methods=['POST'])
def cancelar_reserva_usuario(reserva_id):
    user_id = session.get('user_id')
    if not user_id:
        return {"erro": "Usuário não autenticado"}, 401

    db = get_db()
    resultado = cancelar_reserva(db, user_id, reserva_id)

    if "erro" in resultado:
        status_code = 400
        if resultado["erro"] == "Reserva não encontrada":
            status_code = 404
        return resultado, status_code

    return jsonify(resultado)