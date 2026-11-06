from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.usuario import Usuario

def buscar_usuario_por_email(email):
  return Usuario.query.filter_by(email=email).first()

def autenticar_usuario(email, senha):
  usuario = buscar_usuario_por_email(email)

  if usuario is None:
    return None

  if not check_password_hash(usuario.senha, senha):
    return None

  return usuario

def criar_usuario(nome, email, senha):
  usuario_existente = buscar_usuario_por_email(email)

  if usuario_existente is not None:
    return None

  novo_usuario = Usuario(nome=nome, email=email, senha=generate_password_hash(senha))

  db.session.add(novo_usuario)
  db.session.commit()

  return novo_usuario