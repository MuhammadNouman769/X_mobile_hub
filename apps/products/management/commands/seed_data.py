import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderItem
from apps.products.models import Brand, Category, Product, ProductColorVariant, Review

from ._svg_gen import generate_back_svg, generate_brand_logo_svg, generate_front_svg

random.seed(42)

BRANDS = {
    'Apple':   {'color': '#555555', 'models': [
        ('iPhone 15 Pro Max', 259900, ['8GB'], ['256GB', '512GB'], '6.7 inch', 'A17 Pro', '4422mAh', '48MP + 12MP + 12MP'),
        ('iPhone 15 Pro', 219900, ['8GB'], ['128GB', '256GB'], '6.1 inch', 'A17 Pro', '3274mAh', '48MP + 12MP + 12MP'),
        ('iPhone 15', 179900, ['6GB'], ['128GB', '256GB'], '6.1 inch', 'A16 Bionic', '3349mAh', '48MP + 12MP'),
        ('iPhone 14', 159900, ['6GB'], ['128GB'], '6.1 inch', 'A15 Bionic', '3279mAh', '12MP + 12MP'),
        ('iPhone 13', 139900, ['4GB'], ['128GB'], '6.1 inch', 'A15 Bionic', '3240mAh', '12MP + 12MP'),
        ('iPhone SE (2022)', 99900, ['4GB'], ['64GB', '128GB'], '4.7 inch', 'A15 Bionic', '2018mAh', '12MP'),
    ]},
    'Samsung': {'color': '#1428A0', 'models': [
        ('Galaxy S24 Ultra', 289900, ['12GB'], ['256GB', '512GB'], '6.8 inch', 'Snapdragon 8 Gen 3', '5000mAh', '200MP + 12MP + 50MP + 10MP'),
        ('Galaxy S24+', 229900, ['12GB'], ['256GB'], '6.7 inch', 'Snapdragon 8 Gen 3', '4900mAh', '50MP + 12MP + 10MP'),
        ('Galaxy S23', 189900, ['8GB'], ['128GB', '256GB'], '6.1 inch', 'Snapdragon 8 Gen 2', '3900mAh', '50MP + 12MP + 10MP'),
        ('Galaxy A55', 89900, ['8GB'], ['128GB', '256GB'], '6.6 inch', 'Exynos 1480', '5000mAh', '50MP + 12MP + 5MP'),
        ('Galaxy A35', 69900, ['8GB'], ['128GB'], '6.6 inch', 'Exynos 1380', '5000mAh', '50MP + 8MP + 5MP'),
        ('Galaxy A15', 44900, ['4GB'], ['128GB'], '6.5 inch', 'MediaTek Helio G99', '5000mAh', '50MP + 5MP + 2MP'),
        ('Galaxy M14', 34900, ['4GB'], ['64GB', '128GB'], '6.6 inch', 'Exynos 1330', '6000mAh', '50MP + 2MP + 2MP'),
    ]},
    'Xiaomi': {'color': '#FF6900', 'models': [
        ('Xiaomi 14 Pro', 199900, ['12GB'], ['256GB'], '6.73 inch', 'Snapdragon 8 Gen 3', '4880mAh', '50MP + 50MP + 50MP'),
        ('Redmi Note 13 Pro+', 89900, ['8GB'], ['256GB'], '6.67 inch', 'Dimensity 7200 Ultra', '5000mAh', '200MP + 8MP + 2MP'),
        ('Redmi Note 13 Pro', 74900, ['8GB'], ['128GB', '256GB'], '6.67 inch', 'Snapdragon 7s Gen 2', '5100mAh', '200MP + 8MP + 2MP'),
        ('Redmi Note 13', 54900, ['6GB'], ['128GB'], '6.67 inch', 'Snapdragon 685', '5000mAh', '108MP + 8MP + 2MP'),
        ('Redmi 13C', 34900, ['4GB'], ['128GB'], '6.74 inch', 'MediaTek Helio G85', '5000mAh', '50MP + 2MP'),
        ('POCO X6 Pro', 79900, ['8GB'], ['256GB'], '6.67 inch', 'Dimensity 8300 Ultra', '5000mAh', '64MP + 8MP + 2MP'),
    ]},
    'Oppo': {'color': '#1BA784', 'models': [
        ('Oppo Find X7', 179900, ['12GB'], ['256GB'], '6.78 inch', 'Dimensity 9300', '5000mAh', '50MP + 50MP + 50MP'),
        ('Oppo Reno 11', 99900, ['8GB'], ['256GB'], '6.7 inch', 'Dimensity 7050', '4800mAh', '50MP + 32MP + 8MP'),
        ('Oppo Reno 10', 89900, ['8GB'], ['256GB'], '6.7 inch', 'Snapdragon 778G', '5000mAh', '64MP + 32MP + 8MP'),
        ('Oppo A98', 64900, ['8GB'], ['256GB'], '6.72 inch', 'Snapdragon 695', '5000mAh', '64MP + 2MP'),
        ('Oppo A78', 49900, ['8GB'], ['128GB'], '6.56 inch', 'Snapdragon 680', '5000mAh', '50MP + 2MP'),
    ]},
    'Vivo': {'color': '#4B7BEC', 'models': [
        ('Vivo X100 Pro', 199900, ['12GB'], ['256GB'], '6.78 inch', 'Dimensity 9300', '5400mAh', '50MP + 50MP + 50MP'),
        ('Vivo V30', 99900, ['8GB'], ['256GB'], '6.78 inch', 'Snapdragon 7 Gen 3', '5000mAh', '50MP + 50MP'),
        ('Vivo V29', 89900, ['8GB'], ['256GB'], '6.78 inch', 'Snapdragon 778G', '4600mAh', '50MP + 8MP'),
        ('Vivo Y200', 54900, ['8GB'], ['128GB'], '6.67 inch', 'Snapdragon 4 Gen 2', '5000mAh', '64MP + 2MP'),
        ('Vivo Y17s', 34900, ['4GB'], ['128GB'], '6.56 inch', 'MediaTek Helio G85', '5000mAh', '13MP'),
    ]},
    'Realme': {'color': '#FFC800', 'models': [
        ('Realme GT 5 Pro', 149900, ['12GB'], ['256GB'], '6.78 inch', 'Snapdragon 8 Gen 3', '5400mAh', '50MP + 50MP + 50MP'),
        ('Realme 12 Pro+', 79900, ['8GB'], ['256GB'], '6.7 inch', 'Snapdragon 7s Gen 2', '5000mAh', '50MP + 64MP + 8MP'),
        ('Realme 12', 59900, ['8GB'], ['128GB'], '6.72 inch', 'Dimensity 6100+', '5000mAh', '108MP + 2MP'),
        ('Realme C67', 44900, ['8GB'], ['256GB'], '6.72 inch', 'Snapdragon 685', '5000mAh', '108MP + 2MP'),
        ('Realme C55', 39900, ['6GB'], ['128GB'], '6.72 inch', 'Helio G88', '5000mAh', '64MP + 2MP'),
    ]},
    'OnePlus': {'color': '#EB0028', 'models': [
        ('OnePlus 12', 189900, ['12GB'], ['256GB'], '6.82 inch', 'Snapdragon 8 Gen 3', '5400mAh', '50MP + 64MP + 48MP'),
        ('OnePlus 12R', 129900, ['8GB'], ['128GB', '256GB'], '6.78 inch', 'Snapdragon 8 Gen 2', '5500mAh', '50MP + 8MP + 2MP'),
        ('OnePlus Nord 3', 89900, ['8GB'], ['128GB'], '6.74 inch', 'Dimensity 9000', '5000mAh', '50MP + 8MP + 2MP'),
        ('OnePlus Nord CE 4', 74900, ['8GB'], ['128GB'], '6.7 inch', 'Snapdragon 7 Gen 3', '5500mAh', '50MP + 8MP'),
    ]},
    'Google': {'color': '#4285F4', 'models': [
        ('Pixel 8 Pro', 229900, ['12GB'], ['128GB', '256GB'], '6.7 inch', 'Google Tensor G3', '5050mAh', '50MP + 48MP + 48MP'),
        ('Pixel 8', 179900, ['8GB'], ['128GB'], '6.2 inch', 'Google Tensor G3', '4575mAh', '50MP + 12MP'),
        ('Pixel 7a', 129900, ['8GB'], ['128GB'], '6.1 inch', 'Google Tensor G2', '4385mAh', '64MP + 13MP'),
    ]},
    'Infinix': {'color': '#00A651', 'models': [
        ('Infinix Zero 30', 69900, ['8GB'], ['256GB'], '6.78 inch', 'Dimensity 8020', '5000mAh', '108MP + 50MP + 2MP'),
        ('Infinix Note 30', 49900, ['8GB'], ['256GB'], '6.78 inch', 'Helio G99', '5000mAh', '108MP + 2MP'),
        ('Infinix Hot 40', 34900, ['8GB'], ['128GB'], '6.78 inch', 'Helio G88', '5000mAh', '108MP + AI'),
        ('Infinix Smart 8', 24900, ['4GB'], ['128GB'], '6.6 inch', 'Unisoc SC9863A', '5000mAh', '13MP'),
    ]},
    'Tecno': {'color': '#0057B8', 'models': [
        ('Tecno Camon 20 Pro', 64900, ['8GB'], ['256GB'], '6.67 inch', 'Dimensity 8050', '5000mAh', '64MP + 13MP + 2MP'),
        ('Tecno Spark 20 Pro', 44900, ['8GB'], ['256GB'], '6.78 inch', 'Helio G99', '5000mAh', '108MP + AI'),
        ('Tecno Spark 10', 34900, ['4GB'], ['128GB'], '6.6 inch', 'Helio G85', '5000mAh', '50MP + AI'),
        ('Tecno Pop 8', 22900, ['3GB'], ['64GB'], '6.6 inch', 'Unisoc SC9863A1', '5000mAh', '13MP'),
    ]},
    'Huawei': {'color': '#CF0A2C', 'models': [
        ('Huawei P60 Pro', 219900, ['12GB'], ['256GB'], '6.67 inch', 'Snapdragon 8+ Gen 1', '4815mAh', '48MP + 48MP + 13MP'),
        ('Huawei Nova 11', 99900, ['8GB'], ['256GB'], '6.7 inch', 'Snapdragon 778G', '4500mAh', '60MP + 8MP'),
        ('Huawei Nova Y72', 54900, ['8GB'], ['128GB'], '6.75 inch', 'Snapdragon 680', '6000mAh', '48MP + 8MP + 2MP'),
    ]},
    'Nokia': {'color': '#124191', 'models': [
        ('Nokia G42 5G', 49900, ['6GB'], ['128GB'], '6.56 inch', 'Snapdragon 480+', '5000mAh', '50MP + 2MP + 2MP'),
        ('Nokia C32', 29900, ['4GB'], ['64GB'], '6.5 inch', 'Unisoc T606', '5000mAh', '50MP + AI'),
        ('Nokia G22', 39900, ['4GB'], ['128GB'], '6.5 inch', 'Unisoc T606', '5050mAh', '50MP + 2MP + 2MP'),
    ]},
}

