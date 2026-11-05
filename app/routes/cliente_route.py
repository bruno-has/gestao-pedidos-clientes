from flask import Blueprint, request, jsonify

from app.controllers.cliente_controller import (
  criar_cliente, 
  obter_clientes,
  obter_cliente_por_id,
  atualizar_cliente_completo,
  atualizar_cliente_parcialmente,
  excluir_cliente_por_id,
)

cliente_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@cliente_bp.route('/', methods=['POST'])
def cadastrar():
  dados = request.get_json(silent=True) or {}
  resposta, status = criar_cliente(dados)
  return jsonify(resposta), status

@cliente_bp.route('/', methods=['GET'])
def listar():
  resposta, status = obter_clientes()
  return jsonify(resposta), status

@cliente_bp.route('/<int:cliente_id>', methods=['GET'])
def buscar_por_id(cliente_id):
  resposta, status = obter_cliente_por_id(cliente_id)
  return jsonify(resposta), status

@cliente_bp.route('/<int:cliente_id>', methods=['PUT'])
def atualizar(cliente_id):
  dados = request.get_json(silent=True)
  resposta, status = atualizar_cliente_completo(cliente_id, dados)
  return jsonify(resposta), status

@cliente_bp.route('/<int:cliente_id>', methods=['PATCH'])
def atualizar_parcial(cliente_id):
  dados = request.get_json(silent=True)
  resposta, status = atualizar_cliente_parcialmente(cliente_id, dados)
  return jsonify(resposta), status

@cliente_bp.route('/<int:cliente_id>', methods=['DELETE'])
def excluir(cliente_id):
  resposta, status = excluir_cliente_por_id(cliente_id)
  return jsonify(resposta), status