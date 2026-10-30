"""Testes de unidade: regras de validação de produto (sem banco e sem navegador)."""
import pytest

from validacoes import validar_produto


def _validar(**alteracoes):
    dados = dict(nome='Arroz 5 kg', quantidade='10', preco='25.90',
                 unidade_peso='kg', estoque_minimo='5')
    dados.update(alteracoes)
    return validar_produto(**dados)


def test_dados_validos_nao_geram_erros():
    assert _validar() == []


@pytest.mark.parametrize('nome', ['', '   ', None])
def test_nome_vazio_e_recusado(nome):
    assert 'O nome do produto é obrigatório.' in _validar(nome=nome)


@pytest.mark.parametrize('quantidade', ['-1', '-100'])
def test_quantidade_negativa_e_recusada(quantidade):
    assert 'A quantidade não pode ser negativa.' in _validar(quantidade=quantidade)


@pytest.mark.parametrize('quantidade', ['abc', '', None, '1.5'])
def test_quantidade_nao_inteira_e_recusada(quantidade):
    assert 'Quantidade inválida.' in _validar(quantidade=quantidade)


def test_quantidade_zero_e_aceita():
    assert _validar(quantidade='0') == []


@pytest.mark.parametrize('preco', ['-0.01', '-10'])
def test_preco_negativo_e_recusado(preco):
    assert 'O preço não pode ser negativo.' in _validar(preco=preco)


@pytest.mark.parametrize('preco', ['abc', '', None])
def test_preco_nao_numerico_e_recusado(preco):
    assert 'Preço inválido.' in _validar(preco=preco)


def test_preco_zero_e_aceito():
    assert _validar(preco='0') == []


@pytest.mark.parametrize('unidade', ['kg', 'l', 'ml'])
def test_unidades_permitidas_sao_aceitas(unidade):
    assert _validar(unidade_peso=unidade) == []


@pytest.mark.parametrize('unidade', ['g', 'litro', '', None])
def test_unidade_fora_da_lista_e_recusada(unidade):
    assert 'Selecione uma unidade válida.' in _validar(unidade_peso=unidade)


def test_estoque_minimo_negativo_e_recusado():
    assert 'O estoque mínimo não pode ser negativo.' in _validar(estoque_minimo='-1')


def test_estoque_minimo_invalido_e_recusado():
    assert 'Estoque mínimo inválido.' in _validar(estoque_minimo='abc')


def test_varios_erros_sao_acumulados():
    erros = _validar(nome='', quantidade='-5', preco='-1')
    assert len(erros) == 3
