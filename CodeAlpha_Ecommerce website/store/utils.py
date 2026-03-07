"""
Utility functions for cart management.
Handles both logged-in users and anonymous (session-based) carts.
"""

from store.models import Cart


def get_or_create_cart(request):
    """
    Get existing cart or create a new one.
    - Logged-in users: cart is linked to their account
    - Anonymous users: cart is linked via session_key
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        # Create session if it doesn't exist (required for session_key)
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    return cart
