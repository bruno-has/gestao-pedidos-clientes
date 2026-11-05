from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.services.pedido_service import (
  cadastrar_pedido as salvar_pedido, 
  listar_pedidos,
  buscar_pedido_por_id,
  listar_pedidos_por_cliente,
  atualizar_pedido,
  atualizar_status_pedido,
  excluir_pedido,
)

STATUS_PERMITIDOS = {
  'pendente',
  'em produção',
  'concluído'
}

def serializar_pedido(pedido):
  total = sum((item.quantidade * item.valor_unitario for item in pedido.itens), Decimal('0.00'))

  return {
    'id': pedido.id,
    'cliente_id': pedido.cliente_id,
    'data_pedido': pedido.data_pedido.isoformat(
      sep=' ', 
      timespec='seconds'
    ) if pedido.data_pedido else None,
    'data_retirada': pedido.data_retirada.isoformat(
      sep=' ',
      timespec='minutes'
    ),
    'status': pedido.status,
    'observacoes': pedido.observacoes,
    'itens': [
      {
        'id': item.id,
        'nome_produto': item.nome_produto,
        'quantidade': item.quantidade,
        'valor_unitario': f'{item.valor_unitario:.2f}',
        'subtotal': f'{item.quantidade * item.valor_unitario:.2f}'
      }
      for item in pedido.itens
    ],
    'total': f'{total:.2f}'
  }

def validar_dados_pedido(dados):
  if not isinstance(dados, dict):
    return None, 'O corpo da requisição deve ser um objeto JSON'

  campos_permitidos = {'cliente_id', 'data_retirada', 'observacoes', 'itens'}
  campos_invalidos = set(dados.keys()) - campos_permitidos

  if campos_invalidos:
    return None, 'Foram enviados campos não permitidos'

  # valida ID do cliente
  cliente_id = dados.get('cliente_id')
  if (not isinstance(cliente_id, int) or isinstance(cliente_id, bool) or cliente_id <= 0):
    return None, 'Informe um ID de cliente válido'

  # valida a data de retirada
  data_retirada = dados.get('data_retirada')
  if not isinstance(data_retirada, str) or not data_retirada.strip():
    return None, 'A data de retirada é obrigatória'

  try:
    data_retirada = datetime.fromisoformat(data_retirada)

  except ValueError:
    return None, 'Informe uma data de retirada válida em formato ISO'

  # valida observacoes
  observacoes = dados.get('observacoes')
  if observacoes is not None and not isinstance(observacoes, str):
    return None, 'As observações devem ser um texto'

  if isinstance (observacoes, str):
    observacoes = observacoes.strip() or None

  # valida a lista de itens
  itens = dados.get('itens')
  if not isinstance(itens, list) or not itens:
    return None, 'Informe pelo menosum item para o pedido'

  itens_validados = []
  for indice, item in enumerate(itens, start=1):
    if not isinstance(item, dict):
      return None, f'O item {indice} deve ser um objeto JSON'

    campos_item = {
      'nome_produto', 
      'quantidade', 
      'valor_unitario'
    }

    if set(item.keys()) != campos_item:
      return None, f'O item {indice} possui campos inválidos ou ausentes'

    nome_produto = item['nome_produto']
    quantidade = item['quantidade']
    valor_unitario = item['valor_unitario']

    if not isinstance(nome_produto, str) or not nome_produto.strip():
      return None, f'Informe um nome válido para o produto do item {indice}'

    if (not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0):
      return None, f'A quantidade do item {indice} deve ser inteiro positivo'

    # converte o valor para Decimal
    if isinstance(valor_unitario, bool):
      return None, f'O valor unitário do item {indice} é inválido'

    try:
      valor_unitario = Decimal(str(valor_unitario))

      if not valor_unitario.is_finite() or valor_unitario <= 0:
        return None, f'O valor unitário do item {indice} deve ser positivo'

      if valor_unitario != valor_unitario.quantize(Decimal('0.01')):
        return None, f'O valor unitário do item {indice} deve ter no máximo duas casas decimais'

      if valor_unitario >= Decimal('100000000'):
        return None, f'O valor unitário do item {indice} excede o limite permitido'

    except (InvalidOperation, ValueError):
      return None, f'O valor unitário do item {indice} é inválido.'

    itens_validados.append({
      'nome_produto': nome_produto.strip(),
      'quantidade': quantidade,
      'valor_unitario': valor_unitario
    })

  return {
    'cliente_id': cliente_id,
    'data_retirada': data_retirada,
    'observacoes': observacoes,
    'itens': itens_validados
  }, None

def criar_pedido(dados):
  dados_validados, erro = validar_dados_pedido(dados)

  if erro:
    return {
      'erro': erro
    }, 400

  pedido = salvar_pedido(**dados_validados)

  if pedido is None:
    return {
      'erro': 'Cliente não encontrado.'
    }, 404

  return {
    'mensagem': 'Pedido cadastrado com sucesso!',
    'pedido': serializar_pedido(pedido)
  }, 201

def obter_pedidos():
  pedidos = listar_pedidos()

  return {
    'pedidos': [
      serializar_pedido(pedido)
      for pedido in pedidos
    ]
  }, 200

def obter_pedido_por_id(pedido_id):
  pedido = buscar_pedido_por_id(pedido_id)

  if pedido is None:
    return {
      'erro': 'Pedido não encontrado.'
    }, 404

  return {
    'pedido': serializar_pedido(pedido)
  }, 200


def obter_pedidos_por_cliente(cliente_id):
  pedidos = listar_pedidos_por_cliente(cliente_id)

  if pedidos is None:
    return {'erro': 'Cliente não encontrado.'}, 404

  return {
    'cliente_id': cliente_id,
    'pedidos': [
      serializar_pedido(pedido)
      for pedido in pedidos
    ]
  }, 200


def atualizar_pedido_completo(pedido_id, dados):
  dados_validados, erro = validar_dados_pedido(dados)

  if erro:
    return {
      'erro': erro
    }, 400

  pedido = atualizar_pedido(pedido_id, **dados_validados)

  if pedido is None:
    return {
      'erro': 'Pedido não encontrado.'
    }, 404

  if pedido is False:
    return {
      'erro': 'Cliente informado não encontrado.'
    }, 404

  return {
    'mensagem': 'Pedido atualizado com sucesso!',
    'pedido': serializar_pedido(pedido)
  }, 200


def atualizar_status(pedido_id, dados):
  if not isinstance(dados, dict):
    return {
      'erro': 'O corpo da requisição deve ser um objeto JSON.'
    }, 400

  if set(dados.keys()) != {'status'}:
    return {
      'erro': 'Informe somente o campo status.'
    }, 400

  status = dados.get('status')

  if not isinstance(status, str) or status not in STATUS_PERMITIDOS:
    return {
      'erro': 'Status inválido. Utilize: pendente, em produção ou concluído.'
    }, 400

  pedido = atualizar_status_pedido(pedido_id, status)

  if pedido is None:
    return {
      'erro': 'Pedido não encontrado.'
    }, 404

  return {
    'mensagem': 'Status do pedido atualizado com sucesso!',
    'pedido': serializar_pedido(pedido)
  }, 200


def excluir_pedido_por_id(pedido_id):
  resultado = excluir_pedido(pedido_id)

  if resultado is None:
    return {
      'erro': 'Pedido não encontrado.'
    }, 404

  return {
    'mensagem': 'Pedido excluído com sucesso!'
  }, 200