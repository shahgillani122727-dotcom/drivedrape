from django.shortcuts import render
from django.contrib import messages
from products.models import Product, Category


def home(request):
    featured_products = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('images')[:8]
    categories = Category.objects.filter(is_active=True)
    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'categories':        categories,
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        messages.success(request, f"Thanks {name}! We'll get back to you soon.")
    return render(request, 'core/contact.html')


def faq(request):
    faq_items = [
        ("How long does delivery take?",         "We deliver within 48-72 hours across Pakistan."),
        ("Is Cash on Delivery available?",        "Yes! COD is available all over Pakistan."),
        ("Can I return a product?",               "Yes, we have a 7-day easy return policy."),
        ("How do I track my order?",              "Use your Order ID on our Track Order page."),
        ("Do you ship all over Pakistan?",        "Yes, we ship nationwide including all major cities."),
        ("Are the car mats universal fit?",       "Most are universal fit. Some are custom-cut for specific cars."),
        ("What payment methods are accepted?",    "Cash on Delivery, JazzCash, and EasyPaisa."),
    ]
    return render(request, 'core/faq.html', {'faq_items': faq_items})


def returns(request):
    return render(request, 'core/returns.html')
