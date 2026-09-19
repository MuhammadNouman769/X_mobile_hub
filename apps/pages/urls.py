from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about-us/', views.about_view, name='about'),
    path('contact-us/', views.contact_view, name='contact'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('shipping-policy/', views.shipping_policy_view, name='shipping_policy'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
    path('faq/', views.faq_view, name='faq'),
    path('newsletter/subscribe/', views.newsletter_subscribe_ajax, name='newsletter_subscribe_ajax'),
]
