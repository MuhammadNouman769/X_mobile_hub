from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('live-stats/', views.live_stats_ajax, name='live_stats_ajax'),

    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete_ajax, name='product_delete_ajax'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.order_status_update_ajax, name='order_status_update_ajax'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete_ajax, name='category_delete_ajax'),

    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<int:pk>/edit/', views.brand_update, name='brand_update'),
    path('brands/<int:pk>/delete/', views.brand_delete_ajax, name='brand_delete_ajax'),

    path('customers/', views.customer_list, name='customer_list'),
]
