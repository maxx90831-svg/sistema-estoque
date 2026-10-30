from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql
from routes.auth import login_obrigatorio
from validacoes import validar_produto

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


@produtos_bp.route('/')
@login_obrigatorio
def listar():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.*, c.nome AS categoria_nome
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.nome
    """)
    produtos = cursor.fetchall()
    return render_template('produtos/listar_produto.html', produtos=produtos)


@produtos_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_obrigatorio
def cadastrar():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nome FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria_id = request.form.get('categoria_id') or None
        quantidade = request.form.get('quantidade')
        preco = request.form.get('preco')
        peso = request.form.get('peso') or None
        unidade_peso = request.form.get('unidade_peso', 'kg')
        estoque_minimo = request.form.get('estoque_minimo') or 5
        
    
        erros = validar_produto(nome, quantidade, preco, unidade_peso, estoque_minimo)

        if erros:
            for erro in erros:
                flash(erro)
            return render_template('produtos/cadastrar.html', categorias=categorias)

        cursor_insert = mysql.connection.cursor()
        cursor_insert.execute("""
            INSERT INTO produtos (nome, categoria_id, quantidade, preco, peso, unidade_peso, estoque_minimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, categoria_id, quantidade, preco, peso, unidade_peso, estoque_minimo))
        mysql.connection.commit()

        return redirect(url_for('produtos.listar'))

    return render_template('produtos/cadastrar.html', categorias=categorias)


@produtos_bp.route('/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_obrigatorio
def editar(produto_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nome FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria_id = request.form.get('categoria_id') or None
        quantidade = request.form.get('quantidade')
        preco = request.form.get('preco')
        peso = request.form.get('peso') or None
        unidade_peso = request.form.get('unidade_peso', 'kg')
        estoque_minimo = request.form.get('estoque_minimo') or 5

        erros = validar_produto(nome, quantidade, preco, unidade_peso, estoque_minimo)

        if erros:
            for erro in erros:
                flash(erro)
            produto = {
                'id': produto_id,
                'nome': nome,
                'categoria_id': int(categoria_id) if categoria_id else None,
                'quantidade': quantidade,
                'preco': preco,
                'peso': peso,
                'unidade_peso': unidade_peso,
                'estoque_minimo': estoque_minimo,
            }
            return render_template('produtos/editar.html', produto=produto, categorias=categorias)

        cursor_update = mysql.connection.cursor()
        cursor_update.execute("""
            UPDATE produtos
            SET nome = %s, categoria_id = %s, quantidade = %s, preco = %s, peso = %s, unidade_peso = %s, estoque_minimo = %s
            WHERE id = %s
        """, (nome, categoria_id, quantidade, preco, peso, unidade_peso, estoque_minimo, produto_id))
        mysql.connection.commit()

        return redirect(url_for('produtos.listar'))

    cursor.execute('SELECT * FROM produtos WHERE id = %s', (produto_id,))
    produto = cursor.fetchone()

    if not produto:
        flash('Produto não encontrado.')
        return redirect(url_for('produtos.listar'))

    return render_template('produtos/editar.html', produto=produto, categorias=categorias)


@produtos_bp.route('/excluir/<int:produto_id>', methods=['POST'])
@login_obrigatorio
def excluir(produto_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = %s', (produto_id,))
    mysql.connection.commit()
    return redirect(url_for('produtos.listar'))