# XMobile Hub 📱

A full multi-brand mobile e-commerce platform built with Django — genuine
phones from every major brand, AJAX-driven shopping (no page reloads for
cart, wishlist, color selection or filtering), and a custom industry-level
analytics dashboard (no Django admin involved).

## Features

- **Multi-brand catalog** — 12 real brands (Apple, Samsung, Xiaomi, Oppo,
  Vivo, Realme, OnePlus, Google, Infinix, Tecno, Huawei, Nokia) and 110+
  seeded products across Smartphones, Tablets, Smartwatches, Earbuds &
  Accessories.
- **Color variants with live image swap** — clicking a color swatch swaps
  the product photo instantly (client-side, zero requests). Hovering a
  product card swaps to a secondary "back view" image. Clicking the
  already-selected color is a no-op.
- **Zero-reload shopping** — add to cart, update quantity, remove items,
  toggle wishlist, filter/sort the shop grid, search suggestions, and
  newsletter sign-up are all handled over `fetch()` with JSON responses.
- **Custom staff dashboard** (`/dashboard/`) — a bespoke, industry-style
  admin replacing the default Django admin entirely:
  - Live KPI tiles (revenue, orders, stock levels, low/out-of-stock alerts)
    that auto-refresh every 8 seconds via polling — no page reload.
  - Chart.js analytics: 30-day sales trend, order status split,
    revenue-by-category, and units-sold-by-brand.
  - Full CRUD for products (with inline color-variant management),
    categories, and brands — deletions are AJAX with instant row removal.
  - Order management with inline AJAX status updates.
- **Complete storefront pages** — home, shop/filter, product detail,
  cart, checkout, order confirmation, customer account & order history,
  About Us, Contact Us, Terms & Conditions, Privacy Policy, Shipping
  Policy, Refund Policy, FAQs, and custom 404/500 pages.
- **Professional branding** — custom logo, generated `favicon.ico`,
  consistent header/footer across every page.

## Project Structure

```
XMobileHub/
├── manage.py
├── core/                   # Settings, root urls, wsgi/asgi  (the "settings" folder)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # All Django apps live here
│   ├── accounts/           # Registration, login, profile, order history
│   ├── products/           # Brand, Category, Product, Color Variants, Reviews
│   ├── cart/                # Session-based AJAX cart
│   ├── orders/              # Checkout + order models
│   ├── dashboard/           # Custom staff analytics dashboard (replaces admin)
│   └── pages/                # Home + static/legal pages
├── templates/               # All HTML, organized by app
│   ├── base.html
│   ├── accounts/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── dashboard/
│   └── pages/
├── static/
│   ├── css/style.css
│   ├── js/main.js            # Storefront AJAX interactions
│   ├── js/dashboard.js        # Dashboard live polling + AJAX CRUD
│   ├── favicon.ico
│   └── img/logo.svg
├── media/                    # Uploaded/seeded product & brand images
├── requirements.txt
├── .env                      # Local dev environment (already filled in)
├── .env.example               # Template for other environments
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MuhammadNouman769/X_mobile_hub.git
cd X_mobile_hub
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Environment variables

A working `.env` is already included for local development. To customize
it, copy the example instead:

```bash
cp .env.example .env
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed the database (brands, categories, 110+ products, demo orders)

```bash
python manage.py seed_data
```

This creates:
- A staff account for the dashboard: **admin / admin12345**
- 10 demo customer accounts: **customer1**...**customer10 / customer12345**
- 12 brands, 5 categories, 110+ products with 2–3 color variants each
  (SVG placeholder photos generated automatically — no external images
  needed)
- ~140 backdated demo orders so the dashboard analytics have real data
  to chart from day one

Re-running with `--flush` wipes and reseeds the catalog:

```bash
python manage.py seed_data --flush
```

### 6. Run the development server

```bash
python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- Staff dashboard: http://127.0.0.1:8000/dashboard/ (login: `admin` / `admin12345`)

> Note: Django's default admin is still wired up at `/secret-admin/` for
> emergency/technical use, but the project's real management interface —
> the one meant for daily use — is the custom dashboard at `/dashboard/`.

## Notes on Product Images

Seeded product photos are generated as lightweight SVG files (no external
image downloads or paid stock photos required), so the project works
out of the box with zero extra setup. When you upload your own product
photos through the dashboard's "Add/Edit Product" form, use standard
JPG/PNG/WEBP files — the upload form validates images with Pillow, which
doesn't parse SVG, so real photos are the way to go for anything you add
after seeding.

## Tech Stack

- Django 5 (SQLite by default — swap `DB_ENGINE`/`DB_NAME` in `.env` for
  Postgres/MySQL in production)
- Bootstrap 5 + Bootstrap Icons (CDN)
- Chart.js (CDN) for dashboard analytics
- Vanilla JavaScript (`fetch`) for all no-reload interactions — no
  frontend framework/build step required

## Production Checklist

- Set `DEBUG=False` and a real `SECRET_KEY` in `.env`
- Set `ALLOWED_HOSTS` to your real domain(s)
- Point `DB_ENGINE`/`DB_NAME` (and add host/user/password settings) to a
  production database
- Run `python manage.py collectstatic` and serve `/static/` via your web
  server or a CDN
- Configure a real `EMAIL_BACKEND`/SMTP credentials
- Put the app behind HTTPS and a process manager (gunicorn/uwsgi + nginx)
