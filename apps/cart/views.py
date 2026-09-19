from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.products.models import Product, ProductColorVariant

from .cart import Cart


def _cart_payload(request, cart):
    mini_html = render_to_string('cart/_mini_cart.html', {'cart': cart}, request=request)
    return {
        'success': True,
        'cart_count': len(cart),
        'cart_total': str(cart.get_total_price()),
        'cart_total_display': f"{settings.CURRENCY_SYMBOL} {cart.get_total_price():,.0f}",
        'mini_cart_html': mini_html,
    }


@require_POST
def add_to_cart_ajax(request):
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductColorVariant, id=variant_id, product=product)

    cart = Cart(request)
    cart.add(product=product, variant=variant, quantity=quantity)

    payload = _cart_payload(request, cart)
    payload['message'] = f"{product.name} added to cart."
    return JsonResponse(payload)


@require_POST
def update_cart_ajax(request):
    key = request.POST.get('key')
    quantity = int(request.POST.get('quantity', 1))

    cart = Cart(request)
    cart.update(key, quantity)

    payload = _cart_payload(request, cart)
    cart_html = render_to_string('cart/_cart_table.html', {'cart': cart}, request=request)
    payload['cart_table_html'] = cart_html
    return JsonResponse(payload)


@require_POST
def remove_from_cart_ajax(request):
    key = request.POST.get('key')
    cart = Cart(request)
    cart.remove(key)

    payload = _cart_payload(request, cart)
    cart_html = render_to_string('cart/_cart_table.html', {'cart': cart}, request=request)
    payload['cart_table_html'] = cart_html
    return JsonResponse(payload)


def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
