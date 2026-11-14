import os
from dotenv import load_dotenv

# carrega as variáveis de ambiente
load_dotenv()

class Config: 
  SECRET_KEY = os.getenv('SECRET_KEY')

  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

  SQLALCHEMY_TRACK_MODIFICATIONS = False

  DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

  SESSION_COOKIE_HTTPONLY = True

  SESSION_COOKIE_SAMESITE = 'Lax'

  SESSION_COOKIE_SECURE = (os.getenv('FLASK_ENV') == 'production')

  @staticmethod
  def validar_configuracao(app):
    if not app.config.get('SECRET_KEY'):
      raise RuntimeError('A variável SECRET_KEY não foi configurada')

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
      raise RuntimeError('A variável DATABASE_URL não foi configurada')