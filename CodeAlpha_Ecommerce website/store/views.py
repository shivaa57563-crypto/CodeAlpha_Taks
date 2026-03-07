"""
Views - handle HTTP requests and return responses.
Each view fetches data, processes it, and renders a template.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, CartItem, Order, OrderItem
from .forms import SignUpForm, AddToCartForm
from .utils import get_or_create_cart


def home(request):
    """
    Homepage - displays all products.
    """
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, product_id):
    """
    Product detail page - shows single product with add to cart form.
    """
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartForm()
    return render(request, 'store/product_detail.html', {'product': product, 'form': form})


def cart_view(request):
    """
    Shopping cart page - shows all items in cart with total.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    total = cart.get_total()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    })


def add_to_cart(request, product_id):
    """
    Add product to cart. Handles both GET (from form) and POST.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    if request.method == 'POST':
        form = AddToCartForm(request.POST or None)
        quantity = 1
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
        # Add to cart (use quantity from form, or default 1)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        messages.success(request, f'Added {product.name} to cart!')
    else:
        # Default: add 1
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f'Added {product.name} to cart!')

    # Redirect back to previous page or product detail
    next_url = request.GET.get('next') or request.POST.get('next') or 'store:product_detail'
    if next_url == 'store:product_detail':
        return redirect('store:product_detail', product_id=product_id)
    return redirect(next_url)


def remove_from_cart(request, cart_item_id):
    """
    Remove an item from the cart.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from cart.')
    return redirect('store:cart')


@login_required(login_url='/accounts/login/')
def checkout(request):
    """
    Place order - create Order and OrderItems from cart, then clear cart.
    Requires user to be logged in.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items:
        messages.warning(request, 'Your cart is empty. Add items before checkout.')
        return redirect('store:cart')

    # Create order
    total = sum(item.get_subtotal() for item in cart_items)
    order = Order.objects.create(user=request.user, total=total, status='pending')

    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )

    # Clear cart
    cart.items.all().delete()

    messages.success(request, f'Order #{order.id} placed successfully! Total: ${order.total}')
    return redirect('store:order_confirmation', order_id=order.id)


@login_required(login_url='/accounts/login/')
def order_confirmation(request, order_id):
    """Show order confirmation page after checkout."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


def signup_view(request):
    """
    User registration - create new account.
    """
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('store:home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignUpForm()

    return render(request, 'store/signup.html', {'form': form})
