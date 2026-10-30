"""Testes de integração: autenticação e controle de acesso."""
import pytest

from conftest import ADMIN_EMAIL, ADMIN_SENHA, fazer_login, texto


def test_login_valido_redireciona_para_a_listagem(client):
    resposta = client.post('/login', data={'email': ADMIN_EMAIL, 'senha': ADMIN_SENHA})
    assert resposta.status_code == 302
    assert resposta.headers['Location'].endswith('/produtos/')


def test_login_valido_guarda_usuario_na_sessao(client):
    fazer_login(client, ADMIN_EMAIL, ADMIN_SENHA)
    with client.session_transaction() as sessao:
        assert sessao['usuario_cargo'] == 'administrador'
        assert sessao['usuario_nome'] == 'Administrador'


def test_senha_incorreta_e_recusada(client):
    resposta = client.post('/login', data={'email': ADMIN_EMAIL, 'senha': 'errada'})
    assert resposta.status_code == 200
    assert 'E-mail ou senha inválidos.' in texto(resposta)
    with client.session_transaction() as sessao:
        assert 'usuario_id' not in sessao


def test_email_inexistente_gera_a_mesma_mensagem(client):
    resposta = client.post('/login', data={'email': 'ninguem@teste.com', 'senha': 'qualquer'})
    assert 'E-mail ou senha inválidos.' in texto(resposta)


@pytest.mark.parametrize('metodo, url', [
    ('get', '/produtos/'),
    ('get', '/produtos/cadastrar'),
    ('get', '/usuarios/'),
    ('post', '/movimentacoes/entrada'),
    ('post', '/movimentacoes/saida'),
])
def test_rotas_internas_exigem_login(client, metodo, url):
    resposta = getattr(client, metodo)(url)
    assert resposta.status_code == 302
    assert resposta.headers['Location'].endswith('/login')


def test_rota_raiz_sem_login_vai_para_o_login(client):
    resposta = client.get('/')
    assert resposta.headers['Location'].endswith('/login')


def test_rota_raiz_com_login_vai_para_a_listagem(client_admin):
    resposta = client_admin.get('/')
    assert resposta.headers['Location'].endswith('/produtos/')


def test_logout_encerra_a_sessao(client_admin):
    client_admin.get('/logout')
    resposta = client_admin.get('/produtos/')
    assert resposta.status_code == 302
    assert resposta.headers['Location'].endswith('/login')


def test_administrador_acessa_a_gestao_de_usuarios(client_admin):
    assert client_admin.get('/usuarios/').status_code == 200


def test_funcionario_nao_acessa_a_gestao_de_usuarios(client_funcionario):
    resposta = client_funcionario.get('/usuarios/', follow_redirects=True)
    assert 'Apenas administradores podem acessar essa área.' in texto(resposta)


def test_menu_do_funcionario_nao_mostra_o_link_de_usuarios(client_funcionario):
    pagina = texto(client_funcionario.get('/produtos/'))
    assert 'Usuários' not in pagina


def test_menu_do_administrador_mostra_o_link_de_usuarios(client_admin):
    pagina = texto(client_admin.get('/produtos/'))
    assert 'Usuários' in pagina
