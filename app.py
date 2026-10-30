from flask import Flask, session, redirect, url_for
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    from routes.auth import auth_bp
    from routes.produtos import produtos_bp
    from routes.movimentacoes import movimentacoes_bp
    from routes.usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(movimentacoes_bp)
    app.register_blueprint(usuarios_bp)

    @app.route('/')
    def index():
        if 'usuario_id' in session:
            return redirect(url_for('produtos.listar'))
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)