from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    """Divide o valor pelo argumento"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None 