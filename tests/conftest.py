"""Configuração compartilhada dos testes.

Os testes de integração usam um banco SEPARADO (sistema_estoque_teste),
criado a partir do database/schema.sql no início da execução e removido
ao final. O banco real do sistema nunca é tocado.
"""
import os
from pathlib import Path

import MySQLdb
import MySQLdb.cursors
import pytest
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

RAIZ = Path(__file__).resolve().parent.parent

# A senha do MySQL vem do .env; precisa ser carregada antes de importar o app.
load_dotenv(RAIZ / '.env')

from app import create_app  # noqa: E402

BANCO_TESTE = 'sistema_estoque_teste'
ADMIN_EMAIL = 'admin@sistema.com'
ADMIN_SENHA = 'admin123'


def _conectar(com_banco=True):
    parametros = dict(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        charset='utf8mb4',
        autocommit=True,
        cursorclass=MySQLdb.cursors.DictCursor,
    )
    if com_banco:
        parametros['database'] = BANCO_TESTE
    return MySQLdb.connect(**parametros)


def _criar_banco_de_teste():
    script = (RAIZ / 'database' / 'schema.sql').read_text(encoding='utf-8')
    # Aponta o script para o banco de teste (a primeira troca evita duplicar o sufixo).
    script = script.replace(BANCO_TESTE, 'sistema_estoque')
    script = script.replace('sistema_estoque', BANCO_TESTE)

    conexao = _conectar(com_banco=False)
    cursor = conexao.cursor()
    cursor.execute(f'DROP DATABASE IF EXISTS {BANCO_TESTE}')
    cursor.execute(script)
    while cursor.nextset():
        pass
    conexao.close()


@pytest.fixture(scope='session')
def banco_de_teste():
    _criar_banco_de_teste()
    yield
    conexao = _conectar(com_banco=False)
    conexao.cursor().execute(f'DROP DATABASE IF EXISTS {BANCO_TESTE}')
    conexao.close()


@pytest.fixture
def limpar_dados(banco_de_teste):
    """Deixa o banco no estado inicial antes de cada teste: só o admin padrão."""
    conexao = _conectar()
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM movimentacoes')
    cursor.execute('DELETE FROM produtos')
    cursor.execute('DELETE FROM usuarios WHERE email <> %s', (ADMIN_EMAIL,))
    conexao.close()


@pytest.fixture(scope='session')
def app(banco_de_teste):
    aplicacao = create_app()
    aplicacao.config.update(TESTING=True, MYSQL_DB=BANCO_TESTE)
    return aplicacao


@pytest.fixture
def db(limpar_dados):
    conexao = _conectar()
    yield conexao
    conexao.close()


@pytest.fixture
def consultar(db):
    """Executa um SELECT diretamente no banco e devolve os registros."""
    def _consultar(sql, parametros=()):
        cursor = db.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    return _consultar


@pytest.fixture
def executar(db):
    """Executa um INSERT/UPDATE/DELETE diretamente no banco."""
    def _executar(sql, parametros=()):
        cursor = db.cursor()
        cursor.execute(sql, parametros)
    return _executar


@pytest.fixture
def client(app, limpar_dados):
    """Cliente HTTP sem login."""
    return app.test_client()


def fazer_login(cliente, email, senha):
    return cliente.post('/login', data={'email': email, 'senha': senha},
                        follow_redirects=True)


@pytest.fixture
def client_admin(client):
    fazer_login(client, ADMIN_EMAIL, ADMIN_SENHA)
    return client


@pytest.fixture
def client_funcionario(app, executar):
    executar(
        "INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES (%s, %s, %s, 'funcionario')",
        ('Funcionário Teste', 'func@teste.com', generate_password_hash('func123')),
    )
    cliente = app.test_client()
    fazer_login(cliente, 'func@teste.com', 'func123')
    return cliente


@pytest.fixture
def produto(executar, consultar):
    """Produto de exemplo: Arroz 5 kg, 10 unidades, estoque mínimo 5."""
    executar(
        "INSERT INTO produtos (nome, categoria_id, quantidade, estoque_minimo, preco, peso, unidade_peso) "
        "VALUES ('Arroz 5 kg', 1, 10, 5, 25.90, 5, 'kg')"
    )
    return consultar("SELECT * FROM produtos WHERE nome = 'Arroz 5 kg'")[0]


def texto(resposta):
    """Conteúdo da resposta HTTP como texto."""
    return resposta.get_data(as_text=True)
