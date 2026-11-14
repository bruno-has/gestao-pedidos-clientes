from getpass import getpass
from secrets import token_hex

from sqlalchemy import URL
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.services.auth_service import criar_usuario

HOST = 'gateway01.sa-east-1.prod.aws.tidbcloud.com'
PORT = 4000
DATABASE = 'gestao_pedidos_clientes'

def main():
  print('\n-=-=-=-=-=- Cadastro de administrador no TiDB -=-=-=-=-=-\n')

  # Credenciais do banco remoto
  usuario_db = input('Usuário do TiDB: ').strip()
  senha_db = getpass('Senha do TiDB: ')

  if not usuario_db or not senha_db:
    print('\nErro: informe as credenciais do TiDB.')
    return

  # Monta a conexão com TLS
  url = URL.create(
    drivername='mysql+pymysql',
    username=usuario_db,
    password=senha_db,
    host=HOST,
    port=PORT,
    database=DATABASE,
    query={
      'ssl_verify_cert': 'true',
      'ssl_verify_identity': 'true'
    }
  )

  # Configuração explícita para usar o banco remoto
  app = create_app({
    'SECRET_KEY': token_hex(32),
    'SQLALCHEMY_DATABASE_URI': url.render_as_string(hide_password=False)
  })

  # Dados da conta
  print('\n-=-=-=-=-=- Dados da conta -=-=-=-=-=-\n')
  nome = input('Nome: ').strip()
  email = input('Email: ').strip().lower()

  if not nome:
    print('\nErro: o nome é obrigatório.')
    return

  if not email or '@' not in email:
    print('\nErro: informe um email válido.')
    return

  senha = getpass('Senha da conta: ')
  confirmar_senha = getpass('Confirme a senha: ')

  if len(senha) < 8:
    print('\nErro: a senha deve possuir pelo menos 8 caracteres.')
    return

  if senha != confirmar_senha:
    print('\nErro: as senhas não correspondem.')
    return

  try:
    with app.app_context():
      usuario = criar_usuario(nome, email, senha)

      if usuario is None:
        print('\nErro: este email já está cadastrado no TiDB.')
        return

      print('\nConta administrativa criada com sucesso!')
      print(f'Nome: {usuario.nome}')
      print(f'Email: {usuario.email}')
      print(f'ID: {usuario.id}')

  except SQLAlchemyError:
    from app.extensions import db

    with app.app_context():
      db.session.rollback()

    print('\nErro ao acessar ou gravar no TiDB.')
    print('Verifique as credenciais, a conexão e a existência da tabela usuarios.')

  finally:
    with app.app_context():
      from app.extensions import db
      db.session.remove()

if __name__ == '__main__':
    main()