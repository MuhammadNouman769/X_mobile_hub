from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .models import Brand, Category, Product, Review, Wishlist


def _apply_filters(qs, params):
    brand = params.get('brand')
    category = params.get('category')
    search = params.get('q', '').strip()
    min_price = params.get('min_price')
    max_price = params.get('max_price')
    sort = params.get('sort', 'latest')

    if brand:
        qs = qs.filter(brand__slug=brand)
    if category:
        qs = qs.filter(category__slug=category)
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(short_description__icontains=search)
        )
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    if sort == 'price_low':
        qs = qs.order_by('price')
    elif sort == 'price_high':
        qs = qs.order_by('-price')
    elif sort == 'best_selling':
        qs = qs.order_by('-total_sold')
    elif sort == 'top_rated':
        qs = qs.order_by('-id')  # rating computed in python; keep stable fallback
    else:
        qs = qs.order_by('-created_at')
    return qs


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.active().select_related('brand', 'category').prefetch_related('variants')
        return _apply_filters(qs, self.request.GET)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brands'] = Brand.objects.filter(is_active=True)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['current_brand'] = self.request.GET.get('brand', '')
        ctx['current_category'] = self.request.GET.get('category', '')
        ctx['current_sort'] = self.request.GET.get('sort', 'latest')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


def product_filter_ajax(request):
    """Returns just the product-grid partial so the shop page can filter
    and sort without a full page reload."""
    qs = Product.objects.active().select_related('brand', 'category').prefetch_related('variants')
    qs = _apply_filters(qs, request.GET)

    page_number = request.GET.get('page', 1)
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(page_number)

    html = render_to_string('products/_product_grid.html', {'products': page_obj}, request=request)
    pagination_html = render_to_string('products/_pagination.html', {'page_obj': page_obj}, request=request)
    return JsonResponse({
        'html': html,
        'pagination_html': pagination_html,
        'count': paginator.count,
    })


def search_suggest_ajax(request):
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        products = Product.objects.active().filter(
            Q(name__icontains=q) | Q(brand__name__icontains=q)
        ).select_related('brand')[:6]
        for p in products:
            variant = p.default_variant
            results.append({
                'name': p.name,
                'brand': p.brand.name,
                'url': p.get_absolute_url(),
                'price': str(p.current_price),
                'image': variant.image.url if variant else '',
            })
    return JsonResponse({'results': results})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'

    def get_queryset(self):
        return Product.objects.active().select_related('brand', 'category').prefetch_related('variants', 'reviews__user')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        ctx['variants'] = product.variants.all()
        ctx['related_products'] = Product.objects.active().filter(
            category=product.category
        ).exclude(id=product.id).select_related('brand')[:4]
        ctx['reviews'] = product.reviews.select_related('user').all()
        if self.request.user.is_authenticated:
            ctx['in_wishlist'] = Wishlist.objects.filter(user=self.request.user, product=product).exists()
            ctx['user_has_reviewed'] = Review.objects.filter(user=self.request.user, product=product).exists()
        else:
            ctx['in_wishlist'] = False
            ctx['user_has_reviewed'] = False
        return ctx


class BrandDetailView(ListView):
    model = Product
    template_name = 'products/brand_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.brand = get_object_or_404(Brand, slug=self.kwargs['slug'])
        return Product.objects.active().filter(brand=self.brand).select_related('category').prefetch_related('variants')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brand'] = self.brand
        return ctx


@login_required
@require_POST
def add_review_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '')
    comment = request.POST.get('comment', '')

    review, created = Review.objects.update_or_create(
        product=product, user=request.user,
        defaults={'rating': rating, 'title': title, 'comment': comment}
    )
    return JsonResponse({
        'success': True,
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'html': render_to_string('products/_review_item.html', {'review': review}, request=request),
    })


@login_required
@require_POST
def toggle_wishlist_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        return JsonResponse({'success': True, 'in_wishlist': False})
    return JsonResponse({'success': True, 'in_wishlist': True})
