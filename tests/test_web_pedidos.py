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
    data_retirada=datetime(2026, 11, 10, 14, 0),
    status='pendente',
    observacoes='Pedido para teste'
  )

  item = ItemPedido(
    nome_produto='Bolo de chocolate',
    quantidade=2,
    valor_unitario=Decimal('45.00')
  )

  pedido.itens.append(item)

  db.session.add(pedido)
  db.session.commit()

  return pedido


def test_listar_pedidos_web(app, cliente_autenticado):
  with app.app_context():
    criar_pedido_teste()

  resposta = cliente_autenticado.get('/painel/pedidos')

  assert resposta.status_code == 200
  assert b'Cliente Teste' in resposta.data
  assert b'Bolo de chocolate' in resposta.data


def test_exibir_detalhes_pedido(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  resposta = cliente_autenticado.get(
    f'/painel/pedidos/{pedido_id}'
  )

  assert resposta.status_code == 200
  assert b'Cliente Teste' in resposta.data
  assert b'11999999999' in resposta.data
  assert b'Bolo de chocolate' in resposta.data
  assert b'90,00' in resposta.data


def test_detalhes_pedido_inexistente(cliente_autenticado):
  resposta = cliente_autenticado.get(
    '/painel/pedidos/9999',
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido n' in resposta.data


@pytest.mark.parametrize(
  'status',
  ['pendente', 'em produção', 'concluído']
)
def test_atualizar_status_pedido(app, cliente_autenticado, status):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/status',
    data={'status': status}
  )

  assert resposta.status_code == 302

  with app.app_context():
    pedido_atualizado = db.session.get(Pedido, pedido_id)

    assert pedido_atualizado.status == status


def test_rejeitar_status_invalido(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/status',
    data={'status': 'cancelado'}
  )

  assert resposta.status_code == 302

  with app.app_context():
    pedido_atualizado = db.session.get(Pedido, pedido_id)

    assert pedido_atualizado.status == 'pendente'


def test_atualizar_status_pedido_inexistente(cliente_autenticado):
  resposta = cliente_autenticado.post(
    '/painel/pedidos/9999/status',
    data={'status': 'concluído'},
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido n' in resposta.data


def test_bloquear_atualizacao_status_sem_token_csrf(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  app.config['WTF_CSRF_ENABLED'] = True

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/status',
    data={'status': 'em produção'}
  )

  assert resposta.status_code == 400

  with app.app_context():
    pedido_atualizado = db.session.get(Pedido, pedido_id)

    assert pedido_atualizado.status == 'pendente'
