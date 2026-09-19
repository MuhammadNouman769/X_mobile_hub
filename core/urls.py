from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('secret-admin/', admin.site.urls),  # Django admin kept hidden/unused; custom dashboard is primary
    path('', include('apps.pages.urls')),
    path('shop/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('account/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

handler404 = 'apps.pages.views.error_404'
handler500 = 'apps.pages.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
