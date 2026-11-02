"""Testes da correção: quantidade vazia, não numérica ou ausente em entradas e saídas."""
import pytest

from conftest import texto
from validacoes import converter_quantidade


@pytest.mark.parametrize('valor, esperado', [
    ('5', 5),
    ('0', 0),
    ('-3', -3),
    (' 7 ', 7),
])
def test_converter_quantidade_aceita_numeros_inteiros(valor, esperado):
    assert converter_quantidade(valor) == esperado


@pytest.mark.parametrize('valor', ['', 'abc', '1.5', None])
def test_converter_quantidade_recusa_valores_invalidos(valor):
    assert converter_quantidade(valor) is None


@pytest.mark.parametrize('rota', ['/movimentacoes/entrada', '/movimentacoes/saida'])
@pytest.mark.parametrize('valor', ['', 'abc', '1.5', None])
def test_movimentacao_sem_quantidade_valida_e_recusada(client_admin, produto, consultar, rota, valor):
    dados = {'produto_id': produto['id']}
    if valor is not None:
        dados['quantidade'] = valor

    resposta = client_admin.post(rota, data=dados, follow_redirects=True)

    assert resposta.status_code == 200
    assert 'Informe uma quantidade válida' in texto(resposta)
    saldo = consultar('SELECT quantidade FROM produtos WHERE id = %s', (produto['id'],))[0]['quantidade']
    assert saldo == 10
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_entrada_em_produto_inexistente_e_recusada(client_admin, consultar):
    resposta = client_admin.post('/movimentacoes/entrada',
                                 data={'produto_id': '999999', 'quantidade': '1'},
                                 follow_redirects=True)
    assert 'Produto não encontrado.' in texto(resposta)
    assert consultar('SELECT * FROM movimentacoes') == ()