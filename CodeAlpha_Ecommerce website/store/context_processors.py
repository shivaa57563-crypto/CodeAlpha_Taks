"""
Context processors - make data available in ALL templates.
Used to show cart item count in the navbar on every page.
"""


def cart_context(request):
    """
    Add cart count to template context.
    Shows number of items in cart in the navbar.
    """
    from store.utils import get_or_create_cart
    cart = get_or_create_cart(request)
    return {
        'cart_item_count': cart.get_item_count(),
    }
