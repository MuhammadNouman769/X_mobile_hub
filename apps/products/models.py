from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_list') + f'?brand={self.slug}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=60, blank=True, help_text="Bootstrap icon class e.g. bi-phone")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_list') + f'?category={self.slug}'


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def in_stock(self):
        return self.filter(stock_quantity__gt=0)

    def featured(self):
        return self.filter(is_featured=True, is_active=True)


class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    model_number = models.CharField(max_length=60, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    ram = models.CharField(max_length=20, blank=True, help_text="e.g. 8GB")
    storage = models.CharField(max_length=20, blank=True, help_text="e.g. 128GB")
    display_size = models.CharField(max_length=30, blank=True, help_text="e.g. 6.5 inch")
    battery = models.CharField(max_length=30, blank=True, help_text="e.g. 5000mAh")
    camera = models.CharField(max_length=60, blank=True, help_text="e.g. 50MP + 12MP")
    processor = models.CharField(max_length=80, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=40, unique=True, blank=True)

    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    total_sold = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand.name}-{self.name}-{self.model_number}")
            self.slug = base_slug
            suffix = 2
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{suffix}"
                suffix += 1
        if not self.sku:
            self.sku = f"XMH-{self.brand.name[:3].upper()}-{timezone.now().strftime('%y%m%d%H%M%S%f')[-8:]}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return round((self.price - self.discount_price) / self.price * 100)
        return 0

    @property
    def is_low_stock(self):
        from django.conf import settings as dj_settings
        return 0 < self.stock_quantity <= dj_settings.LOW_STOCK_THRESHOLD

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(agg, 1) if agg else 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def default_variant(self):
        return self.variants.filter(is_default=True).first() or self.variants.first()


class ProductColorVariant(models.Model):
    """A color option for a product. Clicking a color swatch swaps the
    main product image (and the hover/secondary image) client-side."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color_name = models.CharField(max_length=40)
    color_hex = models.CharField(max_length=7, help_text="e.g. #1d1d1f")
    image = models.ImageField(upload_to='products/')
    hover_image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default', 'color_name']
        unique_together = ('product', 'color_name')

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"

    @property
    def hover_image_url(self):
        if self.hover_image:
            return self.hover_image.url
        return self.image.url


class ProductGalleryImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    variant = models.ForeignKey(ProductColorVariant, on_delete=models.CASCADE, related_name='gallery', null=True, blank=True)
    image = models.ImageField(upload_to='products/gallery/')
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.user}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
