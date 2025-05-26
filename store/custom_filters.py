# store/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica o valor pelo argumento"""
    return float(value) * float(arg)