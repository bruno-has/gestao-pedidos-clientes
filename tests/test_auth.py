from app.services.auth_service import criar_usuario

def cadastrar_usuario_teste():
  return criar_usuario(
    nome = 'Maria',
    email = 'maria@teste.com',
    senha = 'senha12345'
  )

def test_login_com_credenciais_validas(client):
  cadastrar_usuario_teste()

  resposta = client.post('/auth/login', json={
    'email': 'maria@teste.com',
    'senha': 'senha12345'
  })

  dados = resposta.get_json()

  assert resposta.status_code == 200
  assert dados['mensagem'] == 'Login realizado com sucesso'
  assert dados['usuario']['email'] == 'maria@teste.com'

def test_login_com_senha_incorreta(client):
  cadastrar_usuario_teste()

  resposta = client.post('/auth/login', json={
    'email': 'maria@teste.com',
    'senha': 'senha67890'
  })

  assert resposta.status_code == 401
  assert resposta.get_json()['erro'] == 'Credenciais inválidas'

def test_login_com_usuario_inexistente(client):
  
  resposta = client.post('/auth/login', json={
    'email': 'inexistente@teste.com',
    'senha': 'senha12345'
  })

  assert resposta.status_code == 401

def test_login_sem_email(client):
  resposta = client.post('/auth/login', json={
    'senha': 'senha12345'
  })

  assert resposta.status_code == 400
  assert resposta.get_json()['erro'] == 'O email é obrigatório'

def test_logout_usuario_autenticado(client):
  cadastrar_usuario_teste()

  client.post('/auth/login', json={
    'email': 'maria@teste.com',
    'senha': 'senha12345'
  })

  resposta = client.post('/auth/logout')

  assert resposta.status_code == 200
  assert resposta.get_json()['mensagem'] == 'Logout realizado com sucesso'

def test_logout_usuario_nao_autenticado(client):
  resposta = client.post('/auth/logout')

  assert resposta.status_code == 401
  assert resposta.get_json()['erro'] == 'Usuário não está autenticado'

def test_consultar_usuario_sem_autenticacao(client):
  resposta = client.get('/auth/me')

  assert resposta.status_code == 401
  assert resposta.get_json()['erro'] == 'Usuário não está autenticado'

def test_consultar_usuario_com_sessao_ativa(client):
  cadastrar_usuario_teste()

  client.post('auth/login', json={
    'email': 'maria@teste.com',
    'senha': 'senha12345'
  })

  resposta = client.get('/auth/me')

  dados = resposta.get_json()

  assert resposta.status_code == 200
  assert dados['usuario']['nome'] == 'Maria'
  assert dados['usuario']['email'] == 'maria@teste.com'

def test_sessao_encerrada_apos_logout(client):
  cadastrar_usuario_teste()
  
  client.post('auth/login', json={
    'email': 'maria@teste.com',
    'senha': 'senha12345'
  })

  client.post('/auth/logout')

  resposta = client.get('/auth/me')

  assert resposta.status_code == 401