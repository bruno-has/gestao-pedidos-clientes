from flask import Flask
from sqlalchemy import text

from config import Config
from app.extensions import db
from app import models

def create_app():
  app = Flask(__name__)

  app.json.ensure_ascii = False

  # carrega as configurações da aplicação
  app.config.from_object(Config)

  # inicializa a conexão com o banco de dados
  db.init_app(app)

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

