from celery_app import Celery
from random import randint
from flask import render_template
from flask_mailman import EmailMessage,Mail
from servidor import criar_app
from celery_app import celery
from dotenv import load_dotenv


load_dotenv()
app = Celery(main='tasks',
             broker='pyamqp://guest@localhost//',
             backend='db+sqlite:///celery.sqlite')
flask_app = criar_app()
mail = Mail()
mail.init_app(flask_app)

@app.task
def enviar_email(to_email,codigo):
    try:
        with flask_app.app_context():
            html_body = render_template('email/verificacao.html',codigo=codigo)

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
        with flask_app.app_context():
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