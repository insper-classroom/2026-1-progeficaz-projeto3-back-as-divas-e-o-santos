from banco import get_db
from services_pasta.user import encontra_emails_admin

def processa_sugestao(data):
    from task import enviar_email_sugestao
    db = get_db()
    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return {"error": "Mensagem é obrigatória"}, 400

    if len(message) > 1000:
        return {"error": "Mensagem deve ter no máximo 1000 caracteres"}, 400

    admins = encontra_emails_admin(db)

    if not admins:
        return {"error": "Nenhum destinatário encontrado"}, 500

    try:
        enviar_email_sugestao.delay(message, admins)
    except Exception:
        return {"error": "Erro ao enviar email"}, 500

    return {"message": "Sugestão enviada para a fila com sucesso!"}, 201