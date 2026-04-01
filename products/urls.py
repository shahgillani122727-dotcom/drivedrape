from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('',                        views.shop,       name='shop'),
    path('<slug:slug>/',             views.detail,     name='detail'),
    path('<slug:slug>/review/',      views.add_review, name='add_review'),
]
