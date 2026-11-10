
from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.pedido import Pedido
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


def criar_cliente_teste():
  cliente = Cliente(
    nome='Cliente Dashboard',
    telefone='11999999999'
  )

  db.session.add(cliente)
  db.session.commit()

  return cliente


def criar_pedido_teste(cliente_id, status, data_retirada):
  pedido = Pedido(
    cliente_id=cliente_id,
    data_retirada=data_retirada,
    status=status
  )

  db.session.add(pedido)
  db.session.commit()

  return pedido


def test_exibir_dashboard(cliente_autenticado):
  resposta = cliente_autenticado.get('/painel')

  assert resposta.status_code == 200
  assert b'Painel' in resposta.data
  assert b'Pedidos pendentes' in resposta.data
  assert b'Em produ' in resposta.data
  assert b'Conclu' in resposta.data
  assert b'Pr\xc3\xb3ximas retiradas' in resposta.data


def test_dashboard_exibir_indicadores_corretos(app, cliente_autenticado):
  with app.app_context():
    cliente = criar_cliente_teste()

    agora = datetime.now()

    criar_pedido_teste(
      cliente.id,
      'pendente',
      agora + timedelta(days=1)
    )

    criar_pedido_teste(
      cliente.id,
      'pendente',
      agora + timedelta(days=2)
    )

    criar_pedido_teste(
      cliente.id,
      'em produção',
      agora + timedelta(days=3)
    )

    criar_pedido_teste(
      cliente.id,
      'concluído',
      agora + timedelta(days=4)
    )

  resposta = cliente_autenticado.get('/painel')

  assert resposta.status_code == 200
  assert b'Cliente Dashboard' in resposta.data

  # Confere os três indicadores.
  assert b'Pedidos pendentes' in resposta.data
  assert b'Em produ' in resposta.data
  assert b'Conclu' in resposta.data


def test_dashboard_listar_proximas_retiradas(app, cliente_autenticado):
  with app.app_context():
    cliente = criar_cliente_teste()

    agora = datetime.now()

    pedido_proximo = criar_pedido_teste(
      cliente.id,
      'pendente',
      agora + timedelta(hours=2)
    )

    pedido_distante = criar_pedido_teste(
      cliente.id,
      'em produção',
      agora + timedelta(days=2)
    )

    pedido_concluido = criar_pedido_teste(
      cliente.id,
      'concluído',
      agora + timedelta(hours=1)
    )

    pedido_passado = criar_pedido_teste(
      cliente.id,
      'pendente',
      agora - timedelta(days=1)
    )

    ids_esperados = {
      pedido_proximo.id,
      pedido_distante.id
    }

    ids_nao_esperados = {
      pedido_concluido.id,
      pedido_passado.id
    }

  resposta = cliente_autenticado.get('/painel')

  assert resposta.status_code == 200

  html = resposta.get_data(as_text=True)

  for pedido_id in ids_esperados:
    assert f'Pedido #{pedido_id}'.encode() in resposta.data

  for pedido_id in ids_nao_esperados:
    assert f'Pedido #{pedido_id}'.encode() not in resposta.data


def test_dashboard_sem_proximas_retiradas(app, cliente_autenticado):
  with app.app_context():
    cliente = criar_cliente_teste()

    criar_pedido_teste(
      cliente.id,
      'concluído',
      datetime.now() + timedelta(days=1)
    )

  resposta = cliente_autenticado.get('/painel')

  assert resposta.status_code == 200
  assert 'Não existem próximas retiradas'.encode('utf-8') in resposta.data


def test_dashboard_exige_autenticacao(client):
  resposta = client.get('/painel')

  assert resposta.status_code == 302
  assert '/login' in resposta.location
