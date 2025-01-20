from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica o valor por arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide o valor por arg"""
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def sub(value, arg):
    """Subtrai arg do valor"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, arg):
    """Divide uma string pelo separador"""
    return value.split(arg) 