from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Review


def shop(request):
    products = Product.objects.filter(is_active=True)\
                              .select_related('category')\
                              .prefetch_related('images')

    # Search
    q = request.GET.get('q', '')
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    # Category filter
    cats = request.GET.getlist('cat')
    if cats:
        products = products.filter(category__slug__in=cats)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Stock / sale filters
    if request.GET.get('in_stock'):
        products = products.filter(stock__gt=0)
    if request.GET.get('on_sale'):
        products = products.filter(sale_price__isnull=False)

    # Sort
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest':     '-created_at',
        'price_low':  'price',
        'price_high': '-price',
        'rating':     '-created_at',  # TODO: annotate avg rating
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # Paginate
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True)

    return render(request, 'products/shop.html', {
        'products':      products_page,
        'categories':    categories,
        'selected_cats': cats,
    })


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True)

    # Star breakdown for sidebar
    rating_breakdown = []
    for star in range(5, 0, -1):
        count   = reviews.filter(rating=star).count()
        percent = int((count / reviews.count() * 100)) if reviews.count() else 0
        rating_breakdown.append({'star': star, 'count': count, 'percent': percent})

    return render(request, 'products/detail.html', {
        'product':          product,
        'reviews':          reviews,
        'rating_breakdown': rating_breakdown,
    })


def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating  = request.POST.get('rating', 3)
        comment = request.POST.get('comment', '').strip()
        title   = request.POST.get('title', '').strip()

        if not comment:
            messages.error(request, 'Please write a review before submitting.')
            return redirect('products:detail', slug=slug)

        Review.objects.create(
            product     = product,
            customer    = request.user if request.user.is_authenticated else None,
            guest_name  = request.POST.get('guest_name', ''),
            guest_email = request.POST.get('guest_email', ''),
            rating      = int(rating),
            title       = title,
            comment     = comment,
            is_approved = False,   # Admin must approve
        )
        messages.success(request, 'Review submitted! It will appear after approval.')

    return redirect('products:detail', slug=slug)
