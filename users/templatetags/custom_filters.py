from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtrai o argumento do valor"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def mul(value, arg):
    """Multiplica o valor pelo argumento"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def div(value, arg):
    """Divide o valor pelo argumento"""
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value 