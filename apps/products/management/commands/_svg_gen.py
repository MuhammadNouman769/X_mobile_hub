"""Lightweight SVG product-render generator used by the seed_data command so
the project ships 100+ products with realistic, visually distinct
color-variant photography without depending on Pillow, network access, or
any copyrighted manufacturer imagery. Every render is 100% original artwork:
a studio-style backdrop, a glossy multi-tone phone body, a lock-screen UI
mockup on the front, and a camera-module render on the back."""

FRONT_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 620">
  <defs>
    <radialGradient id="backdrop-{uid}" cx="50%" cy="38%" r="75%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="55%" stop-color="#f1f2f5"/>
      <stop offset="100%" stop-color="#e2e4e9"/>
    </radialGradient>
    <linearGradient id="body-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_light}"/>
      <stop offset="48%" stop-color="{color}"/>
      <stop offset="100%" stop-color="{color_dark}"/>
    </linearGradient>
    <linearGradient id="sheen-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="28%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="55%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="screen-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{color_dark}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0a0a0c"/>
    </linearGradient>
    <radialGradient id="shadow-{uid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="500" height="620" fill="url(#backdrop-{uid})"/>
  <ellipse cx="250" cy="572" rx="130" ry="20" fill="url(#shadow-{uid})"/>

  <!-- phone body -->
  <rect x="128" y="46" width="244" height="500" rx="46" ry="46" fill="url(#body-{uid})" stroke="#00000014" stroke-width="1.5"/>
  <rect x="128" y="46" width="244" height="500" rx="46" ry="46" fill="url(#sheen-{uid})"/>

  <!-- side buttons -->
  <rect x="124" y="150" width="5" height="34" rx="2.5" fill="#00000030"/>
  <rect x="124" y="196" width="5" height="60" rx="2.5" fill="#00000030"/>
  <rect x="371" y="168" width="5" height="76" rx="2.5" fill="#00000030"/>

  <!-- screen -->
  <rect x="142" y="64" width="216" height="464" rx="32" ry="32" fill="url(#screen-{uid})"/>

  <!-- dynamic island / notch -->
  <rect x="216" y="80" width="68" height="20" rx="10" fill="#000000"/>
  <circle cx="266" cy="90" r="3" fill="#1c2733"/>

  <!-- status bar -->
  <text x="164" y="112" font-family="Arial, sans-serif" font-size="12" fill="#ffffff" font-weight="600">9:41</text>
  <g fill="#ffffff">
    <rect x="316" y="104" width="3" height="8" rx="1"/>
    <rect x="321" y="101" width="3" height="11" rx="1"/>
    <rect x="326" y="98" width="3" height="14" rx="1"/>
    <rect x="333" y="100" width="18" height="10" rx="2.5" fill="none" stroke="#ffffff" stroke-width="1.4"/>
    <rect x="335" y="102" width="12" height="6" rx="1.2"/>
  </g>

  <!-- lock screen clock -->
  <text x="250" y="230" font-family="'Poppins', Arial, sans-serif" font-size="46" fill="#ffffff" text-anchor="middle" font-weight="600" opacity="0.96">10:24</text>
  <text x="250" y="256" font-family="Arial, sans-serif" font-size="13" fill="#ffffff" text-anchor="middle" opacity="0.7">{brand} {model}</text>

  <!-- wallpaper accent shapes -->
  <circle cx="250" cy="360" r="70" fill="{color}" opacity="0.35"/>
  <circle cx="250" cy="360" r="46" fill="{color_light}" opacity="0.4"/>

  <!-- home indicator -->
  <rect x="222" y="500" width="56" height="5" rx="2.5" fill="#ffffff" opacity="0.55"/>

  <!-- caption -->
  <text x="250" y="600" font-family="Arial, sans-serif" font-size="17" fill="#232326" text-anchor="middle" font-weight="600">{brand} {model}</text>
  <text x="250" y="617" font-family="Arial, sans-serif" font-size="12.5" fill="#7a7a80" text-anchor="middle">{color_name}</text>
</svg>"""

BACK_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 620">
  <defs>
    <radialGradient id="backdropb-{uid}" cx="50%" cy="38%" r="75%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="55%" stop-color="#eef0f3"/>
      <stop offset="100%" stop-color="#dfe2e7"/>
    </radialGradient>
    <linearGradient id="bodyb-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_dark}"/>
      <stop offset="45%" stop-color="{color}"/>
      <stop offset="100%" stop-color="{color_light}"/>
    </linearGradient>
    <linearGradient id="sheenb-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.5"/>
      <stop offset="30%" stop-color="#ffffff" stop-opacity="0.05"/>
      <stop offset="60%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="lens-{uid}" cx="35%" cy="30%" r="75%">
      <stop offset="0%" stop-color="#5a5f6b"/>
      <stop offset="55%" stop-color="#15161a"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>
    <radialGradient id="shadowb-{uid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="500" height="620" fill="url(#backdropb-{uid})"/>
  <ellipse cx="250" cy="572" rx="130" ry="20" fill="url(#shadowb-{uid})"/>

  <!-- phone body -->
  <rect x="128" y="46" width="244" height="500" rx="46" ry="46" fill="url(#bodyb-{uid})" stroke="#00000014" stroke-width="1.5"/>
  <rect x="128" y="46" width="244" height="500" rx="46" ry="46" fill="url(#sheenb-{uid})"/>

  <!-- camera module -->
  <rect x="158" y="80" width="118" height="118" rx="30" fill="#00000022"/>
  <rect x="158" y="80" width="118" height="118" rx="30" fill="none" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1.5"/>

  <circle cx="196" cy="118" r="24" fill="url(#lens-{uid})"/>
  <circle cx="196" cy="118" r="24" fill="none" stroke="#00000055" stroke-width="2"/>
  <circle cx="188" cy="110" r="5" fill="#ffffff" opacity="0.5"/>

  <circle cx="240" cy="118" r="24" fill="url(#lens-{uid})"/>
  <circle cx="240" cy="118" r="24" fill="none" stroke="#00000055" stroke-width="2"/>
  <circle cx="232" cy="110" r="5" fill="#ffffff" opacity="0.5"/>

  <circle cx="196" cy="162" r="18" fill="url(#lens-{uid})"/>
  <circle cx="196" cy="162" r="18" fill="none" stroke="#00000055" stroke-width="2"/>
  <circle cx="190" cy="156" r="3.6" fill="#ffffff" opacity="0.5"/>

  <rect x="228" y="150" width="26" height="12" rx="4" fill="#0c0c0e"/>
  <rect x="228" y="150" width="26" height="12" rx="4" fill="none" stroke="#ffffff" stroke-opacity="0.15"/>

  <!-- brand wordmark, subtly etched -->
  <text x="250" y="420" font-family="'Poppins', Arial, sans-serif" font-size="22" fill="#ffffff" fill-opacity="0.5" text-anchor="middle" font-weight="600" letter-spacing="1">{brand}</text>
  <text x="250" y="444" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" fill-opacity="0.35" text-anchor="middle" letter-spacing="2">5G</text>

  <!-- caption -->
  <text x="250" y="600" font-family="Arial, sans-serif" font-size="17" fill="#232326" text-anchor="middle" font-weight="600">{brand} {model}</text>
  <text x="250" y="617" font-family="Arial, sans-serif" font-size="12.5" fill="#7a7a80" text-anchor="middle">{color_name} &#183; Back View</text>
</svg>"""

BRAND_LOGO_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="badge-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_light}"/>
      <stop offset="100%" stop-color="{color_dark}"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="184" height="184" rx="48" fill="url(#badge-{uid})"/>
  <rect x="8" y="8" width="184" height="90" rx="48" fill="#ffffff" opacity="0.12"/>
  <text x="100" y="128" font-family="'Poppins', Arial, sans-serif" font-size="80" fill="#ffffff" text-anchor="middle" font-weight="700">{initial}</text>
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


def _uid(*parts):
    """A short, template-safe id suffix so multiple inline SVGs on the same
    page never clash on gradient/filter ids."""
    raw = "-".join(str(p) for p in parts)
    return "".join(ch for ch in raw if ch.isalnum())[:24] or "x"


def generate_front_svg(brand, model, color_name, color_hex):
    return FRONT_TEMPLATE.format(
        uid=_uid(brand, model, color_name, "f"),
        color=color_hex,
        color_light=_shade(color_hex, 1.35),
        color_dark=_shade(color_hex, 0.68),
        brand=brand, model=model, color_name=color_name,
    )


def generate_back_svg(brand, model, color_name, color_hex):
    return BACK_TEMPLATE.format(
        uid=_uid(brand, model, color_name, "b"),
        color=color_hex,
        color_light=_shade(color_hex, 1.35),
        color_dark=_shade(color_hex, 0.68),
        brand=brand, model=model, color_name=color_name,
    )


def generate_brand_logo_svg(brand_name, color_hex):
    return BRAND_LOGO_TEMPLATE.format(
        uid=_uid(brand_name, "logo"),
        color_light=_shade(color_hex, 1.3),
        color_dark=_shade(color_hex, 0.75),
        initial=brand_name[0].upper(),
    )
