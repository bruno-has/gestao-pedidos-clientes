import pytest

from app import create_app
from app.extensions import db
from app.services.auth_service import criar_usuario

@pytest.fixture
def app():
  app = create_app({
    'TESTING': True,
    'SECRET_KEY': 'chave-de-teste',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'WTF_CSRF_ENABLED': False
  })

  with app.app_context():
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()

@pytest.fixture
def client(app):
  return app.test_client()

@pytest.fixture
def autenticar_cliente(client, app):
  with app.app_context():
    criar_usuario(
      nome = 'Usuário de teste',
      email = 'teste@teste.com',
      senha = 'senha12345'
    )

  resposta = client.post('/auth/login', json={
    'email': 'teste@teste.com',
    'senha': 'senha12345'
  })

  assert resposta.status_code == 200

  return client