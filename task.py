from celery import Celery
from random import randint
from flask import render_template
from flask_mailman import EmailMessage
from dotenv import load_dotenv
 

load_dotenv()
app = Celery(main='tasks',
             broker='pyamqp://guest@localhost//',
             backend='db+sqlite:///celery.sqlite')


def get_flask_app():
    from servidor import criar_app
    flask_app = criar_app()
    return flask_app

@app.task
def enviar_email(to_email,codigo):
    try:
        with get_flask_app().app_context():
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
          print('erro ao envia o email',e)
          raise
    

@app.task
def alterar_senha(email):
    try:
        with get_flask_app().app_context():
            html_body = render_template('email/alterar_senha.html')

            msg = EmailMessage(
            subject="Toca de senha",    
            body="Seu cliente de e-mail não suporta HTML.",
            to=[email]
        )

            msg.content_subtype = "html"
            msg.body = html_body

            msg.send()
            print(f'email enviado para {email}')
    except Exception as e:
          print('erro ao envia o email',e)
          raise