COLOR_PALETTE = [
    ('Midnight Black', '#1c1c1e'),
    ('Pearl White', '#f5f5f0'),
    ('Ocean Blue', '#2b5fb0'),
    ('Rose Gold', '#e8b4b8'),
    ('Emerald Green', '#1f8a5f'),
    ('Titanium Gray', '#8a8a8d'),
    ('Sunset Orange', '#e8622c'),
    ('Lavender Purple', '#8e7cc3'),
]

CATEGORY_DATA = [
    ('Smartphones', 'bi-phone'),
    ('Tablets', 'bi-tablet'),
    ('Smartwatches', 'bi-smartwatch'),
    ('Earbuds & Headphones', 'bi-earbuds'),
    ('Mobile Accessories', 'bi-usb-plug'),
]

REVIEW_COMMENTS = [
    ("Excellent phone, worth every penny!", 5),
    ("Great camera and battery life.", 5),
    ("Good value for money.", 4),
    ("Performance is smooth, no lag at all.", 5),
    ("Decent phone but heats up a bit.", 3),
    ("Amazing display quality!", 5),
    ("Battery drains faster than expected.", 3),
    ("Best purchase this year.", 5),
    ("Camera could be better in low light.", 4),
    ("Super fast delivery and genuine product.", 5),
]


