from flask import Blueprint, jsonify
from banco import get_db
from bson.objectid import ObjectId

user_bp = Blueprint('user', __name__)
sugestao_bp = Blueprint('sugestao', __name__)

@user_bp.route('/', methods=['GET'])
def homepage():
    db = get_db()

    try:
        produtos = list(db.produtos.find())

        for p in produtos:
            p["_id"] = str(p["_id"])

        return jsonify(produtos)

    except Exception:
        return jsonify({"erro": "Erro ao buscar produtos"}), 500

@user_bp.route('/produto/<produto_id>', methods=['GET'])
def produto(produto_id):
    db = get_db()

    try:
        obj_id = ObjectId(produto_id)
    except:
        return {"erro": "Produto não encontrado"}, 404

    produto = db.produtos.find_one({"_id": obj_id})

    if not produto:
        return {"erro": "Produto não encontrado"}, 404

    produto["_id"] = str(produto["_id"])

    return jsonify(produto)