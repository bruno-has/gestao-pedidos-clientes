from app.extensions import db

class Produto(db.Model):
  __tablename__ = 'produtos'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nome = db.Column(db.String(100), nullable=False)
  valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
  itens = db.relationship('ItemPedido', backref='produto', lazy=True)