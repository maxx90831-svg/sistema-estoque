from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from app import mysql
from routes.auth import login_obrigatorio

movimentacoes_bp = Blueprint('movimentacoes', __name__, url_prefix='/movimentacoes')


@movimentacoes_bp.route('/entrada', methods=['POST'])
@login_obrigatorio
def entrada():
    produto_id = request.form.get('produto_id')
    quantidade = int(request.form.get('quantidade', 0))

    if quantidade <= 0:
        flash('A quantidade de entrada deve ser maior que zero.')
        return redirect(url_for('produtos.listar'))

    cursor = mysql.connection.cursor()
    cursor.execute(
        'UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s',
        (quantidade, produto_id)
    )
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade) VALUES (%s, %s, 'entrada', %s)",
        (produto_id, session.get('usuario_id'), quantidade)
    )
    mysql.connection.commit()
    return redirect(url_for('produtos.listar'))


@movimentacoes_bp.route('/saida', methods=['POST'])
@login_obrigatorio
def saida():
    produto_id = request.form.get('produto_id')
    quantidade = int(request.form.get('quantidade', 0))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT quantidade FROM produtos WHERE id = %s', (produto_id,))
    produto = cursor.fetchone()

    if not produto or quantidade <= 0 or quantidade > produto['quantidade']:
        flash('Quantidade de saída inválida ou maior que o estoque disponível.')
        return redirect(url_for('produtos.listar'))

    cursor.execute(
        'UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s',
        (quantidade, produto_id)
    )
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade) VALUES (%s, %s, 'saida', %s)",
        (produto_id, session.get('usuario_id'), quantidade)
    )
    mysql.connection.commit()
    return redirect(url_for('produtos.listar'))


@movimentacoes_bp.route('/historico/<int:produto_id>')
@login_obrigatorio
def historico(produto_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nome FROM produtos WHERE id = %s', (produto_id,))
    produto = cursor.fetchone()

    if not produto:
        flash('Produto não encontrado.')
        return redirect(url_for('produtos.listar'))

    cursor.execute("""
        SELECT m.*, u.nome AS usuario_nome
        FROM movimentacoes m
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE m.produto_id = %s
        ORDER BY m.data_movimentacao DESC
    """, (produto_id,))
    movimentacoes = cursor.fetchall()

    return render_template('movimentacoes/historico.html', produto=produto, movimentacoes=movimentacoes)