from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('filter/', views.product_filter_ajax, name='product_filter_ajax'),
    path('search-suggest/', views.search_suggest_ajax, name='search_suggest_ajax'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('review/<int:product_id>/add/', views.add_review_ajax, name='add_review_ajax'),
    path('wishlist/<int:product_id>/toggle/', views.toggle_wishlist_ajax, name='toggle_wishlist_ajax'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
