from flask import request, Blueprint
from services.services_adm import validar_produto,criar_produto
import cloudinary
import cloudinary.uploader


adm_bp = Blueprint('admin', __name__)

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
