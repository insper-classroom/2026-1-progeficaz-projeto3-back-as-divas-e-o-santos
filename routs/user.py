from flask import Blueprint, request, jsonify
from controller import processa_sugestao

sugestao_bp = Blueprint("sugestoes", __name__)

@sugestao_bp.route("", methods=["POST"])
def envia_sugestao():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON inválido"}), 400

    response, status = processa_sugestao(data)
    return jsonify(response), status