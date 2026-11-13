from app.extensions import db
from app.models.produto import Produto

def cadastrar_produto(nome, valor_unitario):
  produto = Produto(
    nome=nome,
    valor_unitario=valor_unitario
  )

  db.session.add(produto)
  _commit()

  return produto


def listar_produtos():
  return Produto.query.order_by(Produto.nome).all()


def buscar_produto_por_id(produto_id):
  return db.session.get(Produto, produto_id)


def atualizar_produto(produto_id, nome, valor_unitario):
  produto = buscar_produto_por_id(produto_id)

  if produto is None:
    return None

  produto.nome = nome
  produto.valor_unitario = valor_unitario

  _commit()

  return produto


def excluir_produto(produto_id):
  produto = buscar_produto_por_id(produto_id)

  if produto is None:
    return None

  # Preserva os dados históricos dos pedidos
  for item in produto.itens:
    item.produto_id = None

  db.session.delete(produto)
  _commit()

  return True


def _commit():
  try:
    db.session.commit()
  except Exception:
    db.session.rollback()
    raise