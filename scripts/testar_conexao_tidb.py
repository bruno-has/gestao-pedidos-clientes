from getpass import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

HOST = "gateway01.sa-east-1.prod.aws.tidbcloud.com"
PORTA = 4000
BANCO = "gestao_pedidos_clientes"

def testar_conexao():
  print('-=-=-=- TESTE CONEXÃO TIDB -=-=-=-')

  usuario = input('Usuário do TiDB: ').strip()
  senha = getpass('Senha do TiDB: ')

  if not usuario or not senha:
    print('Usuário e senha são obrigatórios')
    return

  url = URL.create(
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

  engine = create_engine(url, pool_pre_ping=True)

  try:
    with engine.connect() as conexao:
      resultado = conexao.execute(text('SELECT 1'))
      print('\nResultado: ', resultado.scalar())

    print('\nConexão com TiDB Cloud realizada com sucesso')

  except Exception as erro:
    print('\nNão foi possível conectar ao TiDB Cloud')
    print('Detalhes:', erro)

  finally:
    engine.dispose()

if __name__ == '__main__':
  testar_conexao()