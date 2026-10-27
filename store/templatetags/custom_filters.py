from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Format a number as Vietnamese Dong currency:
    e.g. 604000 -> 604.000 đ
    """
    if value is None or value == '':
        return '0 đ'
    try:
        val = int(round(float(value)))
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return f"{value} đ"

@register.filter(name='format_price')
def format_price(value):
    """
    Format a number with dot thousand separators:
    e.g. 604000 -> 604.000
    """
    if value is None or value == '':
        return '0'
    try:
        val = int(round(float(value)))
        return f"{val:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='multiply_price')
def multiply_price(price, quantity):
    """
    Multiply price * quantity and format as currency:
    e.g. (604000, 2) -> 1.208.000 đ
    """
    try:
        total = float(price) * int(quantity)
        val = int(round(total))
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return '0 đ'
