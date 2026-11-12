from app.extensions import db

class ItemPedido(db.Model): 
  __tablename__ = 'itens_pedido'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
  produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id', ondelete='SET NULL'), nullable=True)
  nome_produto = db.Column(db.String(100), nullable=False)
  quantidade = db.Column(db.Integer, nullable=False)
  valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
