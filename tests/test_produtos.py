"""Testes de integração: cadastro, edição, exclusão e listagem de produtos."""
from conftest import texto

DADOS_VALIDOS = {
    'nome': 'Refrigerante 2L',
    'categoria_id': '2',
    'quantidade': '12',
    'estoque_minimo': '4',
    'preco': '8.50',
    'peso': '2',
    'unidade_peso': 'l',
}


def test_cadastro_valido_grava_o_produto(client_admin, consultar):
    resposta = client_admin.post('/produtos/cadastrar', data=DADOS_VALIDOS)
    assert resposta.status_code == 302

    registros = consultar("SELECT * FROM produtos WHERE nome = 'Refrigerante 2L'")
    assert len(registros) == 1
    assert registros[0]['quantidade'] == 12
    assert registros[0]['unidade_peso'] == 'l'
    assert registros[0]['estoque_minimo'] == 4


def test_cadastro_sem_peso_e_sem_categoria_grava_nulo(client_admin, consultar):
    dados = dict(DADOS_VALIDOS, peso='', categoria_id='')
    client_admin.post('/produtos/cadastrar', data=dados)

    registro = consultar("SELECT * FROM produtos WHERE nome = 'Refrigerante 2L'")[0]
    assert registro['peso'] is None
    assert registro['categoria_id'] is None


def test_cadastro_sem_nome_e_recusado(client_admin, consultar):
    resposta = client_admin.post('/produtos/cadastrar', data=dict(DADOS_VALIDOS, nome=''))
    assert 'O nome do produto é obrigatório.' in texto(resposta)
    assert consultar('SELECT * FROM produtos') == ()


def test_cadastro_com_quantidade_negativa_e_recusado(client_admin, consultar):
    resposta = client_admin.post('/produtos/cadastrar', data=dict(DADOS_VALIDOS, quantidade='-3'))
    assert 'A quantidade não pode ser negativa.' in texto(resposta)
    assert consultar('SELECT * FROM produtos') == ()


def test_cadastro_com_preco_negativo_e_recusado(client_admin, consultar):
    resposta = client_admin.post('/produtos/cadastrar', data=dict(DADOS_VALIDOS, preco='-1'))
    assert 'O preço não pode ser negativo.' in texto(resposta)
    assert consultar('SELECT * FROM produtos') == ()


def test_edicao_atualiza_os_dados(client_admin, produto, consultar):
    dados = dict(DADOS_VALIDOS, nome='Arroz 10 kg', preco='47.90', quantidade='20')
    resposta = client_admin.post(f"/produtos/editar/{produto['id']}", data=dados)
    assert resposta.status_code == 302

    atualizado = consultar('SELECT * FROM produtos WHERE id = %s', (produto['id'],))[0]
    assert atualizado['nome'] == 'Arroz 10 kg'
    assert float(atualizado['preco']) == 47.90
    assert atualizado['quantidade'] == 20


def test_edicao_com_dados_invalidos_mantem_o_registro(client_admin, produto, consultar):
    resposta = client_admin.post(f"/produtos/editar/{produto['id']}",
                                 data=dict(DADOS_VALIDOS, quantidade='-1'))
    assert 'A quantidade não pode ser negativa.' in texto(resposta)

    registro = consultar('SELECT * FROM produtos WHERE id = %s', (produto['id'],))[0]
    assert registro['quantidade'] == 10


def test_edicao_de_produto_inexistente_avisa_o_usuario(client_admin):
    resposta = client_admin.get('/produtos/editar/999999', follow_redirects=True)
    assert 'Produto não encontrado.' in texto(resposta)


def test_exclusao_remove_o_produto(client_admin, produto, consultar):
    client_admin.post(f"/produtos/excluir/{produto['id']}")
    assert consultar('SELECT * FROM produtos WHERE id = %s', (produto['id'],)) == ()


def test_exclusao_remove_tambem_o_historico_do_produto(client_admin, produto, consultar):
    client_admin.post('/movimentacoes/entrada', data={'produto_id': produto['id'], 'quantidade': '3'})
    assert len(consultar('SELECT * FROM movimentacoes')) == 1

    client_admin.post(f"/produtos/excluir/{produto['id']}")
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_listagem_destaca_produto_abaixo_do_estoque_minimo(client_admin, executar):
    executar("INSERT INTO produtos (nome, quantidade, estoque_minimo, preco) "
             "VALUES ('Sabão em pó', 2, 5, 12.00)")
    pagina = texto(client_admin.get('/produtos/'))
    assert 'linha-alerta' in pagina
    assert '⚠ baixo' in pagina


def test_listagem_nao_destaca_produto_com_estoque_suficiente(client_admin, produto):
    pagina = texto(client_admin.get('/produtos/'))
    assert 'Arroz 5 kg' in pagina
    assert 'linha-alerta' not in pagina


def test_produto_no_limite_do_minimo_nao_e_destacado(client_admin, executar):
    executar("INSERT INTO produtos (nome, quantidade, estoque_minimo, preco) "
             "VALUES ('Feijão 1 kg', 5, 5, 8.00)")
    assert 'linha-alerta' not in texto(client_admin.get('/produtos/'))


def test_listagem_exibe_a_unidade_de_medida(client_admin, executar):
    executar("INSERT INTO produtos (nome, quantidade, preco, peso, unidade_peso) "
             "VALUES ('Suco 1L', 10, 6.00, 1, 'l')")
    assert '1.000 L' in texto(client_admin.get('/produtos/'))
