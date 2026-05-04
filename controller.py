from banco import get_db
from dotenv import load_dotenv
import os



load_dotenv()

def processa_sugestao(data):
    from tasks.tasks import enviar_email_sugestao
    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return {"error": "Mensagem é obrigatória"}, 400

    if len(message) > 1000:
        return {"error": "Mensagem deve ter no máximo 1000 caracteres"}, 400

    admins = os.getenv("CONTACT_EMAIL")

    if not admins:
        return {"error": "Nenhum destinatário encontrado"}, 500

    try:
        enviar_email_sugestao.delay(message, admins)
    except Exception:
        return {"error": "Erro ao enviar email"}, 500

    return {"message": "Sugestão enviada para a fila com sucesso!"}, 201