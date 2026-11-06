def test_acessar_clientes_sem_autenticacao(client):
  resposta = client.get('/clientes/')

  assert resposta.status_code == 401
  assert resposta.get_json()['erro'] == ('Autenticação necessária para acessar esse recurso')


def test_acessar_pedidos_sem_autenticacao(client):
  resposta = client.get('/pedidos/')

  assert resposta.status_code == 401
  assert resposta.get_json()['erro'] == ('Autenticação necessária para acessar esse recurso')
