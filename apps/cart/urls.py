from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('update/', views.update_cart_ajax, name='update_cart_ajax'),
    path('remove/', views.remove_from_cart_ajax, name='remove_from_cart_ajax'),
]
