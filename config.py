import os

class Config: 
  SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-para-desenvolvimento')

  SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@localhost:3306/gestao_pedidos_clientes'
  )

  SQLALCHEMY_TRACK_MODIFICATIONS = False