from flask import render_template
from flask_mailman import EmailMessage, Mail
from celery import Celery
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from celery_app import celery

load_dotenv()

mail = Mail()


def get_app():
    from servidor import criar_app
    app = criar_app()
    mail.init_app(app)
    return app


@celery.task
def enviar_email(to_email, codigo):
    try:
        app = get_app()
        with app.app_context():
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
        app = get_app()
        with app.app_context():
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
        print('erro ao enviar email', e)
        raise


@celery.task
def verificar_reservas():
    print("rodando verificação...")

    mongo_uri = os.getenv("MONGO_URI")

    with MongoClient(mongo_uri) as client:
        db = client[os.getenv("MONGO_DB_NAME")]

        agora = datetime.utcnow()
        inicio = (agora.replace(hour=0, minute=0, second=0, microsecond=0)
                  + timedelta(days=1))
        fim = inicio + timedelta(days=1)

        reservas = db.reservas.find({
            "data_retirada": {"$gte": inicio, "$lt": fim},
            "status": "ativa",
            "notificado": False
        })

        for r in reservas:
            user = db.users.find_one({"_id": r["user_id"]})
            produto = db.produtos.find_one({"_id": r["produto_id"]})

            if not user or not produto:
                continue

            enviar_email.delay(user["email"], produto["nome"])

            db.reservas.update_one(
                {"_id": r["_id"]},
                {"$set": {"notificado": True}}
            )

    print("verificação finalizada")