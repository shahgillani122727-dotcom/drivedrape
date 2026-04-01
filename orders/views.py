from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.cart import Cart
from .models import Order, OrderItem, PAKISTAN_CITIES
from .whatsapp import send_whatsapp_notification, send_customer_whatsapp


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:detail')

    # Handle buy_now shortcut (single product)
    buy_now_id = request.GET.get('buy_now')
    if buy_now_id:
        from products.models import Product
        try:
            product = Product.objects.get(id=buy_now_id, is_active=True)
            cart.clear()
            cart.add(product, quantity=1)
        except Product.DoesNotExist:
            pass

    return render(request, 'orders/checkout.html', {
        'cart_items':    list(cart),
        'cart_subtotal': cart.subtotal,
        'cart_total':    cart.total,
        'city_choices':  PAKISTAN_CITIES,
    })


def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:detail')

    # ── Build order ──────────────────────────
    order = Order(
        customer       = request.user if request.user.is_authenticated else None,
        full_name      = request.POST.get('full_name', '').strip(),
        phone          = request.POST.get('phone', '').strip(),
        email          = request.POST.get('email', '').strip(),
        address        = request.POST.get('address', '').strip(),
        city           = request.POST.get('city', ''),
        province       = request.POST.get('province', '').strip(),
        notes          = request.POST.get('notes', '').strip(),
        payment_method = request.POST.get('payment_method', 'cod'),
        subtotal       = cart.subtotal,
        shipping_cost  = 200,
    )

    # Validate required fields
    if not order.full_name or not order.phone or not order.address or not order.city:
        messages.error(request, 'Please fill in all required fields.')
        return redirect('orders:checkout')

    order.save()

    # ── Save order items ─────────────────────
    for item in cart:
        OrderItem.objects.create(
            order         = order,
            product       = item['product'],
            product_name  = item['name'],
            product_price = item['price'],
            quantity      = item['quantity'],
        )

        # Reduce stock
        product = item['product']
        product.stock = max(0, product.stock - item['quantity'])
        product.save(update_fields=['stock'])

    # ── Clear cart ───────────────────────────
    cart.clear()

    # ── WhatsApp notification ────────────────
    try:
        send_whatsapp_notification(order)
    except Exception as e:
        print(f"WhatsApp notification failed: {e}")

    # ── Redirect to confirmation ─────────────
    return redirect('orders:confirmation', order_id=order.order_id)


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    whatsapp_link = send_customer_whatsapp(order)
    return render(request, 'orders/confirmation.html', {
        'order':          order,
        'whatsapp_link':  whatsapp_link,
    })


def track_order(request):
    order         = None
    whatsapp_link = None

    order_id = request.GET.get('order_id', '').strip().upper()
    if order_id:
        try:
            order         = Order.objects.prefetch_related('items').get(order_id=order_id)
            whatsapp_link = send_customer_whatsapp(order)
        except Order.DoesNotExist:
            order = None

    return render(request, 'orders/track.html', {
        'order':          order,
        'whatsapp_link':  whatsapp_link,
    })
