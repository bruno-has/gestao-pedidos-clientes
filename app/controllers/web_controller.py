from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from app.services.auth_service import autenticar_usuario

def login_page():
  if current_user.is_authenticated:
    return redirect(url_for('web.painel'))

  if request.method == 'POST':
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '')

    if not email or not senha:
      flash('Informe o email e a senha', 'warning')
      return render_template('login.html')

    usuario = autenticar_usuario(email, senha)

    if usuario is None:
      flash('Email ou senha inválidos', 'danger')
      return render_template('login.html')

    login_user(usuario)

    flash('Login realizado com sucesso', 'success')

    return redirect(url_for('web.painel'))

  return render_template('login.html')

@login_required
def painel():
  return render_template('dashboard.html')

@login_required
def pagina_clientes():
  return render_template(
    'em_desenvolvimento.html', 
    titulo='Clientes', 
    descricao='Aqui ficará o gerenciamento dos clientes cadastrados'
  )

@login_required
def pagina_pedidos():
  return render_template(
    'em_desenvolvimento.html',
    titulo='Pedidos',
    descricao='Aqui ficará a listagem e o acompanhamento dos pedidos'
  )

@login_required
def pagina_novo_pedido():
  return render_template(
    'em_desenvolvimento.html',
    titulo='Novo Pedido',
    descricao='Aqui ficará o formulário de cadastro de novos pedidos'
  )

@login_required
def sair():
  logout_user()

  flash('Você saiu do sistema', 'success')

  return redirect(url_for('web.login'))