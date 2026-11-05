from app.extensions import db
from app.models.cliente import Cliente

def cadastrar_cliente(nome, telefone):
  cliente = Cliente(nome=nome, telefone=telefone)
  db.session.add(cliente)
  db.session.commit()

  return cliente

def listar_clientes():
  return Cliente.query.order_by(Cliente.nome).all()

def buscar_cliente_por_id(cliente_id):
  return db.session.get(Cliente, cliente_id)

def atualizar_cliente(cliente_id, nome, telefone):
  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return None

  cliente.nome = nome
  cliente.telefone = telefone
  db.session.commit()

  return cliente

def atualizar_cliente_parcial(cliente_id, dados):
  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return None

  if 'nome' in dados:
    cliente.nome = dados['nome']

  if 'telefone' in dados:
    cliente.telefone = dados['telefone']

  db.session.commit()

  return cliente

def excluir_cliente(cliente_id):
  cliente = db.session.get(Cliente, cliente_id)

  if cliente is None:
    return None

  if cliente.pedidos:
    return False

  db.session.delete(cliente)
  db.session.commit()

  return True