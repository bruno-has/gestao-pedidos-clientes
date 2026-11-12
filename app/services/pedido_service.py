from datetime import datetime, time, timedelta

from app.extensions import db
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido

def cadastrar_pedido(cliente_id, data_retirada, observacoes, itens):
  # verifica se cliente existe
  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return None

  # cria o pedido
  pedido = Pedido(
    cliente_id=cliente.id, 
    data_retirada=data_retirada, 
    observacoes=observacoes
  )

  # adiciona os itens ao pedido
  pedido.itens.extend(_criar_itens_pedido(itens))
  
  db.session.add(pedido)
  _commit()

  return pedido

def listar_pedidos():
  return Pedido.query.order_by(Pedido.data_retirada).all()

def buscar_pedido_por_id(pedido_id):
  return db.session.get(Pedido, pedido_id)

def listar_pedidos_por_cliente(cliente_id):
  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return None

  return Pedido.query.filter_by(cliente_id=cliente_id).order_by(Pedido.data_retirada).all()

def listar_pedidos_por_periodo(data_inicio, data_fim):
  inicio = datetime.combine(data_inicio, time.min)
  fim = datetime.combine(data_fim + timedelta(days=1), time.min)

  return (
    Pedido.query.filter(
      Pedido.data_pedido >= inicio,
      Pedido.data_pedido < fim
    ).order_by(Pedido.data_pedido.desc()).all()
  )

def atualizar_pedido(pedido_id, cliente_id, data_retirada, observacoes, itens):
  pedido = db.session.get(Pedido, pedido_id)
  
  if pedido is None:
    return None

  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return False

  pedido.cliente_id = cliente_id
  pedido.data_retirada = data_retirada
  pedido.observacoes = observacoes
  pedido.itens.clear()
  pedido.itens.extend(_criar_itens_pedido(itens))

  _commit()

  return pedido

def atualizar_status_pedido(pedido_id, status):
  pedido = db.session.get(Pedido, pedido_id)

  if pedido is None:
    return None

  pedido.status = status

  _commit()

  return pedido

def excluir_pedido(pedido_id):
  pedido = db.session.get(Pedido, pedido_id)

  if pedido is None:
    return None

  db.session.delete(pedido)
  _commit()

  return True

def _criar_itens_pedido(itens):
  return [
    ItemPedido(
      produto_id=item.get('produto_id'),
      nome_produto=item['nome_produto'],
      quantidade=item['quantidade'],
      valor_unitario=item['valor_unitario']
    ) for item in itens
  ]

def _commit():
  try: 
    db.session.commit()
  except Exception:
    db.session.rollback()
    raise