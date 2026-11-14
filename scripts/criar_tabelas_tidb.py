from getpass import getpass

from sqlalchemy import inspect
from sqlalchemy.engine import URL

from app import create_app
from app.extensions import db

HOST = "gateway01.sa-east-1.prod.aws.tidbcloud.com"
PORTA = 4000
BANCO = "gestao_pedidos_clientes"

def criar_tabelas():
  print('-=-=-=- Criação das tabelas no TiDB Cloud -=-=-=-')

  usuario = input('Usuário do TiDB: ').strip()
  senha = getpass('Senha do TiDB: ')
  
  if not usuario or not senha:
    print('Usuário e senha são obrigatórios')
    return
  
  database_url = URL.create(
    drivername='mysql+pymysql',
    username=usuario,
    password=senha,
    host=HOST,
    port=PORTA,
    database=BANCO,
    query={
      'ssl_verify_cert': 'true',
      'ssl_verify_identity': 'true'
    }
  )

  app = create_app(test_config={'SQLALCHEMY_DATABASE_URI': database_url})

  try:
    with app.app_context():
      print('\nConectando ao banco remoto...')

      db.create_all()

      inspector = inspect(db.engine)
      tabelas = inspector.get_table_names()

      print('\n Tabelas encontradas no banco:')
      for tabela in tabelas:
        print(f'- {tabela}')

      print('\nProcesso concluído com sucesso')

  except Exception as erro:
    print('\nErro ao criar as tabelas:')
    print(erro)

  finally:
    with app.app_context():
      db.engine.dispose()

if __name__ == '__main__':
  criar_tabelas()