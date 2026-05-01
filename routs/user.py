from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages, Blueprint, jsonify
from dotenv import load_dotenv
from banco import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mailman import EmailMessage, Mail
import os
import secrets
from datetime import datetime, timedelta
from services import autenticar_usuario, valida_informacoes

auth_bp = Blueprint('login',__name__)

@auth_bp.route('/produto/<produto_id>', methods=['GET'])
def produto(produto_id):
    db = get_db()
    if produto_id.startswith('-'):
        return {"erro": "Produto não encontrado"}, 404

    produto = db.produtos.find_one({"_id": produto_id})
    if not produto:
        return {"erro": "Produto não encontrado", "produto": None}, 404

    return produto
