from datetime import datetime, date
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
  listar_pedidos_por_periodo,
  excluir_pedido
)
from app.models.pedido import Pedido
from app.utils.pedido_helpers import (
  calcular_total_pedido,
  adicionar_total_pedidos,
  validar_itens_formulario
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
  pedidos_pendentes = Pedido.query.filter_by(status='pendente').count()
  pedidos_em_producao = Pedido.query.filter_by(status='em produção').count()
  pedidos_concluidos = Pedido.query.filter_by(status='concluído').count()

  proximas_retiradas = (
    Pedido.query.filter(
      Pedido.data_retirada >= datetime.now(),
      Pedido.status != 'concluído'
    ).order_by(Pedido.data_retirada.asc()).limit(5).all())

  return render_template(
    'dashboard.html',
    pedidos_pendentes=pedidos_pendentes,
    pedidos_em_producao=pedidos_em_producao,
    pedidos_concluidos=pedidos_concluidos,
    proximas_retiradas=proximas_retiradas
    )

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

  pedidos_com_total = adicionar_total_pedidos(pedidos)

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

  pedidos_com_total = adicionar_total_pedidos(pedidos)

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

    itens, erro = validar_itens_formulario(
      nomes, 
      quantidades, 
      valores, 
      ignorar_linhas_vazias=True
    )

    if erro:
      flash(erro, 'warning')
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

  total = calcular_total_pedido(pedido)

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
    itens, erro = validar_itens_formulario(
      nomes,
      quantidades,
      valores,
      ignorar_linhas_vazias=False
    )

    if erro:
      flash(erro, 'warning')
      return render_template(
        'pedido_editar.html',
        pedido=pedido,
        clientes=clientes,
        erro=erro
      ), 200

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
def relatorio():
  hoje = date.today()

  # Define o período padrão: primeiro dia do mês até hoje.
  primeiro_dia_mes = hoje.replace(day=1)

  inicio_texto = request.args.get(
    'data_inicio',
    primeiro_dia_mes.isoformat()
  )

  fim_texto = request.args.get(
    'data_fim',
    hoje.isoformat()
  )

  erro = None
  pedidos_com_total = []

  total_pedidos = 0
  valor_total = Decimal('0.00')

  pedidos_pendentes = 0
  pedidos_em_producao = 0
  pedidos_concluidos = 0

  try:
    data_inicio = date.fromisoformat(inicio_texto)
    data_fim = date.fromisoformat(fim_texto)

    if data_inicio > data_fim:
      raise ValueError(
        'A data inicial não pode ser posterior à data final.'
      )

    pedidos = listar_pedidos_por_periodo(
      data_inicio,
      data_fim
    )

    for pedido in pedidos:
      total_pedido = calcular_total_pedido(pedido)

      pedidos_com_total.append({
        'pedido': pedido,
        'total': total_pedido
      })

      valor_total += total_pedido

      if pedido.status == 'pendente':
        pedidos_pendentes += 1
      elif pedido.status == 'em produção':
        pedidos_em_producao += 1
      elif pedido.status == 'concluído':
        pedidos_concluidos += 1

    total_pedidos = len(pedidos)

  except ValueError as e:
    erro = str(e)

  return render_template(
    'relatorio.html',
    data_inicio=inicio_texto,
    data_fim=fim_texto,
    erro=erro,
    pedidos_com_total=pedidos_com_total,
    total_pedidos=total_pedidos,
    valor_total=valor_total,
    pedidos_pendentes=pedidos_pendentes,
    pedidos_em_producao=pedidos_em_producao,
    pedidos_concluidos=pedidos_concluidos
  )

@login_required
def sair():
  logout_user()

  flash('Você saiu do sistema', 'success')

  return redirect(url_for('web.login'))