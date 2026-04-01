from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/',                      views.checkout,          name='checkout'),
    path('place/',                         views.place_order,       name='place'),
    path('confirmation/<str:order_id>/',   views.order_confirmation, name='confirmation'),
    path('track/',                         views.track_order,       name='track'),
]
