import os


class Config:
    """Configurações da aplicação, lidas de variáveis de ambiente
    (definidas no arquivo .env)."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'sistema_estoque')
    MYSQL_CURSORCLASS = 'DictCursor'
