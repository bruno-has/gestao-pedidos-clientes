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


def criar_cliente_com_pedido():
  cliente = Cliente(
    nome='Cliente Histórico',
    telefone='11988887777'
  )

  db.session.add(cliente)
  db.session.flush()

  pedido = Pedido(
    cliente_id=cliente.id,
    data_retirada=datetime(2026, 11, 10, 14, 0),
    status='pendente',
    observacoes='Pedido de teste do histórico'
  )

  item = ItemPedido(
    nome_produto='Bolo de chocolate',
    quantidade=2,
    valor_unitario=Decimal('45.00')
  )

  pedido.itens.append(item)

  db.session.add(pedido)
  db.session.commit()

  return cliente


def test_exibir_detalhes_cliente_com_historico(app, cliente_autenticado):
  with app.app_context():
    cliente = criar_cliente_com_pedido()
    cliente_id = cliente.id

  resposta = cliente_autenticado.get(
    f'/painel/clientes/{cliente_id}'
  )

  assert resposta.status_code == 200
  assert b'Cliente Hist' in resposta.data
  assert b'11988887777' in resposta.data
  assert b'Historico de pedidos' in resposta.data or b'Hist' in resposta.data
  assert b'Bolo de chocolate' not in resposta.data
  assert b'90,00' in resposta.data
  assert b'Ver pedido' in resposta.data


def test_exibir_cliente_sem_pedidos(app, cliente_autenticado):
  with app.app_context():
    cliente = Cliente(
      nome='Cliente Sem Pedidos',
      telefone='11977776666'
    )

    db.session.add(cliente)
    db.session.commit()

    cliente_id = cliente.id

  resposta = cliente_autenticado.get(
    f'/painel/clientes/{cliente_id}'
  )

  assert resposta.status_code == 200
  assert b'Cliente Sem Pedidos' in resposta.data
  assert b'Nenhum pedido encontrado' in resposta.data
  assert b'0' in resposta.data


def test_detalhes_cliente_inexistente(cliente_autenticado):
  resposta = cliente_autenticado.get(
    '/painel/clientes/9999',
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Cliente n' in resposta.data


def test_detalhes_cliente_exige_autenticacao(client):
  resposta = client.get('/painel/clientes/1')

  assert resposta.status_code == 302
  assert '/login' in resposta.location