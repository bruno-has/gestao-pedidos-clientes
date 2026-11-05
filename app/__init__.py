from flask import Flask
from sqlalchemy import text

from config import Config
from app.extensions import db
from app import models
from app.routes.cliente_route import cliente_bp
from app.routes.pedido_route import pedido_bp

def create_app():
  app = Flask(__name__)

  app.json.ensure_ascii = False

  # carrega as configurações da aplicação
  app.config.from_object(Config)

  # inicializa o SQLAlchemy
  db.init_app(app)

  # registra as rotas de clientes
  app.register_blueprint(cliente_bp)

  # registra as rotas de pedidos
  app.register_blueprint(pedido_bp)

  @app.route('/')
  def inicio():
    return 'Sistema de Gestão de Pedidos e Clientes - Cadastro, produção e conclusão'

  @app.route('/teste-conexao')
  def teste_conexao():
    try:
      db.session.execute(text('SELECT 1'))

      return {
        'mensagem': 'Conexão com o MySQL realizada com sucesso' 
      }, 200

    except Exception:
      app.logger.exception('Erro ao conectar ao banco de dados')

      return {
        'erro': 'Não foi possível conectar ao banco de dados'
      }, 500

  return app

