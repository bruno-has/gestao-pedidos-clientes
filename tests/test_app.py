def test_rota_inicial(client):
  resposta = client.get('/')

  assert resposta.status_code == 302
  assert resposta.headers['Location'].endswith('/login')