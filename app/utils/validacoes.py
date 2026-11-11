from datetime import datetime
from decimal import Decimal, InvalidOperation


def converter_id_positivo(valor):
  try:
    resultado = int(valor)
    if resultado <= 0:
      return None
    return resultado
  
  except (ValueError, TypeError):
    return None


def converter_data_retirada(valor):
  try:
    return datetime.strptime(valor, '%Y-%m-%dT%H:%M')
  
  except (ValueError, TypeError):
    return None


def converter_quantidade(valor):
  try:
    resultado = int(valor)
    if resultado <= 0:
      return None
    return resultado
  
  except (ValueError, TypeError):
    return None


def converter_valor_unitario(valor):
  try:
    resultado = Decimal(valor)

    if (
      not resultado.is_finite()
      or resultado <= 0
      or resultado >= Decimal('100000000')
      or resultado.as_tuple().exponent < -2
    ):
      return None

    return resultado

  except (InvalidOperation, ValueError, TypeError):
    return None