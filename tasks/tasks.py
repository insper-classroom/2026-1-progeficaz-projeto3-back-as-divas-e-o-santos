from random import randint
from flask import render_template
from flask_mailman import EmailMessage,Mail
from servidor import criar_app
from celery import shared_task
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
import os


load_dotenv()
flask_app = criar_app()
mail = Mail()
mail.init_app(flask_app)

@shared_task
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
    

@shared_task
def verificar_reservas():
    print("rodando verificação...")

    mongo_uri = os.getenv("MONGO_URI")

    with MongoClient(mongo_uri) as client:
        db = client[os.getenv("MONGO_DB_NAME")]

        agora = datetime.utcnow()

        hoje_00 = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        inicio = hoje_00 + timedelta(days=1)
        fim = inicio + timedelta(days=1)

        reservas = db.reservas.find({
            "data_retirada": {
                "$gte": inicio,
                "$lt": fim
            },
            "status": "ativa",
            "notificado": False
        })

        for r in reservas:
            user = db.users.find_one({"_id": r["user_id"]})
            if not user:
                continue

            if not user.get("notificar_email"):
                continue

            produto = db.produtos.find_one({"_id": r["produto_id"]})
            if not produto:
                continue

            enviar_email.delay(
                user["email"],
                produto["nome"]
            )

            db.reservas.update_one(
                {"_id": r["_id"]},
                {"$set": {"notificado": True}}
            )

    print("verificação finalizada")