import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from apps.accounts.forms import StyledAuthenticationForm as AuthenticationForm
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.orders.models import Order, OrderItem
from apps.products.models import Brand, Category, Product, ProductColorVariant, Review

from .decorators import staff_required
from .forms import BrandForm, CategoryForm, ProductForm, ProductVariantFormSet


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------
def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('dashboard:home')
            messages.error(request, "Invalid credentials or you don't have staff access.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})


@staff_required
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')


# ------------------------------------------------------------------
# HOME / ANALYTICS
# ------------------------------------------------------------------
@staff_required
def dashboard_home(request):
    today = timezone.localdate()
    last_30_days = today - timedelta(days=29)

    products = Product.objects.all()
    orders = Order.objects.exclude(status=Order.STATUS_CANCELLED)

    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    total_products = products.count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_stock_units = products.aggregate(total=Sum('stock_quantity'))['total'] or 0
    low_stock_products = products.filter(stock_quantity__gt=0, stock_quantity__lte=5).order_by('stock_quantity')
    out_of_stock_products = products.filter(stock_quantity=0)

    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.exclude(status=Order.STATUS_CANCELLED).aggregate(total=Sum('total_amount'))['total'] or 0

    # Sales trend for last 30 days (date -> revenue)
    sales_qs = (
        orders.filter(created_at__date__gte=last_30_days)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('total_amount'), order_count=Count('id'))
        .order_by('day')
    )
    sales_by_day = {row['day'].isoformat(): float(row['revenue']) for row in sales_qs}
    orders_by_day = {row['day'].isoformat(): row['order_count'] for row in sales_qs}
    trend_labels = [(last_30_days + timedelta(days=i)).isoformat() for i in range(30)]
    trend_revenue = [sales_by_day.get(d, 0) for d in trend_labels]
    trend_orders = [orders_by_day.get(d, 0) for d in trend_labels]

    # Top selling products
    top_products = products.order_by('-total_sold')[:6]

    # Category-wise revenue share
    category_revenue = (
        OrderItem.objects.exclude(order__status=Order.STATUS_CANCELLED)
        .values('product__category__name')
        .annotate(revenue=Sum(F('price') * F('quantity')))
        .order_by('-revenue')[:6]
    )
    category_labels = [c['product__category__name'] or 'Uncategorized' for c in category_revenue]
    category_values = [float(c['revenue'] or 0) for c in category_revenue]

    # Brand-wise unit sales
    brand_sales = (
        Product.objects.values('brand__name')
        .annotate(units=Sum('total_sold'))
        .order_by('-units')[:6]
    )
    brand_labels = [b['brand__name'] for b in brand_sales]
    brand_values = [b['units'] or 0 for b in brand_sales]

    # Order status distribution
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    status_labels = [dict(Order.STATUS_CHOICES).get(s['status'], s['status']) for s in status_counts]
    status_values = [s['count'] for s in status_counts]

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_stock_units': total_stock_units,
        'today_revenue': today_revenue,
        'today_orders_count': today_orders.count(),
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_products.count(),
        'out_of_stock_count': out_of_stock_products.count(),
        'top_products': top_products,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'chart_trend_labels': json.dumps(trend_labels),
        'chart_trend_revenue': json.dumps(trend_revenue),
        'chart_trend_orders': json.dumps(trend_orders),
        'chart_category_labels': json.dumps(category_labels),
        'chart_category_values': json.dumps(category_values),
        'chart_brand_labels': json.dumps(brand_labels),
        'chart_brand_values': json.dumps(brand_values),
        'chart_status_labels': json.dumps(status_labels),
        'chart_status_values': json.dumps(status_values),
    }
    return render(request, 'dashboard/home.html', context)


@staff_required
def live_stats_ajax(request):
    """Polled every few seconds from the dashboard to show 'live' KPI numbers
    (stock levels, today's sales) without a page reload."""
    today = timezone.localdate()
    products = Product.objects.all()
    total_stock_units = products.aggregate(total=Sum('stock_quantity'))['total'] or 0
    low_stock_count = products.filter(stock_quantity__gt=0, stock_quantity__lte=5).count()
    out_of_stock_count = products.filter(stock_quantity=0).count()
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.exclude(status=Order.STATUS_CANCELLED).aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()

    return JsonResponse({
        'total_stock_units': total_stock_units,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'today_orders_count': today_orders.count(),
        'today_revenue': float(today_revenue),
        'total_orders': total_orders,
        'server_time': timezone.localtime().strftime('%H:%M:%S'),
    })


# ------------------------------------------------------------------
# PRODUCTS CRUD
# ------------------------------------------------------------------
@staff_required
def product_list(request):
    products = Product.objects.select_related('brand', 'category').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q)
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=5)
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)

    from django.core.paginator import Paginator
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'dashboard/product_list.html', {'page_obj': page_obj, 'search_query': q})


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            formset = ProductVariantFormSet(request.POST, request.FILES, instance=product, prefix='variants')
            if formset.is_valid():
                formset.save()
                messages.success(request, f"Product '{product.name}' created successfully.")
                return redirect('dashboard:product_list')
        else:
            formset = ProductVariantFormSet(request.POST, request.FILES, prefix='variants')
    else:
        form = ProductForm()
        formset = ProductVariantFormSet(prefix='variants')
    return render(request, 'dashboard/product_form.html', {'form': form, 'formset': formset, 'is_edit': False})


@staff_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductVariantFormSet(request.POST, request.FILES, instance=product, prefix='variants')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
        formset = ProductVariantFormSet(instance=product, prefix='variants')
    return render(request, 'dashboard/product_form.html', {'form': form, 'formset': formset, 'is_edit': True, 'product': product})


@staff_required
@require_POST
def product_delete_ajax(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    return JsonResponse({'success': True, 'message': f"'{name}' deleted."})


# ------------------------------------------------------------------
# ORDERS
# ------------------------------------------------------------------
@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'dashboard/order_list.html', {
        'page_obj': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
    })


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'status_choices': Order.STATUS_CHOICES})


@staff_required
@require_POST
def order_status_update_ajax(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save(update_fields=['status'])
        return JsonResponse({
            'success': True,
            'status': order.status,
            'status_display': order.get_status_display(),
            'badge_class': order.get_status_badge_class(),
        })
    return JsonResponse({'success': False, 'message': 'Invalid status.'}, status=400)


# ------------------------------------------------------------------
# CATEGORIES
# ------------------------------------------------------------------
@staff_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_list.html', {'categories': categories, 'form': form})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'category': category})


@staff_required
@require_POST
def category_delete_ajax(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return JsonResponse({'success': True})


# ------------------------------------------------------------------
# BRANDS
# ------------------------------------------------------------------
@staff_required
def brand_list(request):
    brands = Brand.objects.annotate(product_count=Count('products')).order_by('name')
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand added successfully.")
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm()
    return render(request, 'dashboard/brand_list.html', {'brands': brands, 'form': form})


@staff_required
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated.")
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'dashboard/brand_form.html', {'form': form, 'brand': brand})


@staff_required
@require_POST
def brand_delete_ajax(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    return JsonResponse({'success': True})


# ------------------------------------------------------------------
# CUSTOMERS
# ------------------------------------------------------------------
@staff_required
def customer_list(request):
    customers = User.objects.filter(is_staff=False).annotate(order_count=Count('orders')).order_by('-date_joined')
    return render(request, 'dashboard/customer_list.html', {'customers': customers})
