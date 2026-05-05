from flask import render_template, redirect, request, session, flash, Blueprint
from banco import get_db
from services import autenticar_usuario, valida_informacoes
from services import alterar_senha as service_alterar_senha

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
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


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    db = get_db()
    
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados."}, 500

    if request.method == "POST":
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        raw_pwd = request.form.get('pwd', '')

        if not nome or not email or not raw_pwd:
            return {"erro": "Preencha todos os campos."}, 400

        user, erro = valida_informacoes(db=db, nome=nome, email=email, pwd=raw_pwd)
    
        if erro:
            return {"erro": erro}, 400

        session.clear()
        session['id_verificacao'] = str(user.inserted_id)

        flash('Registro criado. Verifique seu email para confirmar.', "success")
        return redirect('/auth/login')

    return render_template('registro.html')


@auth_bp.route('/senha', methods=['GET', 'POST'])
def alterar_senha():
    db = get_db()

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Informe o email para alterar a senha.', "error")
            return render_template('auth/email_alteracao.html')

        user, erro = service_alterar_senha(db, email)

        if erro:
            flash(erro, "error")
            return render_template('login.html'), 404

        session.clear()
        session['id_verificacao'] = str(user['_id'])

        flash(
            'Enviamos instruções para alterar a senha (verifique seu email).',
            "success"
        )
        return render_template('auth/email_alteracao.html')

    return render_template('auth/email_alteracao.html')

