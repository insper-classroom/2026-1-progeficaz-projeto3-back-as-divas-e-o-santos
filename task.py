from celery import Celery
from random import randint
from flask import render_template
from flask_mailman import EmailMessage
from dotenv import load_dotenv
from servidor import *

load_dotenv()
celery = Celery(
    'tasks',
    broker='pyamqp://guest@localhost//',
    backend='db+sqlite:///celery.sqlite'
)

flask_app = criar_app()

mail = Mail()
mail.init_app(flask_app)


@celery.task
def enviar_email(to_email, codigo):
    try:
        with flask_app.app_context():
            html_body = render_template('email/verificacao.html', codigo=codigo)

            msg = EmailMessage(
                subject="Bem-vindo!",
                body="Seu cliente de e-mail não suporta HTML.",
                to=[to_email]
            )

            msg.content_subtype = "html"
            msg.body = html_body

            msg.send()
            print(f'email enviado para {to_email}')

    except Exception as e:
        print('erro ao enviar email', e)
        raise


@celery.task
def alterar_senha(email):
    try:
        with get_flask_app().app_context():
            html_body = render_template('email/alterar_senha.html')

            msg = EmailMessage(
                subject="Troca de senha",
                body="Seu cliente de e-mail não suporta HTML.",
                to=[email]
            )

            msg.content_subtype = "html"
            msg.body = html_body

            msg.send()
            print(f'email enviado para {email}')
    
    except Exception as e:
          print('erro ao enviar email',e)
          raise
    
@app.task
def enviar_email_sugestao(message, destinatarios):
    try:
        with flask_app.app_context():
            from flask import current_app
            from flask_mailman import EmailMessage

            body = f"Nova sugestão:\n\n{message}"

            msg = EmailMessage(
                subject="Sugestão recebida",
                body=body,
                to=destinatarios
            )

            msg.send()
            print(f"Sugestão enviada para {destinatarios}")

    except Exception as e:
        print("Erro ao enviar sugestão:", e)
        raise