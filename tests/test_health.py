def test_health_endpoint_sem_autenticacao(client):
  resposta = client.get('/health')

  assert resposta.status_code == 200

  dados = resposta.get_json()

  assert dados['status'] == 'ok'
  assert dados['database'] == 'connected'