"""
Custom template filters for the store app.
"""

from django import template

register = template.Library()


@register.filter
def indian_currency(value):
    """
    Format a number as Indian Rupees: ₹1,299.00
    """
    if value is None:
        return '₹0.00'
    try:
        num = float(value)
        return f'₹{num:,.2f}'
    except (ValueError, TypeError):
        return str(value)
