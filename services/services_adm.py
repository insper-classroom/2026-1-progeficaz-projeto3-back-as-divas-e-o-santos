from flask import session
import secrets
from datetime import datetime, timedelta
from banco import get_db



def gerar_sku(nome, cor, tamanho):
    return f"{nome[:3].upper()}-{cor[:3].upper()}-{tamanho.upper()}"


def validar_produto(request):
    nome = request.form.get('titulo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    cor = request.form.get('cor', '').strip()
    tamanho = request.form.get('tamanho', '').strip()

    valor = request.form.get('valor', '')
    quantidade = request.form.get('quantidade', '')
    desconto = request.form.get('desconto', '')

    if not nome or not descricao or not cor or not tamanho:
        return None, ({"error": "Campos obrigatórios faltando"}, 400)

    if 'image' not in request.files:
        return None, ({"error": "Imagem obrigatória"}, 400)

    file = request.files['image']

    if file.filename == '':
        return None, ({"error": "Arquivo inválido"}, 400)

    try:
        valor = float(valor)
        quantidade = int(quantidade)
        desconto = float(desconto)
    except:
        return None, ({"error": "Dados numéricos inválidos"}, 400)

    if valor <= 0:
        return None, ({"error": "Preço inválido"}, 400)

    if quantidade < 0:
        return None, ({"error": "Quantidade inválida"}, 400)

    if desconto < 0 or desconto > 100:
        return None, ({"error": "Desconto inválido"}, 400)

    sku = gerar_sku(nome, cor, tamanho)

    return {
        "nome": nome,
        "descricao": descricao,
        "cor": cor,
        "tamanho": tamanho,
        "valor": valor,
        "quantidade": quantidade,
        "desconto": desconto,
        "sku": sku,
        "file": file
    }, None

def criar_produto(data):
    db = get_db()

    produto = {
        "nome": data["nome"],
        "descricao": data["descricao"],
        "valor": data["valor"],
        "desconto": data["desconto"],
        "valor_final": data["valor"] - (data["valor"] * data["desconto"] / 100),
        "quantidade": data["quantidade"],
        "cor": data["cor"],
        "tamanho": data["tamanho"],
        "sku": data["sku"],
        "image_url": data["image_url"],
        "created_at": datetime.utcnow()
    }

    try:
        result = db.produtos.insert_one(produto)

        return {
            "id": str(result.inserted_id),
            "sku": produto["sku"]
        }

    except Exception as e:
        return {"error": "Erro ao salvar produto"}