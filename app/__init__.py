from flask import Flask, jsonify
from sqlalchemy import text

from config import Config
from app.extensions import db, login_manager
from app import models
from app.routes.cliente_route import cliente_bp
from app.routes.pedido_route import pedido_bp
from app.routes.auth_route import auth_bp
from app.models.usuario import Usuario

@login_manager.user_loader
def carregar_usuario(usuario_id):
  return db.session.get(Usuario, int(usuario_id))

@login_manager.unauthorized_handler
def usuario_nao_autorizado():
  return jsonify({
    'erro': 'Autenticação necessária para acessar esse recurso'
  }), 401

def create_app(test_config=None):
  app = Flask(__name__)

  app.json.ensure_ascii = False

  # carrega as configurações da aplicação
  app.config.from_object(Config)

  if test_config is not None:
    app.config.update(test_config)

  # inicializa o SQLAlchemy
  db.init_app(app)

  login_manager.init_app(app)
  login_manager.login_view = 'auth.login'
  login_manager.login_message = 'Faça login para acessar está página'
  login_manager.login_message_category = 'warning'

  # registra as rotas
  app.register_blueprint(cliente_bp)
  app.register_blueprint(pedido_bp)
  app.register_blueprint(auth_bp)

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

