from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_currency(value):
    try:
        return f"R$ {Decimal(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    except:
        return "R$ 0,00" 