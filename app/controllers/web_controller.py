from datetime import datetime
from decimal import Decimal, InvalidOperation

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
from app.services.pedido_service import (
  cadastrar_pedido,
  listar_pedidos,
  buscar_pedido_por_id,
  atualizar_pedido,
  atualizar_status_pedido,
  listar_pedidos_por_cliente,
  excluir_pedido
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
def detalhes_cliente(cliente_id):
  cliente = buscar_cliente_por_id(cliente_id)
  if cliente is None:
    flash('Cliente não encontrado', 'warning')
    return redirect(url_for('web.clientes'))

  pedidos = listar_pedidos_por_cliente(cliente_id)
  pedidos_com_total = []

  for pedido in pedidos:
    total = sum(
      (
        item.quantidade * item.valor_unitario
        for item in pedido.itens
      ), Decimal('0.00')
    )

    pedidos_com_total.append({
      'pedido': pedido,
      'total': total
    })

  return render_template(
    'cliente_detalhes.html',
    cliente=cliente,
    pedidos=pedidos_com_total
  )

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

  pedidos = listar_pedidos()

  pedidos_com_total = []

  for pedido in pedidos:
    total = sum(
      (
        item.quantidade * item.valor_unitario
        for item in pedido.itens
      ), Decimal('0.00'))
    
    pedidos_com_total.append({
      'pedido': pedido,
      'total': total
    })

  return render_template('pedidos.html', pedidos=pedidos_com_total)

@login_required
def exibir_formulario_pedido(form_data=None):

  clientes = listar_clientes()

  return render_template(
    'pedido_form.html',
    clientes=clientes,
    form_data=form_data
  )

@login_required
def pagina_novo_pedido():

  if request.method == 'POST':
    cliente_id_texto = request.form.get('cliente_id', '').strip()
    data_retirada_texto = request.form.get('data_retirada', '').strip()
    observacoes = request.form.get('observacoes', '').strip()

    try:
      cliente_id = int(cliente_id_texto)
      if cliente_id <= 0:
        raise ValueError

    except (ValueError, TypeError):
      flash('Selecione um cliente válido', 'warning')
      return exibir_formulario_pedido(request.form)

    try:
      data_retirada = datetime.strptime(
        data_retirada_texto, 
        '%Y-%m-%dT%H:%M'
      )

    except ValueError:
      flash('Informe uma data e horário de retirada válidos', 'warning')
      return exibir_formulario_pedido(request.form)

    nomes = request.form.getlist('nome_produto[]')
    quantidades = request.form.getlist('quantidade[]')
    valores = request.form.getlist('valor_unitario[]')

    if not (len(nomes) == len(quantidades) == len(valores)):
      flash('Os dados dos itens do pedido estão inconsistentes', 'warning')
      return exibir_formulario_pedido(request.form)

    itens = []

    for nome, quantidade_texto, valor_texto in zip(
      nomes, 
      quantidades, 
      valores
    ):
      nome = nome.strip()
      quantidade_texto = quantidade_texto.strip()
      valor_texto = valor_texto.strip()

      if not nome and not quantidade_texto and not valor_texto:
        continue

      if not nome or not quantidade_texto or not valor_texto:
        flash('Preencha todos os campos de cada item', 'warning')
        return exibir_formulario_pedido(request.form)

      if len(nome) > 100: 
        flash('O nome do produto deve ter até 100 caracteres', 'warning')
        return exibir_formulario_pedido(request.form)

      try:
        quantidade = int(quantidade_texto)
        if quantidade <= 0:
          raise ValueError

      except (ValueError, TypeError):
        flash('A quantidade de cada item deve ser um inteiro positivo', 'warning')
        return exibir_formulario_pedido(request.form)

      try:
        valor_unitario = Decimal(valor_texto)
        
        if (
          not valor_unitario.is_finite()
          or valor_unitario <= 0
          or valor_unitario >= Decimal('100000000') 
          or valor_unitario.as_tuple().exponent < -2
        ):
          raise InvalidOperation

      except (InvalidOperation, ValueError):
        flash('Informe um valor unitário positivo com no máximo duas casas decimais', 'warning')
        return exibir_formulario_pedido(request.form)

      itens.append({
        'nome_produto': nome, 
        'quantidade': quantidade,
        'valor_unitario': valor_unitario
      })

    if not itens:
      flash('Adicione pelo menos um item ao pedido', 'warning')
      return exibir_formulario_pedido(request.form)

    pedido = cadastrar_pedido(
      cliente_id=cliente_id, 
      data_retirada=data_retirada, 
      observacoes=observacoes, 
      itens=itens
    )

    if pedido is None:
      flash('O cliente selecionado não foi encontrado', 'warning')
      return exibir_formulario_pedido(request.form)

    flash('Pedido cadastrado com sucesso', 'success')

    return redirect(url_for('web.pedidos'))

  return exibir_formulario_pedido()

@login_required
def detalhes_pedido(pedido_id):
  pedido = buscar_pedido_por_id(pedido_id)

  if pedido is None:
    flash('Pedido não encontrado', 'warning')
    return redirect(url_for('web.pedidos'))

  total = sum(
    (
      item.quantidade * item.valor_unitario
      for item in pedido.itens
    ), Decimal('0.00')
  )

  return render_template(
    'pedido_detalhes.html', 
    pedido=pedido,
    total=total
  )

@login_required 
def atualizar_status_pedido_web(pedido_id):
  status = request.form.get('status', '').strip()

  status_permitido = [
    'pendente', 
    'em produção', 
    'concluído'
  ]

  if status not in status_permitido:
    flash('Selecione um status válido', 'warning')
    return redirect(url_for('web.detalhes_pedido', pedido_id=pedido_id))

  pedido = atualizar_status_pedido(pedido_id, status)
  if pedido is None:
    flash('Pedido não encontrado', 'warning')
    return redirect(url_for('web.pedidos'))

  flash('Status do pedido alterado com sucesso', 'success')
  return redirect(url_for('web.detalhes_pedido', pedido_id=pedido_id))

@login_required
def editar_pedido(pedido_id):
  pedido = buscar_pedido_por_id(pedido_id)
  if pedido is None:
    flash('Pedido não encontrado', 'warning')
    return redirect(url_for('web.pedidos'))

  clientes = listar_clientes()

  if request.method == 'POST':
    try:
      cliente_id = int(request.form.get('cliente_id', ''))
      if cliente_id <= 0:
        raise ValueError

    except (ValueError, TypeError):
      flash('Selecione um cliente válido', 'warning')
      return render_template(
        'pedido_editar.html', 
        pedido=pedido, 
        clientes=clientes
      )

    cliente = buscar_cliente_por_id(cliente_id)
    if cliente is None:
      flash('O cliente selecionado não existe', 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido, 
        clientes=clientes
      )

    try:
      data_retirada = datetime.strptime(
        request.form.get('data_retirada', ''), '%Y-%m-%dT%H:%M'
      )

    except ValueError:
      flash('Informe uma data de retirada válida', 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido,
        clientes=clientes
      )

    nomes = request.form.getlist('nome_produto[]')
    quantidades = request.form.getlist('quantidade[]')
    valores = request.form.getlist('valor_unitario[]')

    if not nomes or not (len(nomes) == len(quantidades) == len(valores)):
      flash('Informe pelo menos um item válido', 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido,
        clientes=clientes
      )

    itens = []

    try:
      for nome, quantidade, valor in zip(nomes, quantidades, valores):
        nome = nome.strip()
        if not nome or len(nome) > 100:
          raise ValueError

        quantidade = int(quantidade)
        if quantidade <= 0:
          raise ValueError

        valor = Decimal(valor)
        if (
          not valor.is_finite()
          or valor <= 0
          or valor >= Decimal('100000000')
          or valor.as_tuple().exponent < -2
        ):
          raise ValueError

        itens.append({
          'nome_produto': nome,
          'quantidade': quantidade,
          'valor_unitario': valor
        })

    except (ValueError, TypeError, InvalidOperation):
      flash('Confira os produtos, quantidades e valores informados', 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido,
        clientes=clientes
      )

    observacoes = request.form.get('observacoes', '').strip()

    resultado = atualizar_pedido(
      pedido_id,
      cliente_id,
      data_retirada,
      observacoes,
      itens
    )

    if resultado is None:
      flash('Pedido não encontrado')
      return redirect(url_for('web.pedidos'))

    if resultado is False:
      flash('O cliente selecionado não existe', 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido,
        clientes=clientes
      )

    flash('Pedido atualizado com sucesso', 'success')
    return redirect(url_for('web.detalhes_pedido', pedido_id=pedido_id))

  return render_template(
    'pedido_editar.html',
    pedido=pedido,
    clientes=clientes
  )

@login_required
def excluir_pedido_web(pedido_id):
  resultado = excluir_pedido(pedido_id)
  if resultado is None:
    flash('Pedido não encontrado.', 'warning')
  else:
    flash('Pedido excluído com sucesso!', 'success')

  return redirect(url_for('web.pedidos'))

@login_required
def sair():
  logout_user()

  flash('Você saiu do sistema', 'success')

  return redirect(url_for('web.login'))