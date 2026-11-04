from flask import Flask

def create_app():
  app = Flask(__name__)

  @app.route('/')
  def inicio():
    return 'Sistema de Gestão de Pedidos e Clientes'

  return app