from django import template
register = template.Library()

@register.filter
def cart_count(cart):
    if cart:
        return len(cart)
    return 0