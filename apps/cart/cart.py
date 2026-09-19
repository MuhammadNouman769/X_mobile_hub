from decimal import Decimal

from django.conf import settings

from apps.products.models import Product, ProductColorVariant


class Cart:
    """A session-based shopping cart. Every mutation (add/update/remove) is
    driven by AJAX from the frontend so the page never has to reload."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def _key(self, product_id, variant_id):
        return f"{product_id}:{variant_id or 0}"

    def add(self, product, variant=None, quantity=1, override_quantity=False):
        key = self._key(product.id, variant.id if variant else None)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.id,
                'variant_id': variant.id if variant else None,
                'quantity': 0,
                'price': str(product.current_price),
            }
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self.save()

    def update(self, key, quantity):
        if key in self.cart:
            if quantity <= 0:
                del self.cart[key]
            else:
                self.cart[key]['quantity'] = quantity
            self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids).select_related('brand')
        products_map = {p.id: p for p in products}

        variant_ids = [item['variant_id'] for item in self.cart.values() if item['variant_id']]
        variants_map = {v.id: v for v in ProductColorVariant.objects.filter(id__in=variant_ids)}

        for key, item in self.cart.items():
            product = products_map.get(item['product_id'])
            if not product:
                continue
            variant = variants_map.get(item['variant_id']) if item['variant_id'] else None
            data = item.copy()
            data['key'] = key
            data['product'] = product
            data['variant'] = variant
            data['price'] = Decimal(item['price'])
            data['total_price'] = data['price'] * item['quantity']
            yield data

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
