from app.services.cliente_service import (
  cadastrar_cliente, 
  listar_clientes,
  buscar_cliente_por_id,
  atualizar_cliente,
  atualizar_cliente_parcial,
  excluir_cliente,
)

def serializar_cliente(cliente):
  return {
    'id': cliente.id,
    'nome': cliente.nome,
    'telefone': cliente.telefone
  }

def criar_cliente(dados):
  if not isinstance(dados, dict):
    return {
      'erro': 'O corpo da requisição deve ser um objeto JSON'
    }, 400

  nome = dados.get('nome')
  telefone = dados.get('telefone')

  if not isinstance(nome, str) or not nome.strip():
    return {
      'erro': 'O nome do cliente é obrigatório'
    }, 400

  if not isinstance(telefone, str) or not telefone.strip():
    return {
      'erro': 'O telefone do cliente é obrigatório'
    }, 400

  cliente = cadastrar_cliente(nome.strip(), telefone.strip())

  return {
    'mensagem': 'Cliente cadastrado com sucesso',
    'cliente': serializar_cliente(cliente)
  }, 201

def obter_clientes():
  clientes = listar_clientes()

  return {
    'clientes': [
      serializar_cliente(cliente)
      for cliente in clientes
    ]
  }, 200

def obter_cliente_por_id(cliente_id): 
  cliente = buscar_cliente_por_id(cliente_id)

  if cliente is None:
    return {
      'erro': 'Cliente não encontrado'
    }, 404

  return {
    'cliente': serializar_cliente(cliente)
  }, 200

def atualizar_cliente_completo(cliente_id, dados):
  if not isinstance(dados, dict):
    return {
      'erro': 'O corpo da requisição deve ser um objeto JSON'
    }, 400

  nome = dados.get('nome')
  telefone = dados.get('telefone')

  if not isinstance(nome, str) or not nome.strip():
    return {
      'erro': 'O nome do cliente é obrigatório'
    }, 400

  if not isinstance(telefone, str) or not telefone.strip():
    return {
      'erro': 'O telefone do cliente é obrigatório'
    }, 400

  cliente = atualizar_cliente(cliente_id, nome.strip(), telefone.strip())

  if cliente is None:
    return {
      'erro': 'Cliente não encontrado'
    }, 404

  return {
    'mensagem': 'Cliente atualizado com sucesso',
    'cliente': serializar_cliente(cliente)
  }, 200

def atualizar_cliente_parcialmente(cliente_id, dados):
  if not isinstance(dados, dict):
    return {
      'erro': 'O corpo da requisição deve ser um objeto JSON'
    }, 400

  if not dados:
    return {
      'erro': 'Informe pelo menos um campo para atualização'
    }, 400

  campos_permitidos = {'nome', 'telefone'}
  campos_invalidos = set(dados.keys()) - campos_permitidos

  if campos_invalidos:
    return {
      'erro': 'Foram enviados campos não permitidos',
      'campos': list(campos_invalidos)
    }, 400

  if 'nome' in dados:
    if not isinstance(dados['nome'], str) or not dados['nome'].strip():
      return {
        'erro': 'O nome deve ser um texto válido'
      }, 400

  if 'telefone' in dados:
    if not isinstance(dados['telefone'], str) or not dados['telefone'].strip():
      return {
        'erro': 'O telefone deve ser um texto válido'
      }, 400

  dados_atualizados = {
    campo: valor.strip()
    for campo, valor in dados.items()
  }

  cliente = atualizar_cliente_parcial(cliente_id, dados_atualizados)

  if cliente is None:
    return {
      'erro': 'Cliente não encontrado'
    }, 404

  return {
    'mensagem': 'Cliente atualizado com sucesso',
    'cliente': serializar_cliente(cliente)
  }, 200

def excluir_cliente_por_id(cliente_id):
  resultado = excluir_cliente(cliente_id)

  if resultado is None:
    return {
      'erro': 'Cliente não encontrado'
    }, 404

  if resultado is False:
    return {
      'erro': 'Não é possível excluir o cliente, pois ele possui pedidos associados'
    }, 409

  return {
    'mensagem': 'Cliente excluído com sucesso'
  }, 200