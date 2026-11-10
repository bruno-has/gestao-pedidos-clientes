
from datetime import datetime
from decimal import Decimal

import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
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


def criar_pedido_teste():
  cliente = Cliente(
    nome='Cliente Teste',
    telefone='11999999999'
  )

  db.session.add(cliente)
  db.session.flush()

  pedido = Pedido(
    cliente_id=cliente.id,
    data_retirada=datetime(2026, 11, 12, 15, 30),
    status='pendente',
    observacoes='Pedido para teste'
  )

  pedido.itens.append(
    ItemPedido(
      nome_produto='Bolo de chocolate',
      quantidade=2,
      valor_unitario=Decimal('45.00')
    )
  )

  db.session.add(pedido)
  db.session.commit()

  return pedido


def test_excluir_pedido_com_sucesso(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id
    cliente_id = pedido.cliente_id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/excluir',
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido exclu' in resposta.data

  with app.app_context():
    assert db.session.get(Pedido, pedido_id) is None

    itens = ItemPedido.query.filter_by(pedido_id=pedido_id).all()

    assert len(itens) == 0

    assert db.session.get(Cliente, cliente_id) is not None


def test_excluir_pedido_inexistente(cliente_autenticado):
  resposta = cliente_autenticado.post(
    '/painel/pedidos/9999/excluir',
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido n' in resposta.data


def test_exclusao_exige_autenticacao(client):
  resposta = client.post('/painel/pedidos/1/excluir')

  assert resposta.status_code == 302
  assert '/login' in resposta.location


def test_bloquear_exclusao_sem_token_csrf(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  app.config['WTF_CSRF_ENABLED'] = True

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/excluir'
  )

  assert resposta.status_code == 400

  with app.app_context():
    assert db.session.get(Pedido, pedido_id) is not None

    itens = ItemPedido.query.filter_by(pedido_id=pedido_id).all()

    assert len(itens) == 1
