from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import date

from products.models import Product, Category, ProductImage
from orders.models import Order, OrderStatusLog
from orders.whatsapp import send_whatsapp_notification


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    """Decorator — sirf admin access kar sake"""
    decorated = login_required(user_passes_test(is_admin, login_url='/')(view_func))
    return decorated


@admin_required
def dashboard_home(request):
    today = date.today()

    # Stats
    today_orders  = Order.objects.filter(created_at__date=today).count()
    month_sales   = Order.objects.filter(
        created_at__month=today.month,
        created_at__year=today.year,
        status__in=['confirmed', 'packed', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0
    pending_orders  = Order.objects.filter(status='pending').count()
    total_products  = Product.objects.filter(is_active=True).count()

    recent_orders   = Order.objects.prefetch_related('items').order_by('-created_at')[:8]
    recent_products = Product.objects.prefetch_related('images').order_by('-created_at')[:6]
    categories      = Category.objects.filter(is_active=True)

    return render(request, 'dashboard/dashboard.html', {
        'stats': {
            'today_orders':   today_orders,
            'month_sales':    f"{int(month_sales):,}",
            'pending_orders': pending_orders,
            'total_products': total_products,
        },
        'recent_orders':   recent_orders,
        'recent_products': recent_products,
        'categories':      categories,
    })


@admin_required
def all_orders(request):
    orders = Order.objects.prefetch_related('items').order_by('-created_at')

    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    total_count = Order.objects.count()
    paginator   = Paginator(orders, 20)
    page        = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)

    return render(request, 'dashboard/orders.html', {
        'orders':      orders_page,
        'total_count': total_count,
    })


@admin_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order      = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get('status')

        if new_status and new_status != order.status:
            # Log status change
            OrderStatusLog.objects.create(
                order      = order,
                old_status = order.status,
                new_status = new_status,
            )
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order_id} updated to {order.get_status_display()}')

            # Auto WhatsApp notification on shipped
            if new_status == 'shipped':
                try:
                    send_whatsapp_notification(order)
                except Exception:
                    pass

    # Redirect back
    next_url = request.META.get('HTTP_REFERER', '/dashboard/orders/')
    return redirect(next_url)


@admin_required
def all_products(request):
    products = Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/products.html', {
        'products':   products,
        'categories': categories,
    })


@admin_required
def add_product(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price       = request.POST.get('price')
        sale_price  = request.POST.get('sale_price') or None
        stock       = request.POST.get('stock', 0)
        description = request.POST.get('description', '').strip()
        is_active   = bool(request.POST.get('is_active'))
        is_featured = bool(request.POST.get('is_featured'))
        is_bestseller = bool(request.POST.get('is_bestseller'))

        if not name or not price or not category_id:
            messages.error(request, 'Name, price and category are required.')
            return redirect('dashboard:home')

        try:
            category = Category.objects.get(id=category_id)
            product  = Product.objects.create(
                name          = name,
                category      = category,
                price         = price,
                sale_price    = sale_price,
                stock         = stock,
                description   = description,
                is_active     = is_active,
                is_featured   = is_featured,
                is_bestseller = is_bestseller,
            )

            # Handle image upload
            image = request.FILES.get('image')
            if image:
                ProductImage.objects.create(
                    product = product,
                    image   = image,
                    is_main = True,
                    order   = 0,
                )

            messages.success(request, f'Product "{name}" added successfully!')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return redirect('dashboard:home')


@admin_required
def edit_product(request, product_id):
    product    = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True)

    if request.method == 'POST':
        product.name          = request.POST.get('name', product.name).strip()
        product.price         = request.POST.get('price', product.price)
        product.sale_price    = request.POST.get('sale_price') or None
        product.stock         = request.POST.get('stock', product.stock)
        product.description   = request.POST.get('description', product.description).strip()
        product.is_active     = bool(request.POST.get('is_active'))
        product.is_featured   = bool(request.POST.get('is_featured'))
        product.is_bestseller = bool(request.POST.get('is_bestseller'))

        cat_id = request.POST.get('category')
        if cat_id:
            product.category = get_object_or_404(Category, id=cat_id)

        product.save()

        # New image
        image = request.FILES.get('image')
        if image:
            ProductImage.objects.create(
                product=product, image=image, is_main=True, order=0
            )

        messages.success(request, f'Product "{product.name}" updated!')
        return redirect('dashboard:products')

    return render(request, 'dashboard/edit_product.html', {
        'product':    product,
        'categories': categories,
    })


@admin_required
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        name    = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
    return redirect('dashboard:products')


@admin_required
def whatsapp_notify(request):
    """Send WhatsApp to all pending orders"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order    = get_object_or_404(Order, order_id=order_id)
        try:
            send_whatsapp_notification(order)
            messages.success(request, f'WhatsApp sent for order #{order_id}')
        except Exception as e:
            messages.error(request, f'Failed: {e}')
    return redirect('dashboard:orders')
