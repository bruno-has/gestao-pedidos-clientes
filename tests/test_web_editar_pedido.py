from datetime import datetime
from decimal import Decimal

import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.produto import Produto
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
    nome='Cliente Original',
    telefone='11999999999'
  )

  db.session.add(cliente)
  db.session.flush()

  pedido = Pedido(
    cliente_id=cliente.id,
    data_retirada=datetime(2026, 11, 10, 14, 0),
    status='em produção',
    observacoes='Observação original'
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


def criar_produto_teste(nome, valor):
  produto = Produto(
    nome=nome,
    valor_unitario=Decimal(valor)
  )

  db.session.add(produto)
  db.session.flush()

  return produto


def dados_edicao(cliente_id, produto_ids):
  return {
    'cliente_id': str(cliente_id),
    'data_retirada': '2026-11-12T15:30',
    'observacoes': 'Pedido atualizado',
    'produto_id[]': [str(produto_id) for produto_id in produto_ids],
    'quantidade[]': ['1', '10'][:len(produto_ids)]
  }


def test_exibir_formulario_edicao(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()
    pedido_id = pedido.id

  resposta = cliente_autenticado.get(
    f'/painel/pedidos/{pedido_id}/editar'
  )

  assert resposta.status_code == 200
  assert b'Editar pedido' in resposta.data
  assert b'Cliente Original' in resposta.data
  assert b'Bolo de chocolate' in resposta.data
  assert b'45.00' in resposta.data


def test_editar_pedido_com_sucesso(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()

    cliente_novo = Cliente(
      nome='Cliente Atualizado',
      telefone='11988887777'
    )

    db.session.add(cliente_novo)

    produto_bolo = criar_produto_teste(
      'Bolo de cenoura',
      '60.00'
    )

    produto_brigadeiro = criar_produto_teste(
      'Brigadeiro',
      '2.50'
    )

    db.session.commit()

    pedido_id = pedido.id
    cliente_novo_id = cliente_novo.id
    produto_bolo_id = produto_bolo.id
    produto_brigadeiro_id = produto_brigadeiro.id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data={
      'cliente_id': str(cliente_novo_id),
      'data_retirada': '2026-11-12T15:30',
      'observacoes': 'Pedido atualizado',
      'produto_id[]': [
        str(produto_bolo_id),
        str(produto_brigadeiro_id)
      ],
      'quantidade[]': ['1', '10']
    }
  )

  assert resposta.status_code == 302

  with app.app_context():
    pedido_atualizado = db.session.get(Pedido, pedido_id)

    assert pedido_atualizado.cliente_id == cliente_novo_id
    assert pedido_atualizado.status == 'em produção'
    assert pedido_atualizado.observacoes == 'Pedido atualizado'

    assert pedido_atualizado.data_retirada == datetime(2026, 11, 12, 15, 30)

    assert len(pedido_atualizado.itens) == 2

    itens = {
      item.nome_produto: item
      for item in pedido_atualizado.itens
    }

    assert itens['Bolo de cenoura'].quantidade == 1
    assert itens['Bolo de cenoura'].valor_unitario == Decimal('60.00')

    assert itens['Brigadeiro'].quantidade == 10
    assert itens['Brigadeiro'].valor_unitario == Decimal('2.50')


def test_rejeitar_edicao_com_quantidade_invalida(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()

    produto = criar_produto_teste(
      'Bolo de chocolate',
      '45.00'
    )

    db.session.commit()

    pedido_id = pedido.id
    cliente_id = pedido.cliente_id
    produto_id = produto.id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data={
      'cliente_id': str(cliente_id),
      'data_retirada': '2026-11-12T15:30',
      'observacoes': 'Pedido atualizado',
      'produto_id[]': [str(produto_id)],
      'quantidade[]': ['0']
    }
  )

  assert resposta.status_code == 200
  assert b'A quantidade deve ser um inteiro positivo' in resposta.data

  with app.app_context():
    pedido = db.session.get(Pedido, pedido_id)

    assert pedido.observacoes == 'Observação original'
    assert len(pedido.itens) == 1
    assert pedido.itens[0].nome_produto == 'Bolo de chocolate'
    assert pedido.itens[0].quantidade == 2


def test_editar_pedido_inexistente(cliente_autenticado):
  resposta = cliente_autenticado.get(
    '/painel/pedidos/9999/editar',
    follow_redirects=True
  )

  assert resposta.status_code == 200
  assert b'Pedido n' in resposta.data


def test_edicao_exige_autenticacao(client):
  resposta = client.get('/painel/pedidos/1/editar')

  assert resposta.status_code == 302
  assert '/login' in resposta.location


def test_bloquear_edicao_sem_token_csrf(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()

    produto = criar_produto_teste(
      'Bolo de chocolate',
      '45.00'
    )

    db.session.commit()

    pedido_id = pedido.id
    cliente_id = pedido.cliente_id
    produto_id = produto.id

  app.config['WTF_CSRF_ENABLED'] = True

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data={
      'cliente_id': str(cliente_id),
      'data_retirada': '2026-11-12T15:30',
      'observacoes': 'Pedido atualizado',
      'produto_id[]': [str(produto_id)],
      'quantidade[]': ['2']
  }
  )

  assert resposta.status_code == 400

  with app.app_context():
    pedido = db.session.get(Pedido, pedido_id)

    assert pedido.observacoes == 'Observação original'
    assert pedido.status == 'em produção'
