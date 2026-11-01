# Sistema de Gestão de Estoque para Pequenos Comércios

Aplicação web para controle de estoque de pequenos comércios, desenvolvida como Trabalho de Curso de Ciência da Computação (UNIP). O sistema cadastra produtos, registra entradas e saídas com histórico por usuário e sinaliza produtos com estoque baixo, com acesso restrito por login e por cargo.

## Funcionalidades

- Login e logout, com senhas armazenadas em hash
- Dois cargos: funcionário e administrador
- Cadastro, listagem, edição e exclusão de produtos, com categoria, peso ou volume (kg, L ou mL) e estoque mínimo
- Entradas e saídas de estoque, com recusa de saída acima do saldo
- Histórico de movimentações de cada produto, com data, tipo, quantidade e responsável
- Alerta visual de estoque baixo na listagem
- Gestão de usuários pelo administrador (cadastro e exclusão)

## Tecnologias

Python 3.13, Flask 3.0.3, Flask-MySQLdb 2.0.0, MySQL 8.0, Jinja2, HTML, CSS e JavaScript. Os testes usam pytest.

## Estrutura do projeto

```
sistema-estoque/
├── app.py                 # criação da aplicação
├── config.py              # configurações (lidas do .env)
├── validacoes.py          # regras de validação de produto
├── requirements.txt       # dependências da aplicação
├── requirements-dev.txt   # dependências + pytest
├── pytest.ini
├── .env.example           # modelo do arquivo .env
├── database/
│   └── schema.sql         # banco, tabelas e dados iniciais
├── routes/                # auth, produtos, movimentacoes, usuarios
├── templates/             # páginas HTML (Jinja2)
├── static/                # CSS e JavaScript
└── tests/                 # testes automatizados
```

## Pré-requisitos

- Python 3.13
- MySQL 8.0 instalado e em execução, com o comando `mysql` acessível no terminal
- Git (opcional, para clonar o repositório)

## Instalação (Windows, PowerShell)

Todos os comandos são digitados na pasta que contém o `app.py`.

1. Crie e ative o ambiente virtual:

   ```
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

   Se o PowerShell bloquear a ativação, rode uma vez:
   `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

2. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

3. Crie o banco de dados:

   ```
   Get-Content database/schema.sql | mysql -u root -p
   ```

   No Prompt de Comando (cmd) use `mysql -u root -p < database/schema.sql`.
   O script cria as tabelas sem verificar se já existem. Se o banco `sistema_estoque` já existir, remova-o antes com `mysql -u root -p -e "DROP DATABASE sistema_estoque;"` (isso apaga todos os dados).

4. Crie o arquivo `.env` a partir do modelo:

   ```
   copy .env.example .env
   ```

   Abra o `.env` e preencha `MYSQL_PASSWORD` com a senha do seu MySQL:

   | Variável | Descrição |
   |---|---|
   | MYSQL_HOST | Servidor do banco (padrão: localhost) |
   | MYSQL_USER | Usuário do MySQL (padrão: root) |
   | MYSQL_PASSWORD | Senha do MySQL |
   | MYSQL_DB | Nome do banco (sistema_estoque) |
   | SECRET_KEY | Chave usada para assinar as sessões |

   O `.env` contém credenciais e não é versionado.

Em Linux ou macOS, a ativação do ambiente é `source venv/bin/activate` e o banco é criado com `mysql -u root -p < database/schema.sql`.

## Execução

```
python app.py
```

Acesse `http://localhost:5000`. O servidor iniciado assim é o de desenvolvimento do Flask e não deve ser usado em produção.

## Primeiro acesso

O script do banco cria um administrador padrão:

- E-mail: `admin@sistema.com`
- Senha: `admin123`

Essa senha serve apenas para o primeiro acesso e deve ser trocada em qualquer uso real. Não há cadastro público de usuários: o administrador cria as demais contas na tela **Usuários** e define o cargo de cada uma.

| Recurso | Funcionário | Administrador |
|---|---|---|
| Produtos e movimentações | sim | sim |
| Gestão de usuários | não | sim |

## Testes automatizados

```
pip install -r requirements-dev.txt
python -m pytest -v
```

A suíte tem 100 testes: 35 de unidade e 65 de integração (autenticação, produtos, movimentações e usuários). Os testes criam um banco separado, `sistema_estoque_teste`, a partir do `schema.sql` e o removem ao final, sem tocar no banco do sistema. O MySQL precisa estar em execução e o `.env` precisa ter a senha correta.

## Limitações conhecidas

- Servidor de desenvolvimento, sem HTTPS
- Sem recuperação de senha, e com senha padrão no administrador inicial
- Excluir um produto remove também o seu histórico de movimentações
- Quantidade acima da capacidade do campo no banco de dados gera erro interno
- O cargo do usuário fica guardado na sessão e não é reconsultado a cada requisição

## Autoria

Trabalho de Curso do curso de Ciência da Computação da UNIP, de Carlos Eduardo Loubak e Gabriel Soares Vieira, sob orientação do professor Antonio Palmeira de Araújo Neto.
