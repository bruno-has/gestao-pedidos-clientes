from flask import Blueprint

from app.controllers.web_controller import (
  login_page,
  painel,
  pagina_clientes,
  novo_cliente,
  editar_cliente,
  excluir_cliente_web,
  pagina_pedidos,
  pagina_novo_pedido,
  sair
)

web_bp = Blueprint('web', __name__)

web_bp.add_url_rule(
  '/login', 
  endpoint='login', 
  view_func=login_page, 
  methods=['GET', 'POST']
)

web_bp.add_url_rule(
  '/painel', 
  endpoint='painel', 
  view_func=painel, 
  methods=['GET']
)

web_bp.add_url_rule(
  '/painel/clientes', 
  endpoint='clientes', 
  view_func=pagina_clientes, 
  methods=['GET']
)

web_bp.add_url_rule(
  '/painel/clientes/novo',
  endpoint='novo_cliente',
  view_func=novo_cliente,
  methods=['GET', 'POST']
)

web_bp.add_url_rule(
  '/painel/clientes/<int:cliente_id>/editar',
  endpoint='editar_cliente',
  view_func=editar_cliente,
  methods=['GET', 'POST']
)

web_bp.add_url_rule(
  '/painel/clientes/<int:cliente_id>/excluir',
  endpoint='excluir_cliente',
  view_func=excluir_cliente_web,
  methods=['POST']
)

web_bp.add_url_rule(
  '/painel/pedidos', 
  endpoint='pedidos', 
  view_func=pagina_pedidos, 
  methods=['GET']
)

web_bp.add_url_rule(
  '/painel/pedidos/novo', 
  endpoint='novo_pedido', 
  view_func=pagina_novo_pedido, 
  methods=['GET']
)

web_bp.add_url_rule(
  '/sair', 
  endpoint='sair', 
  view_func=sair, 
  methods=['POST']
)