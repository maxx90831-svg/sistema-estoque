"""Testes de integração: entradas, saídas e histórico de movimentações."""
from conftest import texto


def _saldo(consultar, produto_id):
    return consultar('SELECT quantidade FROM produtos WHERE id = %s', (produto_id,))[0]['quantidade']


def test_entrada_aumenta_o_saldo_e_registra_o_historico(client_admin, produto, consultar):
    resposta = client_admin.post('/movimentacoes/entrada',
                                 data={'produto_id': produto['id'], 'quantidade': '5'})
    assert resposta.status_code == 302
    assert _saldo(consultar, produto['id']) == 15

    movimentacao = consultar('SELECT * FROM movimentacoes')[0]
    assert movimentacao['tipo'] == 'entrada'
    assert movimentacao['quantidade'] == 5


def test_saida_reduz_o_saldo_e_registra_o_historico(client_admin, produto, consultar):
    client_admin.post('/movimentacoes/saida',
                      data={'produto_id': produto['id'], 'quantidade': '4'})
    assert _saldo(consultar, produto['id']) == 6

    movimentacao = consultar('SELECT * FROM movimentacoes')[0]
    assert movimentacao['tipo'] == 'saida'
    assert movimentacao['quantidade'] == 4


def test_movimentacao_registra_o_usuario_responsavel(client_admin, produto, consultar):
    client_admin.post('/movimentacoes/entrada',
                      data={'produto_id': produto['id'], 'quantidade': '1'})
    admin = consultar("SELECT id FROM usuarios WHERE email = 'admin@sistema.com'")[0]
    assert consultar('SELECT usuario_id FROM movimentacoes')[0]['usuario_id'] == admin['id']


def test_funcionario_tambem_pode_movimentar_o_estoque(client_funcionario, produto, consultar):
    client_funcionario.post('/movimentacoes/entrada',
                            data={'produto_id': produto['id'], 'quantidade': '2'})
    assert _saldo(consultar, produto['id']) == 12


def test_saida_maior_que_o_saldo_e_recusada(client_admin, produto, consultar):
    resposta = client_admin.post('/movimentacoes/saida',
                                 data={'produto_id': produto['id'], 'quantidade': '11'},
                                 follow_redirects=True)
    assert 'Quantidade de saída inválida ou maior que o estoque disponível.' in texto(resposta)
    assert _saldo(consultar, produto['id']) == 10
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_saida_igual_ao_saldo_zera_o_estoque(client_admin, produto, consultar):
    client_admin.post('/movimentacoes/saida',
                      data={'produto_id': produto['id'], 'quantidade': '10'})
    assert _saldo(consultar, produto['id']) == 0


def test_saida_com_quantidade_zero_ou_negativa_e_recusada(client_admin, produto, consultar):
    for quantidade in ('0', '-3'):
        client_admin.post('/movimentacoes/saida',
                          data={'produto_id': produto['id'], 'quantidade': quantidade})
    assert _saldo(consultar, produto['id']) == 10
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_entrada_com_quantidade_zero_ou_negativa_e_recusada(client_admin, produto, consultar):
    resposta = client_admin.post('/movimentacoes/entrada',
                                 data={'produto_id': produto['id'], 'quantidade': '0'},
                                 follow_redirects=True)
    assert 'A quantidade de entrada deve ser maior que zero.' in texto(resposta)
    client_admin.post('/movimentacoes/entrada',
                      data={'produto_id': produto['id'], 'quantidade': '-2'})
    assert _saldo(consultar, produto['id']) == 10
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_saida_de_produto_inexistente_e_recusada(client_admin, consultar):
    resposta = client_admin.post('/movimentacoes/saida',
                                 data={'produto_id': '999999', 'quantidade': '1'},
                                 follow_redirects=True)
    assert 'Quantidade de saída inválida' in texto(resposta)
    assert consultar('SELECT * FROM movimentacoes') == ()


def test_sequencia_de_entrada_e_saida_resulta_no_saldo_correto(client_admin, produto, consultar):
    client_admin.post('/movimentacoes/entrada', data={'produto_id': produto['id'], 'quantidade': '20'})
    client_admin.post('/movimentacoes/saida', data={'produto_id': produto['id'], 'quantidade': '7'})
    client_admin.post('/movimentacoes/saida', data={'produto_id': produto['id'], 'quantidade': '3'})
    assert _saldo(consultar, produto['id']) == 20
    assert len(consultar('SELECT * FROM movimentacoes')) == 3


def test_historico_lista_da_mais_recente_para_a_mais_antiga(client_admin, produto, executar):
    admin_id = 1
    executar("INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, data_movimentacao) "
             "VALUES (%s, (SELECT id FROM usuarios WHERE email = 'admin@sistema.com'), 'entrada', 3, '2026-01-01 10:00:00')",
             (produto['id'],))
    executar("INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, data_movimentacao) "
             "VALUES (%s, (SELECT id FROM usuarios WHERE email = 'admin@sistema.com'), 'saida', 2, '2026-01-02 15:30:00')",
             (produto['id'],))

    pagina = texto(client_admin.get(f"/movimentacoes/historico/{produto['id']}"))
    assert pagina.index('02/01/2026 15:30') < pagina.index('01/01/2026 10:00')
    assert 'Administrador' in pagina


def test_historico_vazio_exibe_aviso(client_admin, produto):
    pagina = texto(client_admin.get(f"/movimentacoes/historico/{produto['id']}"))
    assert 'Nenhuma movimentação registrada para este produto.' in pagina


def test_historico_de_produto_inexistente_avisa_o_usuario(client_admin):
    resposta = client_admin.get('/movimentacoes/historico/999999', follow_redirects=True)
    assert 'Produto não encontrado.' in texto(resposta)
