from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages
from dotenv import load_dotenv
from banco import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mailman import EmailMessage, Mail
import os
import secrets
from datetime import datetime, timedelta
from rotas.auth import auth_bp
from rotas.user import sugestao_bp,user_bp
from rotas.adm import adm_bp
import cloudinary
import cloudinary.uploader
import unittest



load_dotenv() 


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def criar_app():
    app = Flask(__name__, instance_relative_config=True)


    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key'),
        JSON_SORT_KEYS = False,
    )



    app.config.update(
        MAIL_SERVER = os.environ.get("MAIL_SERVER"),
        MAIL_PORT = int(os.environ.get("MAIL_PORT", 587)) if os.environ.get("MAIL_PORT") else None,
        MAIL_USE_TLS = (os.environ.get("MAIL_USE_TLS", "false").lower() == "true"),
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER"),
        EMAIL_HOST = os.getenv("EMAIL_HOST"),
        EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465)),
        EMAIL_USER = os.getenv("EMAIL_USER"),
        EMAIL_PASS = os.getenv("EMAIL_PASS"),
    )



    try:
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except Exception:

        pass

    app.register_blueprint(sugestao_bp, url_prefix='/api/sugestoes')

    @app.context_processor
    def inject_flashes():

        return {'flashed_messages': get_flashed_messages(with_categories=True)}

    return app


app = criar_app()

app.register_blueprint(user_bp)
app.register_blueprint(adm_bp)

app.register_blueprint(adm_bp)


if __name__ == '__main__':
    app.run(debug=True) 
