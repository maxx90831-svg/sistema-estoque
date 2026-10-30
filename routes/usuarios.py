from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app import mysql
from routes.auth import admin_obrigatorio

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuarios_bp.route('/')
@admin_obrigatorio
def listar():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nome, email, cargo, criado_em FROM usuarios ORDER BY nome')
    usuarios = cursor.fetchall()
    return render_template('usuarios/listar_usuario.html', usuarios=usuarios)


@usuarios_bp.route('/cadastrar', methods=['GET', 'POST'])
@admin_obrigatorio
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        cargo = request.form.get('cargo')

        erros = []
        if not nome:
            erros.append('O nome é obrigatório.')
        if not email:
            erros.append('O e-mail é obrigatório.')
        if len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')
        if cargo not in ('funcionario', 'administrador'):
            erros.append('Selecione um cargo válido.')

        if erros:
            for erro in erros:
                flash(erro)
            return render_template('usuarios/cadastrar_usuario.html')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        if cursor.fetchone():
            flash('Já existe um usuário com esse e-mail.')
            return render_template('usuarios/cadastrar_usuario.html')

        senha_hash = generate_password_hash(senha)
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, cargo)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, senha_hash, cargo))
        mysql.connection.commit()

        flash('Usuário cadastrado com sucesso.')
        return redirect(url_for('usuarios.listar'))

    return render_template('usuarios/cadastrar_usuario.html')


@usuarios_bp.route('/excluir/<int:usuario_id>', methods=['POST'])
@admin_obrigatorio
def excluir(usuario_id):
    if usuario_id == session.get('usuario_id'):
        flash('Você não pode excluir o seu próprio usuário.')
        return redirect(url_for('usuarios.listar'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT cargo FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        flash('Usuário não encontrado.')
        return redirect(url_for('usuarios.listar'))

    if usuario['cargo'] == 'administrador':
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE cargo = 'administrador'")
        total_admins = cursor.fetchone()['total']
        if total_admins <= 1:
            flash('Não é possível excluir o último administrador do sistema.')
            return redirect(url_for('usuarios.listar'))

    cursor.execute('DELETE FROM usuarios WHERE id = %s', (usuario_id,))
    mysql.connection.commit()
    flash('Usuário excluído com sucesso.')
    return redirect(url_for('usuarios.listar'))