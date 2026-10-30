"""Regras de validação dos dados de produto.

Ficam isoladas das rotas para que possam ser testadas sem navegador
e sem banco de dados (testes de unidade).
"""

UNIDADES_VALIDAS = ('kg', 'l', 'ml')


def validar_produto(nome, quantidade, preco, unidade_peso, estoque_minimo):
    """Valida os dados de um produto e devolve a lista de mensagens de erro.
    Uma lista vazia significa que os dados são válidos.
    """
    erros = []

    if not nome or not str(nome).strip():
        erros.append('O nome do produto é obrigatório.')

    try:
        if int(quantidade) < 0:
            erros.append('A quantidade não pode ser negativa.')
    except (TypeError, ValueError):
        erros.append('Quantidade inválida.')

    try:
        if float(preco) < 0:
            erros.append('O preço não pode ser negativo.')
    except (TypeError, ValueError):
        erros.append('Preço inválido.')

    if unidade_peso not in UNIDADES_VALIDAS:
        erros.append('Selecione uma unidade válida.')

    try:
        if int(estoque_minimo) < 0:
            erros.append('O estoque mínimo não pode ser negativo.')
    except (TypeError, ValueError):
        erros.append('Estoque mínimo inválido.')

    return erros
