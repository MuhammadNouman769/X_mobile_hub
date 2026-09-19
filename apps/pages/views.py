from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from apps.products.models import Brand, Category, Product

from .forms import ContactForm
from .models import NewsletterSubscriber


def home_view(request):
    context = {
        'featured_products': Product.objects.featured().select_related('brand').prefetch_related('variants')[:8],
        'new_arrivals': Product.objects.active().filter(is_new_arrival=True).select_related('brand').prefetch_related('variants')[:8],
        'best_sellers': Product.objects.active().order_by('-total_sold').select_related('brand').prefetch_related('variants')[:8],
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
            return redirect('pages:contact')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})


def terms_view(request):
    return render(request, 'pages/terms_conditions.html')


def privacy_policy_view(request):
    return render(request, 'pages/privacy_policy.html')


def shipping_policy_view(request):
    return render(request, 'pages/shipping_policy.html')


def refund_policy_view(request):
    return render(request, 'pages/refund_policy.html')


def faq_view(request):
    return render(request, 'pages/faq.html')


@require_POST
def newsletter_subscribe_ajax(request):
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})
    obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
    if not created:
        return JsonResponse({'success': True, 'message': 'You are already subscribed!'})
    return JsonResponse({'success': True, 'message': 'Subscribed successfully! 🎉'})


def error_404(request, exception=None):
    return render(request, 'pages/404.html', status=404)


def error_500(request):
    return render(request, 'pages/500.html', status=500)
