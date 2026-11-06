import pytest

pytestmark = pytest.mark.usefixtures('autenticar_cliente')

def cadastrar_cliente(client):
  return client.post('/clientes/', json={
    'nome': 'João da Silva',
    'telefone': '11999999999'
  })


def cadastrar_pedido(client, cliente_id):
  return client.post('/pedidos/', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-10T14:00:00',
    'observacoes': 'Pedido para teste',
    'itens': [
      {
        'nome_produto': 'Bolo de chocolate',
        'quantidade': 2,
        'valor_unitario': 45.00
      }
    ]
  })


def test_cadastrar_pedido(client):
  cadastro_cliente = cadastrar_cliente(client)

  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  resposta = cadastrar_pedido(client, cliente_id)

  assert resposta.status_code == 201

  dados = resposta.get_json()

  assert dados['pedido']['cliente_id'] == cliente_id
  assert dados['pedido']['status'] == 'pendente'
  assert len(dados['pedido']['itens']) == 1
  assert dados['pedido']['itens'][0]['nome_produto'] == 'Bolo de chocolate'


def test_listar_pedidos(client):
  cadastro_cliente = cadastrar_cliente(client)

  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastrar_pedido(client, cliente_id)

  resposta = client.get('/pedidos/')

  assert resposta.status_code == 200

  dados = resposta.get_json()
  
  assert len(dados['pedidos']) == 1
  assert dados['pedidos'][0]['cliente_id'] == cliente_id


def test_buscar_pedido_por_id(client):
  cadastro_cliente = cadastrar_cliente(client)

  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastro_pedido = cadastrar_pedido(client, cliente_id)
  pedido_id = cadastro_pedido.get_json()['pedido']['id']

  resposta = client.get(f'/pedidos/{pedido_id}')

  assert resposta.status_code == 200

  dados = resposta.get_json()
  
  assert dados['pedido']['id'] == pedido_id
  assert dados['pedido']['cliente_id'] == cliente_id


def test_buscar_pedido_inexistente(client):
  resposta = client.get('/pedidos/999')

  assert resposta.status_code == 404


def test_listar_pedidos_por_cliente(client):
  cadastro_cliente = cadastrar_cliente(client)

  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastrar_pedido(client, cliente_id)
  cadastrar_pedido(client, cliente_id)

  resposta = client.get(f'/pedidos/cliente/{cliente_id}')

  assert resposta.status_code == 200

  dados = resposta.get_json()
  
  assert len(dados['pedidos']) == 2


def test_atualizar_pedido_completo(client):
  cadastro_cliente = cadastrar_cliente(client)
  
  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastro_pedido = cadastrar_pedido(client, cliente_id)
  pedido_id = cadastro_pedido.get_json()['pedido']['id']

  resposta = client.put(f'/pedidos/{pedido_id}', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-12T16:00:00',
    'observacoes': 'Pedido atualizado',
    'itens': [
      {
        'nome_produto': 'Torta de morango',
        'quantidade': 1,
        'valor_unitario': 60.00
      }
    ]
  })

  assert resposta.status_code == 200

  dados = resposta.get_json()
  
  assert dados['pedido']['observacoes'] == 'Pedido atualizado'
  assert dados['pedido']['itens'][0]['nome_produto'] == 'Torta de morango'


def test_atualizar_status_com_valor_invalido(client):
  resposta_cliente = cadastrar_cliente(client)
  
  cliente_id = resposta_cliente.get_json()['cliente']['id']

  cadastro = cadastrar_pedido(client, cliente_id)
  
  pedido_id = cadastro.get_json()['pedido']['id']

  resposta = client.patch(f'/pedidos/{pedido_id}', json={'status': 'cancelado'})

  assert resposta.status_code == 400


def test_atualizar_pedido_com_status_invalido(client):
  cadastro_cliente = cadastrar_cliente(client)
  
  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastro_pedido = cadastrar_pedido(client, cliente_id)
  pedido_id = cadastro_pedido.get_json()['pedido']['id']

  resposta = client.patch(f'/pedidos/{pedido_id}', json={'status': 'cancelado'})

  assert resposta.status_code == 400


def test_excluir_pedido(client):
  cadastro_cliente = cadastrar_cliente(client)

  cliente_id = cadastro_cliente.get_json()['cliente']['id']

  cadastro_pedido = cadastrar_pedido(client, cliente_id)
  pedido_id = cadastro_pedido.get_json()['pedido']['id']

  resposta = client.delete(f'/pedidos/{pedido_id}')

  assert resposta.status_code == 200

  consulta = client.get(f'/pedidos/{pedido_id}')

  assert consulta.status_code == 404


def test_cadastrar_pedido_com_cliente_inexistente(client):
  resposta = cadastrar_pedido(client, 999)

  assert resposta.status_code == 404

def test_cadastrar_pedido_com_cliente_inexistente(client):
  resposta = client.post('/pedidos/', json={
    'cliente_id': 999,
    'data_retirada': '2026-11-10T14:00:00',
    'observacoes': 'Pedido para teste',
    'itens': [
      {
        'nome_produto': 'Bolo de chocolate',
        'quantidade': 2,
        'valor_unitario': 45.00
      }
    ]
  })

  assert resposta.status_code == 404

def test_cadastrar_pedido_sem_itens(client):
  novo_cliente = cadastrar_cliente(client)

  cliente_id = novo_cliente.get_json()['cliente']['id']

  resposta = client.post('/pedidos/', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-10T14:00:00',
    'observacoes': 'Pedido para teste',
    'itens': []
  })

  assert resposta.status_code == 400

def test_cadastrar_pedido_com_quantidade_invalida(client):
  novo_cliente = cadastrar_cliente(client)

  cliente_id = novo_cliente.get_json()['cliente']['id']

  resposta = client.post('/pedidos/', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-10T14:00:00',
    'observacoes': 'Pedido para teste',
    'itens': [
      {
        'nome_produto': 'Bolo de chocolate',
        'quantidade': 0,
        'valor_unitario': 45.00
      }
    ]
  })

  assert resposta.status_code == 400

def test_cadastrar_pedido_com_valor_invalido(client):
  resposta_cliente = cadastrar_cliente(client)
  
  cliente_id = resposta_cliente.get_json()['cliente']['id']

  resposta = client.post('/pedidos/', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-10T14:00:00',
    'observacoes': 'Teste de valor',
    'itens': [
      {
        'nome_produto': 'Bolo de chocolate',
        'quantidade': 1,
        'valor_unitario': -10.00
      }
    ]
  })

  assert resposta.status_code == 400

def test_atualizar_pedido_inexistente(client):
  resposta = client.put('/pedidos/999', json={
    'cliente_id': 1,
    'data_retirada': '2026-11-12T15:00:00',
    'observacoes': 'Pedido inexistente',
    'itens': [
      {
        'nome_produto': 'Torta de limão',
        'quantidade': 1,
        'valor_unitario': 35.00
      }
    ]
  })

  assert resposta.status_code == 404