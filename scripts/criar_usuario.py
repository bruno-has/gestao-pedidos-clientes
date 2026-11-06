from getpass import getpass

from app import create_app
from app.services.auth_service import criar_usuario

def main():
  app = create_app()

  with app.app_context():
    print('\n-=-=-=-=-=- Cadastro de usuário administrador -=-=-=-=-=-\n')
    nome = input('Nome: ').strip()
    email = input('Email: ').strip()

    if not nome:
      print('\nErro: o nome é obrigatório\n')
      return

    if not email or '@' not in email:
      print('\nErro: informe um email válido\n')
      return

    senha = getpass('Senha: ') 
    confirmar_senha = getpass('Confirme sua senha: ')

    if len(senha) < 8:
      print('\nErro: a senha deve possuir pelo menos 8 caracteres')
      return

    if senha != confirmar_senha:
      print('\nErro: as senhas não correspondem')
      return

    usuario = criar_usuario(nome, email, senha)

    if usuario is None:
      print('\nErro: email já cadastrado')
      return

    print('\nUsuário administrado cadastrado com sucesso')
    print(f'Nome: {nome}')
    print(f'Email: {email}')
    
if __name__ == '__main__':
  main()    