from app.extensions import db

class Cliente(db.Model): 
  __tablename__ = 'clientes'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nome = db.Column(db.String(100), nullable=False)
  telefone = db.Column(db.String(20), nullable=False)
  pedidos = db.relationship('Pedido', backref='cliente', lazy=True)