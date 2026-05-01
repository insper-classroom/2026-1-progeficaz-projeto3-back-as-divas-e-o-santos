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

@auth_bp.route('/login', methods=['POST'])
def login():
    db = get_db()
    
    if request.method == "POST":
        email = request.form.get('email', '').strip().lower()
        pwd = request.form.get('pwd', '')
 
        if not email or not pwd:
            flash("Preencha o email e a senha.", "error")
            return render_template('login.html')

        user, erro = autenticar_usuario(db, email, pwd)

        if erro:
            flash(erro, "error")
            return render_template('login.html')

        session.clear()
        session['user_id'] = str(user['_id'])

        flash('Login efetuado com sucesso.', "success")
        return redirect('/')

    return render_template('login.html')


@auth_bp.route('/registro', methods=['POST'])
def registro():
    db = get_db()
    
    if request.method == "POST":
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        raw_pwd = request.form.get('pwd', '')
        if not nome or not email or not raw_pwd:
            flash('Preencha todos os campos.', "error")
            return render_template('registro.html')
    
        user, erro = valida_informacoes(db=db, nome=nome, email=email, pwd=raw_pwd)

        if erro:
            flash(erro, "error")
            return render_template('login.html')
        
        session.clear() 
        session['id_verificacao'] = str(user.inserted_id)

        flash('Registro criado. Verifique seu email para confirmar.', "success")
        return redirect('/auth/login')  
    return render_template('registro.html')


@auth_bp.route('/senha', methods=['GET', 'POST'])
def alterar_senha():
    db = get_db()
    
    if request.method == 'POST':
        email  = request.form.get('email', '').strip().lower()
        if not email:
            flash('Informe o email para alterar a senha.', "error")
            return render_template('auth/email_alteracao.html')

        user, erro = alterar_senha(db,email)

        if erro:
            flash(erro, "error")
            return render_template('login.html')
        
        session.clear() 
        session['id_verificacao'] = str(user.inserted_id)
            
        flash('Enviamos instruções para alterar a senha (verifique seu email).', "success")
        return render_template('auth/email_alteracao.html')

    return render_template('auth/email_alteracao.html')