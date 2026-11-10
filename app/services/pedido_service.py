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
  pedido = Pedido(cliente_id=cliente.id, data_retirada=data_retirada, observacoes=observacoes)

  # adiciona os itens ao pedido
  for item in itens:
    novo_item = ItemPedido(nome_produto=item['nome_produto'], quantidade=item['quantidade'], valor_unitario=item['valor_unitario'])

    pedido.itens.append(novo_item)

  
  db.session.add(pedido)
  db.session.commit()

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

  for item in itens:
    novo_item = ItemPedido(
      nome_produto=item['nome_produto'], 
      quantidade=item['quantidade'], 
      valor_unitario=item['valor_unitario']
    )
    pedido.itens.append(novo_item)

  db.session.commit()

  return pedido

def atualizar_status_pedido(pedido_id, status):
  pedido = db.session.get(Pedido, pedido_id)

  if pedido is None:
    return None

  pedido.status = status

  db.session.commit()

  return pedido

def excluir_pedido(pedido_id):
  pedido = db.session.get(Pedido, pedido_id)

  if pedido is None:
    return None

  db.session.delete(pedido)
  db.session.commit()

  return True