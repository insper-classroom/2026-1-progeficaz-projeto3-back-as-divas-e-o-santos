from flask import Blueprint, jsonify, session
from banco import get_db
from bson.objectid import ObjectId
from services.services_user import buscar_perfil_usuario, cancelar_reserva,criar_reserva
from flask import Blueprint, jsonify, request
from banco import get_db
from bson.objectid import ObjectId
from controller import processa_sugestao

user_bp = Blueprint('user', __name__)
sugestao_bp = Blueprint('sugestao', __name__)

@user_bp.route('/', methods=['GET'])
def homepage():
    db = get_db()

    produtos = list(db.produtos.find())

    for p in produtos:
        p["_id"] = str(p["_id"])

    return jsonify(produtos), 200


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

    return jsonify(produto), 200


@user_bp.route('/user/perfil', methods=['GET'])
def perfil_usuario():
    user_id = session.get('user_id')
    if not user_id:
        return {"erro": "Usuário não autenticado"}, 401

    db = get_db()
    perfil = buscar_perfil_usuario(db, user_id)

    if "erro" in perfil:
        return perfil, 404

    return jsonify(perfil), 200

@sugestao_bp.route("", methods=["POST"])
def envia_sugestao():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON inválido"}), 400

    response, status = processa_sugestao(data)
    return jsonify(response), status


@user_bp.route('/user/reserva/<reserva_id>/cancelar', methods=['POST'])
def cancelar_reserva_usuario(reserva_id):
    user_id = session.get('user_id')
    if not user_id:
        return {"erro": "Usuário não autenticado"}, 401
    
    try:
        reserva_id = ObjectId(reserva_id)
    except Exception:
            return {"erro": "ID inválido"}, 400

    db = get_db()
    resultado = cancelar_reserva(db, user_id, reserva_id)

    if "erro" in resultado:
        status_code = 400
        if resultado["erro"] == "Reserva não encontrada":
            status_code = 404
        return resultado, status_code

    return jsonify(resultado)

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




@user_bp.route('/configuracoes/<user_id>', methods=['POST'])
def configuracao(user_id):

    user_id = session.get('user_id')
    if not user_id:
        return {"erro": "Usuário não autenticado"}, 401

    db = get_db()
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"erro": "Dados não encontrados"}), 400
    notificacoes_push = data.get("notificacoes_push")
    promocoes_email = data.get("promocoes_email")

    db.users.update_one({'_id': ObjectId(user_id)},
    {"$set": {"notificacoes_push": notificacoes_push, "promocoes_email": promocoes_email}})


    return {"sucesso": "Dados atualizado com sucesso"}, 200

