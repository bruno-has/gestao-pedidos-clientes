from flask import Blueprint, request, jsonify

from app.controllers.pedido_controller import (
  criar_pedido,
  obter_pedidos,
  obter_pedido_por_id,
  obter_pedidos_por_cliente,
  atualizar_pedido_completo,
  atualizar_status,
  excluir_pedido_por_id,
)

pedido_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@pedido_bp.route('/', methods=['POST'])
def cadastrar():
  dados = request.get_json(silent=True)
  resposta, status = criar_pedido(dados)
  return jsonify(resposta), status

@pedido_bp.route('/', methods=['GET'])
def listar():
  resposta, status = obter_pedidos()
  return jsonify(resposta), status

@pedido_bp.route('/cliente/<int:cliente_id>', methods=['GET'])
def listar_por_cliente(cliente_id):
  resposta, status = obter_pedidos_por_cliente(cliente_id)
  return jsonify(resposta), status

@pedido_bp.route('/<int:pedido_id>', methods=['GET'])
def buscar_por_id(pedido_id):
  resposta, status = obter_pedido_por_id(pedido_id)
  return jsonify(resposta), status

@pedido_bp.route('/<int:pedido_id>', methods=['PUT'])
def atualizar(pedido_id):
  dados = request.get_json(silent=True)
  resposta, status = atualizar_pedido_completo(pedido_id, dados)
  return jsonify(resposta), status

@pedido_bp.route('/<int:pedido_id>', methods=['PATCH'])
def atualizar_parcial(pedido_id):
  dados = request.get_json(silent=True)
  resposta, status = atualizar_status(pedido_id, dados)
  return jsonify(resposta), status

@pedido_bp.route('/<int:pedido_id>', methods=['DELETE'])
def excluir(pedido_id):
  resposta, status = excluir_pedido_por_id(pedido_id)
  return jsonify(resposta), status