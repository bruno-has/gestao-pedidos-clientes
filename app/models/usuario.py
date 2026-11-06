from app.extensions import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model): 
  __tablename__ = 'usuarios'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nome = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(150), unique=True, nullable=False)
  senha = db.Column(db.String(255), nullable=False)
  data_criacao = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())