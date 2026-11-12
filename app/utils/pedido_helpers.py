from decimal import Decimal

from app.extensions import db
from app.models.produto import Produto
from app.utils.validacoes import (
  converter_id_positivo,
  converter_data_retirada,
  converter_quantidade,
  converter_valor_unitario
)

def calcular_total_pedido(pedido):
  return sum(
    (
      item.quantidade * item.valor_unitario
      for item in pedido.itens
    ), Decimal('0.00')
  )

def adicionar_total_pedidos(pedidos):
  return [
    {
      'pedido': pedido,
      'total': calcular_total_pedido(pedido)
    } for pedido in pedidos
  ]

def validar_itens_formulario(
  nomes, 
  quantidades, 
  valores, 
  ignorar_linhas_vazias=False
):
  if not (len(nomes) == len(quantidades) == len(valores)):
    return None, 'Os dados dos itens estão incosistentes'

  itens =[]

  for nome, quantidade_texto, valor_texto in zip(
    nomes, quantidades, valores
  ):
    nome = nome.strip()
    quantidade_texto = quantidade_texto.strip()
    valor_texto = valor_texto.strip()

    if not nome and not quantidade_texto and not valor_texto:
      if ignorar_linhas_vazias:
        continue

      return None, 'Preencha todos os campos de cada item'  

    if not nome or not quantidade_texto or not valor_texto:
      return None, 'Preencha todos os campos de cada item'

    if len(nome) > 100:
      return None, 'O nome deve ter até 100 caracteres'

    quantidade = converter_quantidade(quantidade_texto)
    if quantidade is None:
      return None, 'Confira os produtos: a quantidade deve ser um inteiro positivo'

    valor = converter_valor_unitario(valor_texto)
    if valor is None:
      return None, 'Informe um valor positivo com até duas casas decimais'

    itens.append({
      'nome_produto': nome,
      'quantidade': quantidade,
      'valor_unitario': valor
    })

  if not itens:
    return None, 'Adicione pelo menos um item ao pedido'

  return itens, None

def validar_produtos_formulario(produto_ids, quantidades, ignorar_linhas_vazias=False):
  if len(produto_ids) != len(quantidades):
    return None, 'Os dados dos itens estão inconsistentes'

  itens = []

  for produto_id_texto, quantidade_texto in zip(
    produto_ids, quantidades
  ):
    produto_id_texto = produto_id_texto.strip()
    quantidade_texto = quantidade_texto.strip()

    if not produto_id_texto and not quantidade_texto:
      if ignorar_linhas_vazias:
        continue

      return None, 'Preencha todos os campos de cada item'

    if not produto_id_texto or not quantidade_texto:
      return None, 'Selecione o produto e informe sua quantidade'

    try:
      produto_id = int(produto_id_texto)
      if produto_id <= 0:
        raise ValueError

    except (ValueError, TypeError):
      return None, 'Selecione um produto válido'

    produto = db.session.get(Produto, produto_id)
    if produto is None:
      return None, 'Um dos produtos selecionados não existe'

    quantidade = converter_quantidade(quantidade_texto)
    if quantidade is None:
      return None, 'A quantidade deve ser um inteiro positivo'

    itens.append({
      'produto_id': produto_id,
      'nome_produto': produto.nome,
      'quantidade': quantidade,
      'valor_unitario': produto.valor_unitario
    })

  if not itens:
    return None, 'Adicione pelo menos um produto ao pedido'

  return itens, None
    