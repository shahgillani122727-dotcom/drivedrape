from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer
from orders.models import Order


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        email    = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            return redirect(request.GET.get('next', 'core:home'))
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        email     = request.POST.get('email', '').lower().strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first     = request.POST.get('first_name', '').strip()
        last      = request.POST.get('last_name', '').strip()
        phone     = request.POST.get('phone', '').strip()

        # Validations
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered. Please login.')
            return render(request, 'accounts/register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/register.html')

        # Create user
        user = Customer.objects.create_user(
            email      = email,
            password   = password1,
            first_name = first,
            last_name  = last,
            phone      = phone,
        )
        login(request, user)
        messages.success(request, f'Account created! Welcome to Drive Drape, {first or email}!')
        return redirect('core:home')

    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def my_orders(request):
    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related('items').order_by('-created_at')

    return render(request, 'accounts/orders.html', {'orders': orders})
