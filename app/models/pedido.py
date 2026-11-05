from app.extensions import db

class Pedido(db.Model): 
  __tablename__ = 'pedidos'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
  data_pedido = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
  data_retirada = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.String(20), nullable=False, default='pendente')
  observacoes = db.Column(db.Text, nullable=True)
  itens = db.relationship('ItemPedido', backref='pedido', lazy=True)