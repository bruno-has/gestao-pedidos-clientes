from flask import Flask, jsonify, redirect, url_for, request
from sqlalchemy import text

from config import Config
from app.extensions import db, login_manager, csrf
from app import models
from app.routes.cliente_route import cliente_bp
from app.routes.pedido_route import pedido_bp
from app.routes.auth_route import auth_bp
from app.routes.web_route import web_bp
from app.models.usuario import Usuario

@login_manager.user_loader
def carregar_usuario(usuario_id):
  return db.session.get(Usuario, int(usuario_id))

@login_manager.unauthorized_handler
def usuario_nao_autorizado():
  if request.blueprint == 'web':
    return redirect(url_for('web.login'))

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

  # valida as configuracoes obrigatorias
  Config.validar_configuracao(app)

  db.init_app(app)

  login_manager.init_app(app)
  login_manager.login_view = 'web.login'
  login_manager.login_message = 'Faça login para acessar está página'
  login_manager.login_message_category = 'warning'

  csrf.init_app(app)

  # registra as rotas
  app.register_blueprint(cliente_bp)
  app.register_blueprint(pedido_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(web_bp)

  @app.route('/')
  def inicio():
    return redirect(url_for('web.login'))

  @app.route('/health', methods=['GET'])
  def health():
    try:
      db.session.execute(text('SELECT 1'))

      return jsonify({
        'status': 'ok',
        'database': 'connected'
      }), 200

    except Exception:
      db.session.rollback()

      return jsonify({
        'status': 'unavailable'
      }), 503

  return app