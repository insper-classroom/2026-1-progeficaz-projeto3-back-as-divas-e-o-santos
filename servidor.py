from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages
from dotenv import load_dotenv
from banco import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mailman import EmailMessage, Mail
import os
import secrets
from datetime import datetime, timedelta
from routs.auth import auth_bp

load_dotenv() 

def criar_app():
    app = Flask(__name__, instance_relative_config=True)


    app.config.from_mapping(
        SECRET_KEY = os.environ['SECRET_KEY'],
        DATABASE = r".\banco.db",
        JSON_SORT_KEYS = False,
    )



    app.config.update(
        MAIL_SERVER = os.environ.get("MAIL_SERVER"),
        MAIL_PORT = int(os.environ.get("MAIL_PORT", 587)) if os.environ.get("MAIL_PORT") else None,
        MAIL_USE_TLS = (os.environ.get("MAIL_USE_TLS", "false").lower() == "true"),
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER"),
    )


    try:
        app.register_blueprint(auth_bp, url_prefix='/alterar')
    except Exception:

        pass

    @app.context_processor
    def inject_flashes():

        return {'flashed_messages': get_flashed_messages(with_categories=True)}

    return app


app = criar_app()

@app.route('/')
def root():
    if 'user_id' in session:
        return redirect('/home')
    return redirect('/auth/login')

if __name__ == '__main__':
    app.run(debug=True) 

teste merge