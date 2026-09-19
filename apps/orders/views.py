from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.cart import Cart
from django.conf import settings

from .forms import CheckoutForm
from .models import Order, OrderItem


def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('products:product_list')

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': getattr(request.user.profile, 'phone', ''),
            'address': getattr(request.user.profile, 'address', ''),
            'city': getattr(request.user.profile, 'city', ''),
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user if request.user.is_authenticated else None
                order.subtotal = cart.get_total_price()
                order.shipping_fee = 0 if order.subtotal >= settings.FREE_SHIPPING_THRESHOLD else settings.SHIPPING_FEE
                order.total_amount = order.subtotal + order.shipping_fee
                order.save()

                for item in cart:
                    product = item['product']
                    variant = item['variant']
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        product_name=product.name,
                        color_name=variant.color_name if variant else '',
                        price=item['price'],
                        quantity=item['quantity'],
                    )
                    product.total_sold += item['quantity']
                    product.stock_quantity = max(product.stock_quantity - item['quantity'], 0)
                    product.save(update_fields=['total_sold', 'stock_quantity'])
                    if variant:
                        variant.stock_quantity = max(variant.stock_quantity - item['quantity'], 0)
                        variant.save(update_fields=['stock_quantity'])

                cart.clear()
            messages.success(request, f"Order {order.order_number} placed successfully!")
            return redirect('orders:order_success', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
