from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from werkzeug.security import generate_password_hash


def autenticar_usuario(client):
  usuario = Usuario(
    nome='Usuário de teste',
    email='relatorio@teste.com',
    senha=generate_password_hash('senha123')
  )

  db.session.add(usuario)
  db.session.commit()

  with client.session_transaction() as sess:
    sess['_user_id'] = str(usuario.id)
    sess['_fresh'] = True


def criar_pedido(
  cliente,
  data_pedido,
  status='pendente',
  quantidade=2,
  valor_unitario=Decimal('10.00')
):
  pedido = Pedido(
    cliente_id=cliente.id,
    data_pedido=data_pedido,
    data_retirada=datetime(2026, 12, 10, 14, 0),
    status=status,
    observacoes='Pedido de teste'
  )

  pedido.itens.append(
    ItemPedido(
      nome_produto='Bolo de teste',
      quantidade=quantidade,
      valor_unitario=valor_unitario
    )
  )

  db.session.add(pedido)
  db.session.commit()

  return pedido


def preparar_cliente():
  cliente = Cliente(
    nome='Maria da Silva',
    telefone='11999999999'
  )

  db.session.add(cliente)
  db.session.commit()

  return cliente


def test_relatorio_exige_autenticacao(client):
  resposta = client.get('/painel/relatorio')

  assert resposta.status_code == 302
  assert '/login' in resposta.location


def test_relatorio_exibe_indicadores(client):
  autenticar_usuario(client)
  cliente = preparar_cliente()

  criar_pedido(
    cliente,
    datetime(2026, 11, 5, 10, 0),
    'pendente',
    2,
    Decimal('10.00')
  )

  criar_pedido(
    cliente,
    datetime(2026, 11, 6, 11, 0),
    'em produção',
    1,
    Decimal('30.00')
  )

  criar_pedido(
    cliente,
    datetime(2026, 11, 7, 12, 0),
    'concluído',
    3,
    Decimal('15.00')
  )

  resposta = client.get(
    '/painel/relatorio?data_inicio=2026-11-01&data_fim=2026-11-30'
  )

  assert resposta.status_code == 200
  assert b'Total de pedidos' in resposta.data
  assert b'Valor total' in resposta.data
  assert b'Pendentes' in resposta.data
  assert b'Em produ' in resposta.data
  assert b'Conclu' in resposta.data

  assert b'>3<' in resposta.data
  assert b'R$ 95,00' in resposta.data


def test_relatorio_filtra_pedidos_por_periodo(client):
  autenticar_usuario(client)
  cliente = preparar_cliente()

  criar_pedido(
    cliente,
    datetime(2026, 10, 31, 23, 59),
    'pendente'
  )

  criar_pedido(
    cliente,
    datetime(2026, 11, 10, 10, 0),
    'pendente'
  )

  criar_pedido(
    cliente,
    datetime(2026, 11, 30, 23, 59),
    'concluído'
  )

  criar_pedido(
    cliente,
    datetime(2026, 12, 1, 0, 0),
    'pendente'
  )

  resposta = client.get(
    '/painel/relatorio?data_inicio=2026-11-01&data_fim=2026-11-30'
  )

  assert resposta.status_code == 200
  assert b'Total de pedidos' in resposta.data
  assert b'2 pedido(s) encontrado(s)' in resposta.data


def test_relatorio_sem_pedidos_no_periodo(client):
  autenticar_usuario(client)

  resposta = client.get(
    '/painel/relatorio?data_inicio=2026-11-01&data_fim=2026-11-30'
  )

  assert resposta.status_code == 200
  assert b'0 pedido(s) encontrado(s)' in resposta.data
  assert b'Nenhum pedido encontrado neste per' in resposta.data
  assert b'R$ 0,00' in resposta.data


def test_relatorio_rejeita_periodo_invertido(client):
  autenticar_usuario(client)

  resposta = client.get(
    '/painel/relatorio?data_inicio=2026-11-30&data_fim=2026-11-01'
  )

  assert resposta.status_code == 200
  assert b'A data inicial n' in resposta.data


def test_relatorio_rejeita_data_invalida(client):
  autenticar_usuario(client)

  resposta = client.get(
    '/painel/relatorio?data_inicio=data-invalida&data_fim=2026-11-30'
  )

  assert resposta.status_code == 200
  assert b'Erro' not in resposta.data
  assert b'invalid' in resposta.data.lower()