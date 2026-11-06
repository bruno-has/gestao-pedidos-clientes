from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from app.services.auth_service import autenticar_usuario
from app.services.cliente_service import (
  cadastrar_cliente,
  listar_clientes,
  buscar_cliente_por_id,
  atualizar_cliente,
  excluir_cliente
)

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

  clientes = listar_clientes()

  return render_template('clientes.html', clientes=clientes)

@login_required
def novo_cliente():

  if request.method == 'POST':
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()

    if len(nome) < 3:
      flash('O nome deve possuir pelo menos 3 caracteres', 'warning')
      return render_template('cliente_form.html', cliente=None)

    if not telefone:
      flash('O telefone é obrigatório', 'warning')
      return render_template('cliente_form.html', cliente=None)

    cadastrar_cliente(nome, telefone)
    flash('Cliente cadastrado com sucesso', 'success')

    return redirect(url_for('web.clientes'))

  return render_template('cliente_form.html', cliente=None)

@login_required
def editar_cliente(cliente_id):

  cliente = buscar_cliente_por_id(cliente_id)

  if cliente is None:
    flash('Cliente não encontrado', 'warning')
    return redirect(url_for('web.clientes'))

  if request.method == 'POST':
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()

    if len(nome) < 3:
      flash('O nome deve possuir pelo menos 3 caracteres', 'warning')
      return render_template('cliente_form.html', cliente=cliente)

    if not telefone:
      flash('O telefone é obrigatório', 'warning')
      return render_template('cliente_form.html', cliente=cliente)

    atualizar_cliente(cliente_id, nome, telefone)
    flash('Cliente atualizado com sucesso', 'success')

    return redirect(url_for('web.clientes'))

  return render_template('cliente_form.html', cliente=cliente) 

@login_required
def excluir_cliente_web(cliente_id):
    
  resultado = excluir_cliente(cliente_id)

  if resultado is None:
    flash('Cliente não encontrado', 'warning')

  elif resultado is False:
    flash('Não é possível excluir um cliente que possui pedidos associados', 'danger')

  else:
    flash('Cliente excluído com sucesso', 'success')

  return redirect(url_for('web.clientes'))

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