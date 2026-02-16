from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()



@register.filter
def tax_payable(subtotal, tax_percentage):
    return subtotal * tax_percentage / 100

