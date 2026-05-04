from flask import request, Blueprint
from services.services_adm import validar_produto, criar_produto, buscar_dashboard_admin
from bson.objectid import ObjectId
from banco import get_db
import cloudinary.uploader


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
    db = get_db()
    produtos = list(db.produtos.find())
    return [produto_para_json(produto) for produto in produtos]


@adm_bp.route('/admin/produtos/<produto_id>', methods=['GET'])
def visualizar_produto_admin(produto_id):
    db = get_db()
    try:
        obj_id = ObjectId(produto_id)
    except Exception:
        return {"erro": "ID de produto inválido"}, 404

    produto = db.produtos.find_one({"_id": obj_id})

    if not produto:
        return {"erro": "Produto não encontrado"}, 404

    return produto_para_json(produto)


@adm_bp.route('/admin/dashboard', methods=['GET'])
def dashboard_admin():
    db = get_db()
    return buscar_dashboard_admin(db)
