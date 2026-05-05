from datetime import datetime
from banco import get_db
from bson.objectid import ObjectId



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
    
def validar_produto_edicao(request):
    nome = request.form.get('titulo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    cor = request.form.get('cor', '').strip()
    tamanho = request.form.get('tamanho', '').strip()

    valor = request.form.get('valor', '')
    quantidade = request.form.get('quantidade', '')
    desconto = request.form.get('desconto', '')

    if not nome or not descricao or not cor or not tamanho:
        return None, ({"error": "Campos obrigatórios faltando"}, 400)

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

    file = request.files.get('image')

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
    


def buscar_dashboard_admin(db, limite_estoque_baixo=5):
    agora = datetime.utcnow()
    inicio = datetime(agora.year, agora.month, agora.day)
    fim = inicio + timedelta(days=1)

    reservas_hoje = list(db.reservas.find({
        "data_reserva": {"$gte": inicio, "$lt": fim}
    }))

    produtos_vendidos = sum(reserva.get("quantidade", 0) for reserva in reservas_hoje)
    quantidade_reservas_hoje = len(reservas_hoje)
    produtos_estoque_baixo = db.produtos.count_documents({"quantidade": {"$lte": limite_estoque_baixo}})

    return {
        "produtos_vendidos": produtos_vendidos,
        "produtos_estoque_baixo": produtos_estoque_baixo,
        "reservas_hoje": quantidade_reservas_hoje
    }


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
    

def serializar_reserva(reserva):
    reserva["_id"] = str(reserva["_id"])

    if "usuario_id" in reserva and isinstance(reserva["usuario_id"], ObjectId):
        reserva["usuario_id"] = str(reserva["usuario_id"])

    if "produto_id" in reserva and isinstance(reserva["produto_id"], ObjectId):
        reserva["produto_id"] = str(reserva["produto_id"])

    if "data_reserva" in reserva and isinstance(reserva["data_reserva"], datetime):
        reserva["data_reserva"] = reserva["data_reserva"].isoformat()

    if "data_retirada" in reserva and isinstance(reserva["data_retirada"], datetime):
        reserva["data_retirada"] = reserva["data_retirada"].isoformat()

    return reserva