from werkzeug.security import check_password_hash,generate_password_hash
from email_validator import validate_email, EmailNotValidError
from flask import session
import secrets
from datetime import datetime, timedelta


 
def autenticar_usuario(db, email, pwd):
    try:
        email = validate_email(email).email
    except EmailNotValidError:
        return None, "Email inválido."

    user = db.users.find_one({"email": email})

    if not user or not check_password_hash(user['senha_hash'], pwd):
        return None, "Email ou senha inválidos."

    return user, None


def valida_informacoes(db,nome,email,pwd):
    try:
        v = validate_email(email)
        email = v.email
    except EmailNotValidError:
        return None, 'Email inválido'
    
    dominio = email.split("@")[-1]
    if dominio != "al.insper.edu.br":
        return None, "Use um email institucional da faculdade."

    if len(pwd) < 8:
        return None, "Senha muito curta. Use pelo menos 8 caracteres."

    row =  db.users.find_one({"email": email})
    if row:
        return None, 'Usuário já cadastrado.'
    
    pwd_hash = generate_password_hash(pwd)
    codigo = secrets.token_hex(3)
    expira = (datetime.utcnow() + timedelta(minutes=25)).strftime('%Y-%m-%d %H:%M:%S')

    user_doc = {
        "nome": nome,
        "email": email,
        "senha_hash": pwd_hash,
        "email_codigo": codigo,
        "codigo_expira": expira
    }
    result = db.users.insert_one(user_doc)


    try:
        from task import enviar_email
        enviar_email.delay(email, codigo)
    except Exception:
        print("Falha ao agendar enviar_email; verifique worker. Continuando...")

    return result, None


def alterar_senha(db,email):
    row  = db.users.find_one({"email": email})
    if not row:

        return None ,'Este email não está cadastrado.'
    else:
        try:
            from task import alterar_senha as task_alterar_senha
            task_alterar_senha.delay(email)
        except Exception:
            print("Falha ao agendar alterar_senha task; verifique worker.")

        return row, None



