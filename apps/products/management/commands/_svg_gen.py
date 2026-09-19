"""Lightweight SVG placeholder generator used by the seed_data command so the
project can ship 100+ products with real, visually distinct color-variant
images without depending on Pillow or any binary image assets."""

FRONT_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f4f5f7"/>
      <stop offset="100%" stop-color="#e7e9ec"/>
    </linearGradient>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="100%" stop-color="{color_dark}"/>
    </linearGradient>
  </defs>
  <rect width="500" height="600" fill="url(#bg)"/>
  <rect x="130" y="60" width="240" height="480" rx="42" ry="42" fill="url(#body)" stroke="#00000022" stroke-width="2"/>
  <rect x="146" y="96" width="208" height="410" rx="20" ry="20" fill="#0d0d0f"/>
  <rect x="152" y="102" width="196" height="398" rx="16" ry="16" fill="#15151a"/>
  <circle cx="250" cy="108" r="4" fill="#333"/>
  <rect x="215" y="565" width="70" height="6" rx="3" fill="#00000033"/>
  <text x="250" y="560" font-family="Arial, sans-serif" font-size="18" fill="#2b2b2f" text-anchor="middle" font-weight="600">{brand} {model}</text>
  <text x="250" y="580" font-family="Arial, sans-serif" font-size="13" fill="#6b6b70" text-anchor="middle">{color_name}</text>
</svg>"""

BACK_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 600">
  <defs>
    <linearGradient id="bgb" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eef0f3"/>
      <stop offset="100%" stop-color="#dfe2e6"/>
    </linearGradient>
    <linearGradient id="bodyb" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_dark}"/>
      <stop offset="100%" stop-color="{color}"/>
    </linearGradient>
  </defs>
  <rect width="500" height="600" fill="url(#bgb)"/>
  <rect x="130" y="60" width="240" height="480" rx="42" ry="42" fill="url(#bodyb)" stroke="#00000022" stroke-width="2"/>
  <rect x="160" y="90" width="100" height="100" rx="24" fill="#00000022"/>
  <circle cx="190" cy="120" r="16" fill="#111"/>
  <circle cx="190" cy="120" r="9" fill="#3a3a3a"/>
  <circle cx="228" cy="120" r="16" fill="#111"/>
  <circle cx="228" cy="120" r="9" fill="#3a3a3a"/>
  <circle cx="190" cy="158" r="16" fill="#111"/>
  <circle cx="190" cy="158" r="9" fill="#3a3a3a"/>
  <rect x="215" y="180" width="30" height="14" rx="4" fill="#111"/>
  <text x="250" y="560" font-family="Arial, sans-serif" font-size="18" fill="#2b2b2f" text-anchor="middle" font-weight="600">{brand} {model}</text>
  <text x="250" y="580" font-family="Arial, sans-serif" font-size="13" fill="#6b6b70" text-anchor="middle">{color_name} · Back View</text>
</svg>"""

BRAND_LOGO_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="92" fill="{color}"/>
  <text x="100" y="122" font-family="Arial, sans-serif" font-size="72" fill="#ffffff" text-anchor="middle" font-weight="700">{initial}</text>
</svg>"""


def _shade(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        hex_color = '888888'
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_front_svg(brand, model, color_name, color_hex):
    return FRONT_TEMPLATE.format(
        color=color_hex, color_dark=_shade(color_hex, 0.72),
        brand=brand, model=model, color_name=color_name,
    )


def generate_back_svg(brand, model, color_name, color_hex):
    return BACK_TEMPLATE.format(
        color=color_hex, color_dark=_shade(color_hex, 0.72),
        brand=brand, model=model, color_name=color_name,
    )


def generate_brand_logo_svg(brand_name, color_hex):
    return BRAND_LOGO_TEMPLATE.format(color=color_hex, initial=brand_name[0].upper())
