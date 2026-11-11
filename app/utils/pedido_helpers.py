from decimal import Decimal

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