class Command(BaseCommand):
    help = "Seed the database with brands, categories, 100+ mobile products with color variants, demo customers, reviews and orders."

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing catalog/orders data before seeding.')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data...')
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Review.objects.all().delete()
            ProductColorVariant.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()

        with transaction.atomic():
            self.create_superuser()
            categories = self.create_categories()
            brands = self.create_brands()
            products = self.create_products(brands, categories)
            customers = self.create_customers()
            self.create_reviews(products, customers)
            self.create_orders(products, customers)

        self.stdout.write(self.style.SUCCESS(
            f"\nSeed complete: {Brand.objects.count()} brands, "
            f"{Category.objects.count()} categories, {Product.objects.count()} products, "
            f"{ProductColorVariant.objects.count()} color variants, {Order.objects.count()} orders."
        ))
        self.stdout.write(self.style.WARNING(
            "\nDashboard login -> username: admin | password: admin12345\n"
            "Demo customer login -> username: customer1 | password: customer12345\n"
        ))

    # ------------------------------------------------------------------
    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@xmobilehub.com', 'admin12345')
            self.stdout.write(self.style.SUCCESS('Created staff/admin user: admin / admin12345'))

    def create_categories(self):
        categories = {}
        for name, icon in CATEGORY_DATA:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon_class': icon})
            categories[name] = cat
        self.stdout.write(f"Categories ready: {len(categories)}")
        return categories

    def create_brands(self):
        brands = {}
        for name, data in BRANDS.items():
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={'description': f"{name} - trusted global smartphone manufacturer."}
            )
            if created or not brand.logo:
                svg = generate_brand_logo_svg(name, data['color'])
                brand.logo.save(f"{brand.slug}.svg", ContentFile(svg.encode('utf-8')), save=True)
            brands[name] = brand
        self.stdout.write(f"Brands ready: {len(brands)}")
        return brands

    def create_products(self, brands, categories):
        smartphone_cat = categories['Smartphones']
        products = []
        total_created = 0

        for brand_name, data in BRANDS.items():
            brand = brands[brand_name]
            for model_name, base_price, ram_options, storage_options, display, processor, battery, camera in data['models']:
                # Guarantee at least two storage tiers per model so the catalog
                # comfortably exceeds 100 total product listings.
                if len(storage_options) == 1:
                    bump_map = {'64GB': '128GB', '128GB': '256GB', '256GB': '512GB', '512GB': '1TB'}
                    bumped = bump_map.get(storage_options[0], '256GB')
                    storage_options = storage_options + [bumped]
                for storage in storage_options:
                    ram = random.choice(ram_options)
                    price_bump = storage_options.index(storage) * random.randint(8000, 15000)
                    price = Decimal(base_price + price_bump)
                    has_discount = random.random() < 0.35
                    discount_price = (price * Decimal('0.9')).quantize(Decimal('1')) if has_discount else None

                    product = Product.objects.create(
                        brand=brand,
                        category=smartphone_cat,
                        name=f"{model_name} {ram}/{storage}",
                        model_number=storage,
                        short_description=f"{ram} RAM, {storage} Storage, {display} Display",
                        description=(
                            f"The {brand_name} {model_name} delivers a {display} display, "
                            f"{processor} chipset, {ram} RAM with {storage} storage, a "
                            f"{camera} camera system and a {battery} battery — built for "
                            f"everyday performance and reliability."
                        ),
                        ram=ram,
                        storage=storage,
                        display_size=display,
                        battery=battery,
                        camera=camera,
                        processor=processor,
                        price=price,
                        discount_price=discount_price,
                        stock_quantity=random.choice([0, 3, 4, 5, 8, 12, 15, 20, 25, 30, 40]),
                        is_featured=random.random() < 0.18,
                        is_new_arrival=random.random() < 0.25,
                    )

                    colors = random.sample(COLOR_PALETTE, k=random.choice([2, 2, 3]))
                    for idx, (color_name, color_hex) in enumerate(colors):
                        variant = ProductColorVariant(
                            product=product,
                            color_name=color_name,
                            color_hex=color_hex,
                            stock_quantity=random.randint(0, 15),
                            is_default=(idx == 0),
                        )
                        front_svg = generate_front_svg(brand_name, model_name, color_name, color_hex)
                        back_svg = generate_back_svg(brand_name, model_name, color_name, color_hex)
                        variant.image.save(f"{product.slug}-{idx}.svg", ContentFile(front_svg.encode('utf-8')), save=False)
                        variant.hover_image.save(f"{product.slug}-{idx}-back.svg", ContentFile(back_svg.encode('utf-8')), save=False)
                        variant.save()

                    products.append(product)
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Products created: {total_created}"))
        return products

    def create_customers(self):
        customers = []
        first_names = ['Ali', 'Ahmed', 'Sara', 'Ayesha', 'Bilal', 'Fatima', 'Hassan', 'Zainab', 'Usman', 'Hira']
        last_names = ['Khan', 'Malik', 'Raza', 'Iqbal', 'Sheikh', 'Butt', 'Chaudhry', 'Ansari', 'Farooq', 'Aslam']
        for i in range(1, 11):
            username = f'customer{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='customer12345',
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                )
            else:
                user = User.objects.get(username=username)
            customers.append(user)
        self.stdout.write(f"Demo customers ready: {len(customers)}")
        return customers

    def create_reviews(self, products, customers):
        sample_products = random.sample(products, k=min(60, len(products)))
        count = 0
        for product in sample_products:
            reviewers = random.sample(customers, k=random.randint(1, 4))
            for user in reviewers:
                comment, rating = random.choice(REVIEW_COMMENTS)
                Review.objects.update_or_create(
                    product=product, user=user,
                    defaults={'rating': rating, 'comment': comment, 'title': 'Verified purchase'}
                )
                count += 1
        self.stdout.write(f"Reviews created: {count}")

    def create_orders(self, products, customers):
        statuses = [Order.STATUS_DELIVERED, Order.STATUS_DELIVERED, Order.STATUS_DELIVERED,
                    Order.STATUS_SHIPPED, Order.STATUS_PROCESSING, Order.STATUS_PENDING,
                    Order.STATUS_CANCELLED]
        cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar']
        order_count = 0
        for _ in range(140):
            user = random.choice(customers)
            days_ago = random.randint(0, 45)
            order_products = random.sample(products, k=random.randint(1, 3))

            order = Order.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                email=user.email,
                phone=f"03{random.randint(10,49)}{random.randint(1000000,9999999)}",
                address=f"House {random.randint(1,900)}, Street {random.randint(1,50)}",
                city=random.choice(cities),
                payment_method=random.choice(['cod', 'card', 'bank_transfer']),
                status=random.choice(statuses),
            )
            subtotal = Decimal('0')
            for product in order_products:
                variant = product.default_variant
                qty = random.randint(1, 2)
                price = product.current_price
                OrderItem.objects.create(
                    order=order, product=product, variant=variant,
                    product_name=product.name,
                    color_name=variant.color_name if variant else '',
                    price=price, quantity=qty,
                )
                subtotal += price * qty
                if order.status == Order.STATUS_DELIVERED:
                    product.total_sold += qty
                    product.save(update_fields=['total_sold'])

            shipping = Decimal('0') if subtotal >= 50000 else Decimal('250')
            order.subtotal = subtotal
            order.shipping_fee = shipping
            order.total_amount = subtotal + shipping
            order.save(update_fields=['subtotal', 'shipping_fee', 'total_amount'])

            # Backdate created_at for a realistic 45-day sales trend
            backdated = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            Order.objects.filter(pk=order.pk).update(created_at=backdated, updated_at=backdated)
            order_count += 1

        self.stdout.write(self.style.SUCCESS(f"Demo orders created: {order_count}"))
