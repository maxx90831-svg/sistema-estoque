"""Testes de integração: gestão de usuários pelo administrador."""
from werkzeug.security import check_password_hash, generate_password_hash

from conftest import fazer_login, texto

NOVO_USUARIO = {
    'nome': 'Maria Souza',
    'email': 'maria@loja.com',
    'senha': 'senha123',
    'cargo': 'funcionario',
}


def test_administrador_cadastra_funcionario(client_admin, consultar):
    resposta = client_admin.post('/usuarios/cadastrar', data=NOVO_USUARIO)
    assert resposta.status_code == 302

    usuario = consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'")[0]
    assert usuario['cargo'] == 'funcionario'


def test_senha_do_novo_usuario_e_gravada_em_hash(client_admin, consultar):
    client_admin.post('/usuarios/cadastrar', data=NOVO_USUARIO)
    usuario = consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'")[0]
    assert usuario['senha_hash'] != 'senha123'
    assert check_password_hash(usuario['senha_hash'], 'senha123')


def test_novo_usuario_consegue_fazer_login(app, client_admin):
    client_admin.post('/usuarios/cadastrar', data=NOVO_USUARIO)
    cliente = app.test_client()
    fazer_login(cliente, 'maria@loja.com', 'senha123')
    with cliente.session_transaction() as sessao:
        assert sessao['usuario_cargo'] == 'funcionario'


def test_cargo_invalido_e_recusado(client_admin, consultar):
    resposta = client_admin.post('/usuarios/cadastrar', data=dict(NOVO_USUARIO, cargo='dono'))
    assert 'Selecione um cargo válido.' in texto(resposta)
    assert consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'") == ()


def test_senha_curta_e_recusada(client_admin, consultar):
    resposta = client_admin.post('/usuarios/cadastrar', data=dict(NOVO_USUARIO, senha='123'))
    assert 'A senha deve ter pelo menos 6 caracteres.' in texto(resposta)
    assert consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'") == ()


def test_email_duplicado_e_recusado(client_admin, consultar):
    client_admin.post('/usuarios/cadastrar', data=NOVO_USUARIO)
    resposta = client_admin.post('/usuarios/cadastrar', data=dict(NOVO_USUARIO, nome='Outra Maria'))
    assert 'Já existe um usuário com esse e-mail.' in texto(resposta)
    assert len(consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'")) == 1


def test_funcionario_nao_consegue_cadastrar_usuarios(client_funcionario, consultar):
    resposta = client_funcionario.post('/usuarios/cadastrar', data=NOVO_USUARIO)
    assert resposta.status_code == 302
    assert consultar("SELECT * FROM usuarios WHERE email = 'maria@loja.com'") == ()


def test_funcionario_nao_consegue_excluir_usuarios(client_funcionario, consultar):
    admin = consultar("SELECT id FROM usuarios WHERE email = 'admin@sistema.com'")[0]
    client_funcionario.post(f"/usuarios/excluir/{admin['id']}")
    assert len(consultar("SELECT * FROM usuarios WHERE email = 'admin@sistema.com'")) == 1


def test_administrador_exclui_funcionario(client_admin, executar, consultar):
    executar("INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES ('Joao', 'joao@loja.com', 'x', 'funcionario')")
    joao = consultar("SELECT id FROM usuarios WHERE email = 'joao@loja.com'")[0]

    client_admin.post(f"/usuarios/excluir/{joao['id']}")
    assert consultar("SELECT * FROM usuarios WHERE email = 'joao@loja.com'") == ()


def test_administrador_nao_exclui_a_propria_conta(client_admin, consultar):
    admin = consultar("SELECT id FROM usuarios WHERE email = 'admin@sistema.com'")[0]
    resposta = client_admin.post(f"/usuarios/excluir/{admin['id']}", follow_redirects=True)
    assert 'Você não pode excluir o seu próprio usuário.' in texto(resposta)
    assert len(consultar("SELECT * FROM usuarios WHERE email = 'admin@sistema.com'")) == 1


def test_listagem_de_usuarios_nao_oferece_exclusao_da_propria_conta(client_admin):
    assert '(você)' in texto(client_admin.get('/usuarios/'))


def test_administrador_pode_excluir_outro_administrador_quando_ha_mais_de_um(
        client_admin, executar, consultar):
    executar("INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES ('Admin 2', 'admin2@loja.com', 'x', 'administrador')")
    admin2 = consultar("SELECT id FROM usuarios WHERE email = 'admin2@loja.com'")[0]

    client_admin.post(f"/usuarios/excluir/{admin2['id']}")
    assert consultar("SELECT * FROM usuarios WHERE email = 'admin2@loja.com'") == ()


def test_ultimo_administrador_nao_pode_ser_excluido(app, executar, consultar):
    """Cenário: o admin 2 está logado, é excluído por outro admin e, com a sessão
    ainda ativa, tenta excluir o único administrador restante."""
    executar("INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES ('Admin 2', 'admin2@loja.com', %s, 'administrador')",
             (generate_password_hash('admin456'),))
    cliente = app.test_client()
    fazer_login(cliente, 'admin2@loja.com', 'admin456')
    executar("DELETE FROM usuarios WHERE email = 'admin2@loja.com'")

    admin = consultar("SELECT id FROM usuarios WHERE email = 'admin@sistema.com'")[0]
    resposta = cliente.post(f"/usuarios/excluir/{admin['id']}", follow_redirects=True)

    assert 'Não é possível excluir o último administrador do sistema.' in texto(resposta)
    assert len(consultar("SELECT * FROM usuarios WHERE email = 'admin@sistema.com'")) == 1
