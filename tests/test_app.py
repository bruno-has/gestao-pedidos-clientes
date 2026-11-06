def test_rota_inicial(client):
  resposta = client.get('/')

  assert resposta.status_code == 200

  assert 'Sistema de Gestão de Pedidos e Clientes' in resposta.get_data(as_text=True)