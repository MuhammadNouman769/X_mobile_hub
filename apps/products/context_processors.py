from .models import Brand, Category


def categories_and_brands(request):
    return {
        'nav_categories': Category.objects.filter(is_active=True),
        'nav_brands': Brand.objects.filter(is_active=True),
    }
