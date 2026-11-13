from datetime import datetime
from decimal import Decimal

import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.services.auth_service import criar_usuario
from app.services.pedido_service import cadastrar_pedido


@pytest.fixture
def cliente_autenticado(client, app):
  with app.app_context():
    usuario = criar_usuario(
      nome='Maria',
      email='maria_produtos@teste.com',
      senha='senha12345'
    )

    usuario_id = usuario.id

  with client.session_transaction() as sess:
    sess['_user_id'] = str(usuario_id)
    sess['_fresh'] = True

  return client


def criar_produto_teste():
  produto = Produto(
    nome='Bolo de chocolate',
    valor_unitario=Decimal('45.00')
  )

  db.session.add(produto)
  db.session.commit()

  return produto


def test_listar_produtos(cliente_autenticado, app):
  with app.app_context():
    criar_produto_teste()

  resposta = cliente_autenticado.get('/painel/produtos')

  assert resposta.status_code == 200
  assert b'Bolo de chocolate' in resposta.data


def test_cadastrar_produto(cliente_autenticado):
  resposta = cliente_autenticado.post(
    '/painel/produtos/novo',
    data={
      'nome': 'Bolo de cenoura',
      'valor_unitario': '35.00'
    },
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Produto cadastrado com sucesso' in resposta.data

  produto = Produto.query.filter_by(
    nome='Bolo de cenoura'
  ).first()

  assert produto is not None
  assert produto.valor_unitario == Decimal('35.00')


def test_rejeitar_produto_com_valor_invalido(cliente_autenticado):
  resposta = cliente_autenticado.post(
    '/painel/produtos/novo',
    data={
      'nome': 'Bolo de cenoura',
      'valor_unitario': '-10'
    },
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Informe um valor unit' in resposta.data

  produto = Produto.query.filter_by(
    nome='Bolo de cenoura'
  ).first()

  assert produto is None


def test_editar_produto(cliente_autenticado, app):
  with app.app_context():
    produto = criar_produto_teste()
    produto_id = produto.id

  resposta = cliente_autenticado.post(
    f'/painel/produtos/{produto_id}/editar',
    data={
      'nome': 'Bolo de chocolate especial',
      'valor_unitario': '50.00'
    },
    follow_redirects=True
  )

  assert resposta.status_code == 200

  with app.app_context():
    produto = db.session.get(Produto, produto_id)

    assert produto.nome == 'Bolo de chocolate especial'
    assert produto.valor_unitario == Decimal('50.00')


def test_excluir_produto(cliente_autenticado, app):
  with app.app_context():
    produto = criar_produto_teste()
    produto_id = produto.id

  resposta = cliente_autenticado.post(
    f'/painel/produtos/{produto_id}/excluir',
    follow_redirects=True
  )

  assert resposta.status_code == 200

  with app.app_context():
    assert db.session.get(Produto, produto_id) is None


def test_excluir_produto_preserva_historico(
  cliente_autenticado,
  app
):
  with app.app_context():
    cliente = Cliente(
      nome='Cliente Teste',
      telefone='11999999999'
    )

    db.session.add(cliente)
    db.session.commit()

    produto = criar_produto_teste()

    produto_id = produto.id

    pedido = cadastrar_pedido(
      cliente_id=cliente.id,
      data_retirada=datetime(2026, 11, 15, 14, 0),
      observacoes='Pedido de teste',
      itens=[
        {
          'produto_id': produto.id,
          'nome_produto': produto.nome,
          'quantidade': 2,
          'valor_unitario': produto.valor_unitario
        }
      ]
    )

    pedido_id = pedido.id
    item_id = pedido.itens[0].id

  resposta = cliente_autenticado.post(
    f'/painel/produtos/{produto_id}/excluir',
    follow_redirects=True
  )

  assert resposta.status_code == 200

  with app.app_context():
    produto_excluido = db.session.get(Produto, produto_id)
    item = db.session.get(ItemPedido, item_id)

    assert produto_excluido is None
    assert item.produto_id is None
    assert item.nome_produto == 'Bolo de chocolate'
    assert item.quantidade == 2
    assert item.valor_unitario == Decimal('45.00')


def test_cadastrar_pedido_com_produto_selecionado(
  cliente_autenticado,
  app
):
  with app.app_context():
    cliente = Cliente(
      nome='Cliente Pedido',
      telefone='11988888888'
    )

    db.session.add(cliente)
    db.session.commit()

    cliente_id = cliente.id

    produto = criar_produto_teste()
    produto_id = produto.id

  resposta = cliente_autenticado.post(
    '/painel/pedidos/novo',
    data={
      'cliente_id': str(cliente_id),
      'data_retirada': '2026-11-15T14:00',
      'observacoes': 'Pedido com produto cadastrado',
      'produto_id[]': str(produto_id),
      'quantidade[]': '2'
    },
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido cadastrado com sucesso' in resposta.data

  with app.app_context():
    pedido = Pedido.query.filter_by(
      cliente_id=cliente_id
    ).first()

    assert pedido is not None
    assert len(pedido.itens) == 1

    item = pedido.itens[0]

    assert item.produto_id == produto_id
    assert item.nome_produto == 'Bolo de chocolate'
    assert item.quantidade == 2
    assert item.valor_unitario == Decimal('45.00')