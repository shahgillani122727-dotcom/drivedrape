from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .cart import Cart
from products.models import Product


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {
        'cart_items':   list(cart),
        'cart_subtotal': cart.subtotal,
        'cart_total':    cart.total,
    })


def cart_add(request, product_id):
    cart    = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product, quantity=quantity)
        messages.success(request, f'"{product.name}" added to cart!')

    # AJAX support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart), 'message': 'Added!'})

    # Redirect back to referring page or cart
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/cart/'
    return redirect(next_url)


def cart_update(request, product_id):
    cart    = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            cart.remove(product)
        else:
            cart.add(product, quantity=quantity, override_qty=True)

    return redirect('cart:detail')


def cart_remove(request, product_id):
    cart    = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        cart.remove(product)
        messages.success(request, f'"{product.name}" removed from cart.')

    return redirect('cart:detail')


def cart_clear(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart.clear()
        messages.success(request, 'Cart cleared.')
    return redirect('cart:detail')
