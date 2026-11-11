import pytest

pytestmark = pytest.mark.usefixtures('autenticar_cliente')

def cadastrar_cliente(client):
  return client.post('/clientes/', json={
    'nome': 'João da Silva',
    'telefone': '11999999999'
  })

def test_cadastrar_cliente(client):
  resposta = cadastrar_cliente(client)

  assert resposta.status_code == 201

  dados = resposta.get_json()

  assert dados['mensagem'] == 'Cliente cadastrado com sucesso'
  assert dados['cliente']['nome'] == 'João da Silva'
  assert dados['cliente']['telefone'] == '11999999999'

def test_cadastrar_cliente_dados_invalidos(client):
  resposta = client.post('/clientes/', json=['lista', 'inválida'])

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O corpo da requisição deve ser um objeto JSON'

def test_cadastrar_cliente_sem_nome(client):
  resposta = client.post('/clientes/', json={
    'telefone': '11999999999'
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O nome do cliente é obrigatório'

def test_cadastrar_cliente_nome_vazio(client):
  resposta = client.post('/clientes/', json={
    'nome': '',
    'telefone': '11999999999'
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O nome do cliente é obrigatório'

def test_cadastrar_cliente_nome_apenas_espacos(client):
  resposta = client.post('/clientes/', json={
    'nome': '    ',
    'telefone': '11999999999'
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O nome do cliente é obrigatório'

def test_cadastrar_cliente_sem_telefone(client):
  resposta = client.post('/clientes/', json={
    'nome': 'João da Silva'
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O telefone do cliente é obrigatório'

def test_cadastrar_cliente_telefone_vazio(client):
  resposta = client.post('/clientes/', json={
    'nome': 'João da Silva',
    'telefone': ''
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O telefone do cliente é obrigatório'

def test_cadastrar_cliente_telefone_somente_espacos(client):
  resposta = client.post('/clientes/', json={
    'nome': 'João da Silva',
    'telefone': '      '
  })

  assert resposta.status_code == 400

  dados = resposta.get_json()

  assert dados['erro'] == 'O telefone do cliente é obrigatório'

def test_listar_clientes(client):
  cadastrar_cliente(client)

  resposta = client.get('/clientes/')

  assert resposta.status_code == 200

  dados = resposta.get_json()

  assert len(dados['clientes'])  == 1
  assert dados['clientes'][0]['nome'] == 'João da Silva'

def test_buscar_cliente_por_id(client):
  cadastro = cadastrar_cliente(client)

  cliente_id = cadastro.get_json()['cliente']['id']
  resposta = client.get(f'/clientes/{cliente_id}')

  assert resposta.status_code == 200

  dados = resposta.get_json()

  assert dados['cliente']['id'] == cliente_id
  assert dados['cliente']['nome'] == 'João da Silva'


def test_buscar_cliente_inexistente(client):
  resposta = client.get('/clientes/999')

  assert resposta.status_code == 404


def test_atualizar_cliente_completo(client):
  cadastro = cadastrar_cliente(client)

  cliente_id = cadastro.get_json()['cliente']['id']

  resposta = client.put(f'/clientes/{cliente_id}', json={
    'nome': 'Maria Oliveira',
    'telefone': '11988888888'
  })

  assert resposta.status_code == 200

  dados = resposta.get_json()

  assert dados['cliente']['nome'] == 'Maria Oliveira'
  assert dados['cliente']['telefone'] == '11988888888'

def test_atualizar_cliente_parcialmente(client):
  cadastro = cadastrar_cliente(client)

  cliente_id = cadastro.get_json()['cliente']['id']

  resposta = client.patch(f'/clientes/{cliente_id}', json={
    'telefone': '11977777777'
  })

  assert resposta.status_code == 200

  dados = resposta.get_json()

  assert dados['cliente']['nome'] == 'João da Silva'
  assert dados['cliente']['telefone'] == '11977777777'

def test_excluir_cliente(client):
  cadastro = cadastrar_cliente(client)

  cliente_id = cadastro.get_json()['cliente']['id']

  resposta = client.delete(f'/clientes/{cliente_id}')

  assert resposta.status_code == 200

  consulta = client.get(f'/clientes/{cliente_id}')

  assert consulta.status_code == 404

def test_nao_excluir_cliente_com_pedido(client):
  cadastro = cadastrar_cliente(client)

  cliente_id = cadastro.get_json()['cliente']['id']

  resposta_pedido = client.post('/pedidos/', json={
    'cliente_id': cliente_id,
    'data_retirada': '2026-11-10',
    'observacoes': 'Pedido para teste',
    'itens': [
      {
        'nome_produto': 'Bolo de chocolate',
        'quantidade': 1,
        'valor_unitario': 45.00
      }
    ]
  })

  assert resposta_pedido.status_code == 201

  # tenta excluir o cliente que possui pedido
  resposta = client.delete(f'/clientes/{cliente_id}')

  assert resposta.status_code == 409