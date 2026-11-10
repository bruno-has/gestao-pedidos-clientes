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


def dados_edicao(cliente_id):
  return {
    'cliente_id': str(cliente_id),
    'data_retirada': '2026-11-12T15:30',
    'observacoes': 'Pedido atualizado',
    'nome_produto[]': [
      'Bolo de cenoura',
      'Brigadeiro'
    ],
    'quantidade[]': [
      '1',
      '10'
    ],
    'valor_unitario[]': [
      '60.00',
      '2.50'
    ]
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


def test_editar_pedido_com_sucesso(app, cliente_autenticado):
  with app.app_context():
    pedido = criar_pedido_teste()

    cliente_novo = Cliente(
      nome='Cliente Atualizado',
      telefone='11988887777'
    )

    db.session.add(cliente_novo)
    db.session.commit()

    pedido_id = pedido.id
    cliente_novo_id = cliente_novo.id

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data=dados_edicao(cliente_novo_id)
  )

  print(resposta.get_data(as_text=True))
  assert resposta.status_code == 302

  with app.app_context():
    pedido_atualizado = db.session.get(Pedido, pedido_id)

    assert pedido_atualizado.cliente_id == cliente_novo_id
    assert pedido_atualizado.status == 'em produção'
    assert pedido_atualizado.observacoes == 'Pedido atualizado'
    assert pedido_atualizado.data_retirada == datetime(
      2026, 11, 12, 15, 30
    )

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
    pedido_id = pedido.id
    cliente_id = pedido.cliente_id

  dados = dados_edicao(cliente_id)
  dados['quantidade[]'] = ['0', '10']

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data=dados
  )

  assert resposta.status_code == 200
  assert b'Confira os produtos' in resposta.data

  with app.app_context():
    pedido = db.session.get(Pedido, pedido_id)

    assert pedido.observacoes == 'Observação original'
    assert len(pedido.itens) == 1
    assert pedido.itens[0].nome_produto == 'Bolo de chocolate'


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
    pedido_id = pedido.id
    cliente_id = pedido.cliente_id

  app.config['WTF_CSRF_ENABLED'] = True

  resposta = cliente_autenticado.post(
    f'/painel/pedidos/{pedido_id}/editar',
    data=dados_edicao(cliente_id)
  )

  assert resposta.status_code == 400

  with app.app_context():
    pedido = db.session.get(Pedido, pedido_id)

    assert pedido.observacoes == 'Observação original'
    assert pedido.status == 'em produção'