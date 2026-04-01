from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                              views.dashboard_home,       name='home'),
    path('orders/',                       views.all_orders,           name='orders'),
    path('orders/<str:order_id>/status/', views.update_order_status,  name='update_status'),
    path('products/',                     views.all_products,         name='products'),
    path('products/add/',                 views.add_product,          name='add_product'),
    path('products/<int:product_id>/edit/',   views.edit_product,     name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product,   name='delete_product'),
    path('whatsapp/',                     views.whatsapp_notify,      name='whatsapp'),
]
