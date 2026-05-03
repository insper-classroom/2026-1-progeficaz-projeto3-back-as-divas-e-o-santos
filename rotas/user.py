from flask import Blueprint, jsonify, request
from banco import get_db
from bson.objectid import ObjectId
from services.services_user import criar_reserva

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
        obj_id = (produto_id)
    except:
        return {"erro": "Produto não encontrado"}, 404

    produto = db.produtos.find_one({"_id": obj_id})

    if not produto:
        return {"erro": "Produto não encontrado"}, 404

    produto["_id"] = str(produto["_id"])

    return jsonify(produto)

@user_bp.route('/reservas', methods=['POST'])
def criar_reserva_route():
    db = get_db()

    data = request.get_json()

    resultado = criar_reserva(
        db=db,
        user_id=data.get("user_id"),
        produto_id=data.get("produto_id"),
        data_str=data.get("data")
    )

    if "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify(resultado), 200

@user_bp.route('/reservas/<reserva_id>', methods=['GET'])
def obter_reserva(reserva_id):
    db = get_db()

    try:
        obj_id = ObjectId(reserva_id)
    except:
        return {"erro": "ID inválido"}, 400

    reserva = db.reservas.find_one({"_id": obj_id})

    if not reserva:
        return {"erro": "Reserva não encontrada"}, 404

    reserva["_id"] = str(reserva["_id"])
    reserva["user_id"] = str(reserva["user_id"])
    reserva["produto_id"] = str(reserva["produto_id"])
    reserva["data_retirada"] = reserva["data_retirada"].isoformat()

    return jsonify(reserva), 200