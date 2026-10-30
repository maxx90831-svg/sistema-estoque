from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app import mysql

auth_bp = Blueprint('auth', __name__)


def login_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para continuar.')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapper


def admin_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para continuar.')
            return redirect(url_for('auth.login'))
        if session.get('usuario_cargo') != 'administrador':
            flash('Apenas administradores podem acessar essa área.')
            return redirect(url_for('produtos.listar'))
        return view_func(*args, **kwargs)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['senha_hash'], senha):
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_cargo'] = usuario['cargo']
            return redirect(url_for('produtos.listar'))

        flash('E-mail ou senha inválidos.')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))