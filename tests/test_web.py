import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.services.auth_service import criar_usuario

@pytest.fixture
def usuario_teste(app):
  usuario = criar_usuario(
    nome='Maria',
    email='maria@teste.com',
    senha='senha12345'
  )

  return usuario.id

@pytest.fixture
def cliente_autenticado(client, usuario_teste):
  with client.session_transaction() as sess:
    sess['_user_id'] = str(usuario_teste)
    sess['_fresh'] = True

  return client

def test_acessar_pagina_login(client):
  resposta = client.get('/login')

  assert resposta.status_code == 200
  assert b'Gest' in resposta.data

def test_acessar_painel_sem_autenticacao(client):
  resposta = client.get('/painel')

  assert resposta.status_code == 302
  assert '/login' in resposta.headers['Location']

def test_acessar_painel_autenticado(cliente_autenticado):
  resposta = cliente_autenticado.get('/painel')

  assert resposta.status_code == 200
  assert 'Olá, Maria!' in resposta.get_data(as_text=True)

def test_listar_clientes_autenticado(cliente_autenticado):
  resposta = cliente_autenticado.get('/painel/clientes')

  assert resposta.status_code == 200
  assert b'Clientes' in resposta.data

def test_cadastrar_cliente_web(cliente_autenticado):
  resposta = cliente_autenticado.post(
    '/painel/clientes/novo', 
    data={
      'nome': 'João da Silva',
      'telefone': '(11) 99999-9999'
    }
  )

  assert resposta.status_code == 302
  assert resposta.headers['Location'].endswith('/painel/clientes')

  cliente = Cliente.query.filter_by(nome='João da Silva').first()

  assert cliente is not None
  assert cliente.telefone == '(11) 99999-9999'

def test_editar_cliente_web(cliente_autenticado):
  cliente = Cliente(
    nome = 'Ana Souza',
    telefone = '11912345678'
  )

  db.session.add(cliente)
  db.session.commit()

  resposta = cliente_autenticado.post(
    f'/painel/clientes/{cliente.id}/editar',
    data = {
      'nome': 'Ana Souza',
      'telefone': '11987654321'
    }
  )

  assert resposta.status_code == 302

  cliente_autenticado = db.session.get(Cliente, cliente.id)

  assert cliente_autenticado.telefone == '11987654321'

def test_excluir_cliente_web(cliente_autenticado):
  cliente = Cliente(
    nome = 'Carlos Lima',
    telefone = '11988887777'
  )

  db.session.add(cliente)
  db.session.commit()

  cliente_id = cliente.id

  resposta = cliente_autenticado.post(f'/painel/clientes/{cliente_id}/excluir')

  assert resposta.status_code == 302
  
  cliente_excluido = db.session.get(Cliente, cliente_id)
  
  assert cliente_excluido is None

def test_impedir_exclusao_cliente_com_pedidos(cliente_autenticado):
  from datetime import datetime, timedelta
  from app.models.pedido import Pedido

  cliente = Cliente(
    nome = 'Pedro Santos',
    telefone = '11912344321'
  )

  db.session.add(cliente)
  db.session.commit()

  pedido = Pedido(
    cliente_id = cliente.id,
    data_retirada = datetime.now() + timedelta(days=1),
    status = 'pendente'
  )

  db.session.add(pedido)
  db.session.commit()

  resposta = cliente_autenticado.post(
    f'/painel/clientes/{cliente.id}/excluir',
    follow_redirects=True
  )

  assert resposta.status_code == 200

  cliente_existente = db.session.get(Cliente, cliente.id)

  assert cliente_existente is not None
  assert ('Não é possível excluir um cliente que possui pedidos associados') in resposta.get_data(as_text=True)

def test_bloquear_login_sem_token_csrf(app, client):
  app.config['WTF_CSRF_ENABLED'] = True

  resposta = client.post(
    '/login',
    data={
      'email': 'maria@teste.com',
      'senha': 'senha123'
    }
  )

  assert resposta.status_code == 400

def test_exibir_botao_alto_contraste_painel(cliente_autenticado):
  resposta = cliente_autenticado.get('/painel')

  conteudo = resposta.get_data(as_text=True)

  assert resposta.status_code == 200
  assert 'btn-alto-contraste' in conteudo
  assert 'aria-pressed="false"' in conteudo

