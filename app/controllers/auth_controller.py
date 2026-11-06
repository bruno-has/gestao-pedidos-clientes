from flask import request, jsonify
from flask_login import login_user, logout_user, current_user

from app.services.auth_service import autenticar_usuario

def login():
  if current_user.is_authenticated:
    return jsonify({
      'mensagem': 'Usuário já está autenticado'
  }), 200

  dados = request.get_json(silent=True)

  if not isinstance(dados, dict):
    return jsonify({
      'erro': 'Informe os dados de acesso em formato JSON'
  }), 400

  email = dados.get('email')
  senha = dados.get('senha')

  if not isinstance(email, str) or not email.strip():
    return jsonify({
      'erro': 'O email é obrigatório'
  }), 400

  if not isinstance(senha, str) or not senha:
    return jsonify({
      'erro': 'A senha é obrigatória'
  }), 400

  usuario = autenticar_usuario(email.strip(), senha)

  if usuario is None:
    return jsonify({
      'erro': 'Credenciais inválidas'
  }), 401

  login_user(usuario)

  return jsonify({
    'mensagem': 'Login realizado com sucesso',
    'usuario': {
      'id': usuario.id,
      'nome': usuario.nome,
      'email': usuario.email
    }
  }), 200

def logout():
  if not current_user.is_authenticated:
    return jsonify({
      'erro': 'Usuário não está autenticado'
  }), 401

  logout_user()

  return jsonify({
    'mensagem': 'Logout realizado com sucesso'
  }), 200

def usuario_autenticado():
  if not current_user.is_authenticated:
    return jsonify({
      'erro': 'Usuário não está autenticado'
  }), 401

  return jsonify({
    'usuario': {
      'id': current_user.id,
      'nome': current_user.nome,
      'email': current_user.email
    }
  }), 200