"""Server-rendered HTML views. All markup is generated with the standard library."""
import html
import json
import os
import re
import urllib.parse
from datetime import datetime
from pathlib import Path

import db
import seed
import admin_views

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

# ---------- CSRF helper ----------
# app.py sets this after import so forms can embed the token without circular imports.
def get_csrf_input(token: str = "") -> str:
    """Return a hidden <input> for CSRF protection. token is the per-session CSRF token."""
    if not token:
        return ""
    return f'<input type="hidden" name="_csrf" value="{html.escape(token, quote=True)}">'

# Thread-local storage for the current request's CSRF token (set by app.py dispatcher)
import threading as _threading
_request_local = _threading.local()

def _set_csrf(token: str) -> None:
    _request_local.csrf_token = token

def _get_csrf() -> str:
    return getattr(_request_local, "csrf_token", "")

def csrf_input() -> str:
    """Render hidden CSRF input using the current request's token."""
    return get_csrf_input(_get_csrf())


def e(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


_DATA_IMG_RE = re.compile(
    r"^data:image/(png|jpeg|jpg|webp|gif);base64,[A-Za-z0-9+/=\s]+$",
    re.IGNORECASE,
)


def safe_http_url(url, max_len=500):
    val = (url or "").strip()
    if not val or len(val) > max_len or any(c in val for c in ("\r", "\n", "\x00")):
        return ""
    parsed = urllib.parse.urlparse(val)
    if parsed.scheme.lower() in ("http", "https") and parsed.netloc:
        return val
    return ""


def safe_media_url(url, default=""):
    val = (url or "").strip()
    if not val or any(c in val for c in ("\r", "\n", "\x00")):
        return default
    if val.startswith("/") and not val.startswith("//"):
        return val if len(val) <= 500 else default
    if _DATA_IMG_RE.match(val) and len(val) <= 3_000_000:
        return val
    http_val = safe_http_url(val, max_len=1000)
    return http_val or default


CATEGORY_BY_SLUG = {slugify(c): c for c in seed.CATEGORIES}
SALARY_BY_SLUG = {slugify(s["title"]): s for s in seed.SALARIES}
TAG_BY_SLUG = {slugify(t): t for t in sorted({a["tag"] for a in seed.ARTICLES})}
HUB_BY_SLUG = {h["slug"]: h for h in seed.TECH_HUBS}


def qs(params):
    clean = {k: v for k, v in params.items() if v not in (None, "", False, 0)}
    return urllib.parse.urlencode(clean, doseq=True)


def url(path, **params):
    query = qs(params)
    return path + ("?" + query if query else "")


def money(value):
    return "${:,.0f}".format(value or 0)


def thousands(value):
    return "{:,}".format(value or 0)


def contrast_text(hex_color):
    h = (hex_color or "#244fe7").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#04003f" if lum > 0.62 else "#ffffff"
    except ValueError:
        return "#ffffff"


ICON_PATHS = {
    "search": '<circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.7-7.5 1.1-1.1a5.5 5.5 0 0 0 0-7.8z"></path>',
    "bell": '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 1 1 16 0z"></path><circle cx="12" cy="10" r="2.5"></circle>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"></rect><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>',
    "clock": '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>',
    "money": '<path d="M12 2v20"></path><path d="M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "trophy": '<path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M7 4h10v5a5 5 0 0 1-10 0V4z"></path><path d="M7 6H4v2a3 3 0 0 0 3 3"></path><path d="M17 6h3v2a3 3 0 0 1-3 3"></path>',
    "users": '<circle cx="9" cy="8" r="3"></circle><path d="M3 20a6 6 0 0 1 12 0"></path><path d="M16 5a3 3 0 0 1 0 6"></path><path d="M18 14a5 5 0 0 1 3 5"></path>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"></rect><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"></path>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"></path>',
    "chevron": '<path d="m6 9 6 6 6-6"></path>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"></path><path d="M19 16l.7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16z"></path>',
    "check": '<path d="m5 12 4 4L19 6"></path>',
    "filter": '<path d="M4 6h16M7 12h10M10 18h4"></path>',
    "external": '<path d="M14 4h6v6"></path><path d="M20 4 10 14"></path><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"></path>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2V5z"></path><path d="M8 3v18"></path>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"></path>',
    "close": '<path d="M6 6l12 12M18 6 6 18"></path>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"></path>',
    "shield": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6l8-3z"></path>',
    "globe": '<circle cx="12" cy="12" r="9"></circle><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"></path>',
    "lightning": '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"></path>',
    "plus": '<path d="M12 5v14M5 12h14"></path>',
    "edit": '<path d="M4 20h4l10-10-4-4L4 16v4z"></path><path d="M14 6l4 4"></path>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14"></path>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9L12 3z"></path>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5z"></path><path d="m3 13 9 5 9-5M3 17l9 5 9-5"></path>',
}


def icon(name, size=18, extra=""):
    return (
        f'<svg class="icon {extra}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{ICON_PATHS.get(name, "")}</svg>'
    )


def brand_logo():
    return (
        '<a class="brand brand-logistic-waves" href="/" aria-label="Logistics Waves">'
        '<span class="brand-diamond-wrap">'
        '<img class="brand-diamond-logo" src="/static/images/logo_emblem.png?v=20261114_shaped" alt="Logistics Waves" width="40" height="42" decoding="async" fetchpriority="high">'
        '</span>'
        '<span class="brand-text-lw">'
        '<span class="brand-title-row">'
        '<span class="brand-lw-main">LOGISTICS</span>'
        '<span class="brand-lw-accent">WAVES</span>'
        '</span>'
        '<span class="brand-sub-row">GLOBAL LOGISTICS</span>'
        '</span>'
        '</a>'
    )


def _brand_logo_markup(slug, name, initials="CO", color="#244fe7", size=84, img_id="", lazy=True):
    brand_svg = STATIC / "images" / "brands" / f"{slug}.svg" if slug else None
    if brand_svg and not brand_svg.is_file() and initials:
        init_svg = STATIC / "images" / "brands" / f"{initials.lower()}.svg"
        if init_svg.is_file():
            brand_svg = init_svg
    if brand_svg and brand_svg.is_file():
        id_attr = f' id="{e(img_id)}"' if img_id else ""
        load_attr = ' loading="lazy"' if lazy else ""
        return (
            f'<img src="/static/images/brands/{e(brand_svg.name)}" alt="{e(name)}"{id_attr}'
            f' width="{size}" height="{size}" decoding="async"{load_attr}'
            f' data-fallback-kind="brand" data-initials="{e(initials or "CO")}" data-color="{e(color or "#003366")}"'
            f' style="width:100%;height:100%;max-width:{size}px;max-height:{size}px;object-fit:contain;background:transparent;border:none;">'
        )
    text_color = contrast_text(color)
    return (
        f'<div style="width:{size}px;height:{size}px;min-width:{size}px;min-height:{size}px;'
        f'background:{e(color or "#003366")};color:{e(text_color)};display:flex;align-items:center;'
        f'justify-content:center;font-weight:800;font-size:{max(14, int(size * 0.31))}px;border-radius:10px;border:none;">'
        f'{e(initials or "CO")}</div>'
    )


def company_logo(company, size=84, extra=""):
    slug = company.get("slug") or company.get("company_slug") or ""
    color = company.get("color") or company.get("company_color") or "#244fe7"
    initials = company.get("initials") or company.get("company_initials") or "?"
    name = company.get("name") or company.get("company_name") or "Company"
    if slug:
        brand_svg = STATIC / "images" / "brands" / f"{slug}.svg"
        if brand_svg.is_file():
            return (
                f'<span class="company-logo brand-img-logo {extra}" style="width:{size}px;height:{size}px;min-width:{size}px;min-height:{size}px;display:inline-flex;'
                f'align-items:center;justify-content:center;background:transparent;border:none;box-shadow:none;padding:0;overflow:hidden;" aria-hidden="true">'
                f'{_brand_logo_markup(slug, name, initials=initials, color=color, size=size)}</span>'
            )
    text = contrast_text(color)
    return (
        f'<span class="company-logo {extra}" style="--logo-bg:{e(color)};--logo-fg:{e(text)};'
        f'width:{size}px;height:{size}px;min-width:{size}px;min-height:{size}px;border-radius:10px;border:none;box-shadow:none;font-weight:800;font-size:{max(14, int(size * 0.36))}px;display:inline-flex;align-items:center;justify-content:center;" aria-hidden="true">'
        f'{e(initials)}</span>'
    )


def photo_placeholder(accent="#244fe7", label="Add your photo", slug="photo", variant=0, height=180):
    gid = "pg-" + re.sub(r"[^a-zA-Z0-9]", "", slug)[:14] + "-" + str(variant)
    return f'''
    <div class="photo-frame" style="--photo-h:{height}px">
      <svg viewBox="0 0 400 220" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Placeholder illustration for {e(label)}">
        <defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="{e(accent)}" stop-opacity=".14"/>
          <stop offset="1" stop-color="{e(accent)}" stop-opacity=".58"/>
        </linearGradient></defs>
        <rect width="400" height="220" fill="url(#{gid})"/>
        <circle cx="332" cy="44" r="68" fill="#ffffff" opacity=".20"/>
        <circle cx="58" cy="190" r="92" fill="#ffffff" opacity=".13"/>
        <path d="M0 178 L66 122 L118 158 L188 92 L258 152 L330 102 L400 158 V220 H0Z" fill="{e(accent)}" opacity=".20"/>
        <g fill="#ffffff" opacity=".55">
          <rect x="34" y="98" width="26" height="58" rx="2"/><rect x="70" y="76" width="32" height="80" rx="2"/>
          <rect x="112" y="112" width="24" height="44" rx="2"/><rect x="252" y="92" width="30" height="64" rx="2"/>
          <rect x="292" y="68" width="28" height="88" rx="2"/><rect x="330" y="110" width="34" height="46" rx="2"/>
        </g>
        <g stroke="#ffffff" stroke-width="3" opacity=".42" stroke-linecap="round">
          <path d="M22 196h356M48 184l18-18 18 18M278 184l20-20 20 20"/>
        </g>
      </svg>
      <span class="photo-label">{icon("plus", 12)} {e(label)}</span>
    </div>'''


def select(name, options, current="", placeholder="", cls="", attrs=""):
    out = [f'<select name="{e(name)}" class="{e(cls)}" {attrs}>']
    if placeholder:
        out.append(f'<option value="">{e(placeholder)}</option>')
    for opt in options:
        if isinstance(opt, (tuple, list)):
            value, label = opt
        else:
            value = label = opt
        selected = " selected" if str(current) == str(value) else ""
        out.append(f'<option value="{e(value)}"{selected}>{e(label)}</option>')
    out.append("</select>")
    return "".join(out)


def pill_link(label, href, active=False, icon_name=None):
    cls = "filter-pill active" if active else "filter-pill"
    inner = (icon(icon_name, 14) if icon_name else "") + f"<span>{e(label)}</span>"
    return f'<a class="{cls}" href="{e(href)}">{inner}</a>'


def breadcrumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            parts.append(f'<a href="{e(href)}">{e(label)}</a>')
        else:
            parts.append(f'<span>{e(label)}</span>')
        if i < len(items) - 1:
            parts.append('<span class="crumb-sep">/</span>')
    return '<nav class="breadcrumb" aria-label="Breadcrumb">' + "".join(parts) + "</nav>"


def promo_ticker():
    messages = [
        "Verified engineering, logistics, and supply chain roles open across top global employers",
        "Saigon Newport, Gemadept, Viconship, and DHL are actively hiring across port and remote hubs",
        "Employers: Publish and manage open positions directly from your workspace",
        "2026 Best Places to Work rankings announced \u2014 explore winning workplaces",
        "Certified tech and logistics training courses now enrolling for 2026",
    ]
    def render_items(aria_hidden=False):
        hidden_attr = ' aria-hidden="true"' if aria_hidden else ''
        content = []
        for msg in messages:
            content.append(f'<span class="promo-ticker-text">{e(msg)}</span><span class="promo-ticker-dot" aria-hidden="true">&bull;</span>')
        return f'<div class="promo-ticker-track"{hidden_attr}>' + "".join(content) + '</div>'

    return f"""
    <div class="promo-running-bar" id="promoRunningBar" role="region" aria-label="Announcements">
      <script>
        (function() {{
          try {{
            var next = localStorage.getItem('bi_promo_next_popup');
            if (next && Date.now() < parseInt(next, 10)) {{
              document.getElementById('promoRunningBar').style.display = 'none';
              document.documentElement.style.setProperty('--header-promo-offset', '0px');
            }}
          }} catch(e) {{}}
        }})();
      </script>
      <div class="container promo-running-inner">
        <div class="promo-ticker-viewport">
          {render_items(False)}
          {render_items(True)}
        </div>
      </div>
      <script>
        (function() {{
          var bar = document.getElementById('promoRunningBar');
          if (!bar) return;
          try {{
            var next = localStorage.getItem('bi_promo_next_popup');
            if (next && Date.now() < parseInt(next, 10)) {{
              bar.style.display = 'none';
              document.documentElement.style.setProperty('--header-promo-offset', '0px');
              return;
            }}
          }} catch(e) {{}}

          var track = bar.querySelector('.promo-ticker-track');
          if (track) {{
            track.addEventListener('animationend', function() {{
              bar.classList.add('promo-fade-out');
              setTimeout(function() {{
                bar.style.display = 'none';
                bar.classList.add('is-hidden');
                document.documentElement.style.setProperty('--header-promo-offset', '0px');
              }}, 600);
              try {{
                var tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                tomorrow.setHours(0, 0, 0, 0);
                localStorage.setItem('bi_promo_next_popup', tomorrow.getTime().toString());
              }} catch(e) {{}}
            }});
          }}
        }})();
      </script>
    </div>"""
# ---------- shell ----------

def header(user, active=""):
    def nav_link(label, href, key):
        cls = "nav-link active" if active == key else "nav-link"
        return f'<a class="{cls}" href="{e(href)}">{e(label)}</a>'

    if user:
        initials = "".join(w[0] for w in user["name"].split()[:2]).upper()
        admin_link = ""
        if user.get("role") == "admin":
            admin_link = '<a href="/admin" style="color:#034f9a;font-weight:600;"><i class="fa-solid fa-gauge-high" style="font-size:13px;width:15px;margin-right:6px;"></i> Admin Dashboard</a>'
        avatar_src = user.get("avatar") or "/static/images/default_user_avatar.png"
        account = f'''
        <div class="user-dropdown">
          <button class="user-avatar" type="button" aria-label="Account menu">
            <img class="user-avatar-img" src="{avatar_src}" alt="Profile" width="36" height="36" decoding="async" data-fallback-kind="avatar">
          </button>
          <div class="dropdown-menu">
            <div class="dropdown-head">
              <div class="dropdown-user-row">
                <img class="dropdown-avatar-thumb" src="{avatar_src}" alt="Profile" width="38" height="38" decoding="async" data-fallback-kind="avatar">
                <div class="dropdown-user-info">
                  <strong>{e(user["name"])}</strong>
                  <span>{e(user["email"])}</span>
                </div>
              </div>
            </div>
            <a href="/profile">{icon("users", 15)} Profile</a>
            <a href="/saved">{icon("heart", 15)} Saved Jobs</a>
            <a href="/tracker">{icon("check", 15)} Application Tracker</a>
            <a href="/alerts">{icon("bell", 15)} Job Alerts</a>
            <a href="/employers">{icon("building", 15)} Employer Portal</a>
            {admin_link}
            <form method="post" action="/logout">{csrf_input()}<button type="submit">{icon("external", 15)} Log Out</button></form>
          </div>
        </div>'''
    else:
        account = (
            '<a class="header-auth" href="/auth/signup">Join</a>'
            '<span class="header-sep">|</span>'
            '<a class="header-auth" href="/auth/login">Log In</a>'
        )

    mobile_links = "".join([
        nav_link("Home", "/", "home"),
        nav_link("Companies", "/companies", "companies"),
        nav_link("Jobs", "/jobs", "jobs"),
        nav_link("Articles", "/article-blogs", "articles"),
        nav_link("Courses", "/courses", "courses"),
        '<a class="nav-link" href="/salaries">Salaries</a>',
        '<a class="nav-link" href="/remote">Remote</a>',
        '<a class="nav-link" href="/awards">Best Places To Work</a>',
        '<a class="nav-link" href="/tracker">Tracker</a>',
        '<a class="nav-link" href="/auth/login">Log In / Join</a>',
    ])
    return f'''
    <header class="site-header">
      <div class="container header-inner">
        {brand_logo()}
        <nav class="main-nav" aria-label="Primary">
          {nav_link("Home", "/", "home")}
          {nav_link("Companies", "/companies", "companies")}
          {nav_link("Jobs", "/jobs", "jobs")}
          {nav_link("Articles", "/article-blogs", "articles")}
          {nav_link("Courses", "/courses", "courses")}
        </nav>
        <div class="header-actions">
          <button class="icon-btn search-trigger" type="button" aria-label="Open search">{icon("search", 22)}</button>
          {account}
          <a class="btn btn-outline-light employer-btn" href="/employers">For Employers</a>
          <button class="icon-btn mobile-menu-btn" type="button" aria-label="Open menu">{icon("menu", 24)}</button>
        </div>
      </div>
      <nav class="mobile-nav" aria-label="Mobile">{mobile_links}</nav>
      {promo_ticker()}
    </header>
    <div class="search-overlay" id="searchOverlay" hidden>
      <div class="container search-overlay-inner">
        <div class="search-overlay-bar">
          {icon("search", 22)}
          <input id="globalSearchInput" type="search" autocomplete="off" placeholder="Search jobs, companies and articles" aria-label="Search">
          <button class="icon-btn" id="closeSearch" type="button" aria-label="Close search">{icon("close", 22)}</button>
        </div>
        <div id="globalSearchResults" class="global-search-results"></div>
      </div>
    </div>'''


def footer():
    columns = [
        ("Opportunities", [
            ("Logistics & Tech Jobs", "/jobs"),
            ("Remote Opportunities", "/remote"),
            ("Company Directory", "/companies"),
            ("Industry Courses", "/courses"),
            ("Salary Benchmarks", "/salaries"),
            ("Best Places to Work", "/awards"),
        ]),
        ("Intelligence & Research", [
            ("Articles & News", "/article-blogs"),
            ("Industry Hubs", "/tech-hubs"),
            ("Logistics Terminology", "/tech-dictionary"),
            ("Editor's Picks", "/tag/editors-picks"),
            ("Career Guides", "/tag/guides"),
            ("All Research Tags", "/tag/all"),
        ]),
        ("Member Tools", [
            ("Candidate Profile", "/profile"),
            ("Application Tracker", "/tracker"),
            ("Saved Jobs", "/saved"),
            ("Job Alerts", "/alerts"),
            ("Sign In", "/auth/login"),
            ("Create Account", "/auth/signup"),
        ]),
        ("Employers & Corporate", [
            ("Employer Portal", "/employers"),
            ("Post an Opening", "/employers/post-job"),
            ("Add Company Profile", "/node/add/company"),
            ("About Logistic Waves", "/about"),
            ("Contact Support", "/contact"),
            ("Privacy & Terms", "/terms"),
        ]),
    ]
    cols = ""
    for title, links in columns:
        cols += '<div class="footer-col"><h3>' + e(title) + "</h3><ul>" + "".join(
            f'<li><a href="{e(href)}">{e(label)}</a></li>' for label, href in links
        ) + "</ul></div>"
    return f'''
    <footer class="site-footer">
      <div class="container footer-grid">
        <div class="footer-brand">
          {brand_logo()}
          <p>Connecting top talent with leaders in shipping, multimodal logistics, supply chain tech, and global commerce.</p>
          <div class="footer-social">
            <a href="/about" aria-label="About">{icon("globe", 18)}</a>
            <a href="/contact" aria-label="Contact">{icon("mail", 18)}</a>
            <a href="/article-blogs" aria-label="Articles">{icon("book", 18)}</a>
          </div>
        </div>
        {cols}
      </div>
      <div class="container footer-bottom">
        <span>© 2026 Logistic Waves. All rights reserved.</span>
        <span>The leading intelligence and career hub for logistics, supply chains, and freight forwarding.</span>
        <span><a href="/privacy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/sitemap.xml">Sitemap</a></span>
      </div>
    </footer>'''


def layout(title, body, user=None, active="", description="", page_class="", extra_head=""):
    desc = description or "Logistic Waves \u2014 technology & logistics jobs, employer intelligence, and industry editorial."
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(desc)}">
  <meta name="csrf-token" content="{e(_get_csrf())}">
  <title>{e(title)} | Logistic Waves</title>
  <link rel="icon" type="image/png" href="/static/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/styles.css?v=20261127_wttj_v4">
  <link rel="stylesheet" href="/static/home-recreation.css?v=20261126_apple2">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  {extra_head}
</head>
<body class="{e(page_class)}" data-logged-in="{'true' if user else 'false'}">
  {header(user, active)}
  <main id="main-content">{body}</main>
  {footer()}
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script src="/static/app.js?v=20261126_perf" defer></script>
</body>
</html>'''


# ---------- shared cards ----------

def job_card(job, compact=False):
    saved = bool(job.get("saved"))
    applied = bool(job.get("applied"))
    cid = job["id"]
    accent = job.get("accent") or job.get("company_color") or "#244fe7"
    company = {
        "color": job.get("company_color"), "initials": job.get("company_initials"),
        "name": job.get("company_name"), "slug": job.get("company_slug"),
    }
    salary = job.get("salary_display") or "Competitive"
    description = job.get("description") or ""
    industries = [x.strip() for x in (job.get("industries") or "").split(",") if x.strip()]
    skills = [x.strip() for x in (job.get("skills") or "").split(",") if x.strip()]
    job_url = f'/job/{e(job.get("slug") or "job")}/{cid}'
    compact_cls = " compact" if compact else ""
    applied_badge = '<span class="applied-badge">' + icon("check", 12) + " Applied</span>" if applied else ""
    return f'''
    <article class="job-card{compact_cls}" style="--accent:{e(accent)}" id="job-{cid}">
      <div class="job-card-primary">
        {company_logo(company, 84)}
        <div class="job-card-title">
          <a class="job-company" href="/company/{e(job.get('company_slug'))}">{e(job.get('company_name'))}</a>
          <h3><a href="{job_url}">{e(job.get('title'))}</a></h3>
          {applied_badge}
        </div>
      </div>
      <div class="job-card-meta">
        <span class="meta-chip">{icon("clock", 14)} {e(job.get("posted_label") or "Recently")}</span>
        <span class="meta-item">{icon("briefcase", 14)} {e(job.get("workplace"))}</span>
        <a class="meta-item meta-link" href="{url('/jobs', location=job.get('location'))}">{icon("pin", 14)} {e(job.get("location"))}</a>
      </div>
      <div class="job-card-meta right-meta">
        <span class="meta-item">{icon("money", 14)} {e(salary)}</span>
        <span class="meta-item">{icon("trophy", 14)} {e(job.get("level"))}</span>
      </div>
      <div class="job-card-actions">
        <button class="save-btn{' saved' if saved else ''}" type="button" data-job-id="{cid}" aria-pressed="{'true' if saved else 'false'}" aria-label="Save job" title="Save job">{icon("heart", 22)}</button>
        <details class="job-expand">
          <summary aria-label="Show job details">{icon("chevron", 20)}</summary>
          <div class="job-expand-body">
            <p>{e(description)}</p>
            <div class="tag-row">{''.join(f'<span class="tag">{e(x)}</span>' for x in industries[:6])}</div>
            <p class="skills-line"><strong>Top Skills:</strong> {e(", ".join(skills[:10]))}</p>
            <a class="btn btn-primary btn-sm" href="{job_url}">View Full Job {icon("arrow", 15)}</a>
          </div>
        </details>
      </div>
    </article>'''


_ARTICLE_FALLBACK_COVERS = [
    "/static/images/editorial_laptop_dashboard.jpg",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80",
]


def _article_cover_url(article, idx=0):
    thumb = (article.get("thumb") or "").strip() if article else ""
    safe_t = safe_media_url(thumb)
    if safe_t:
        return safe_t
    return _ARTICLE_FALLBACK_COVERS[idx % len(_ARTICLE_FALLBACK_COVERS)]


def article_card(article, featured=False, variant=0):
    cls = "article-card featured" if featured else "article-card"
    accent = article.get("accent") or "#244fe7"
    thumb = article.get("thumb")
    if thumb:
        photo_html = f'<img src="{e(thumb)}" alt="{e(article["title"])}" style="width:100%;height:100%;object-fit:cover;display:block;border-radius:8px;" loading="lazy">'
    else:
        photo_html = photo_placeholder(accent, "Add your image", article["slug"], variant, 220 if featured else 112)
    return f'''
    <article class="{cls}">
      <a class="article-photo" href="/articles/{e(article['slug'])}">
        {photo_html}
      </a>
      <div class="article-body">
        <a class="article-category" href="{url('/article-blogs', category=article['category'])}">{e(article['category'])}</a>
        <h3><a href="/articles/{e(article['slug'])}">{e(article['title'])}</a></h3>
        <p>{e(article['excerpt'])}</p>
        <div class="article-byline"><span class="author-dot" style="background:{e(accent)}"></span>{e(article['author'])} · {e(article['published'])} · {e(article['read_time'])}</div>
      </div>
    </article>'''


def pagination(path, params, page, pages, total, per_page):
    if pages <= 1:
        return ""
    start = (page - 1) * per_page + 1
    end = min(page * per_page, total)
    links = []
    for p in range(1, pages + 1):
        if p == 1 or p == pages or abs(p - page) <= 2:
            cls = "page-link active" if p == page else "page-link"
            links.append(f'<a class="{cls}" href="{e(url(path, **{**params, "page": p}))}">{p}</a>')
        elif links and links[-1] != '<span class="page-ellipsis">…</span>':
            links.append('<span class="page-ellipsis">…</span>')
    prev = f'<a class="page-link" href="{e(url(path, **{**params, "page": page-1}))}">← Prev</a>' if page > 1 else '<span class="page-link disabled">← Prev</span>'
    nxt = f'<a class="page-link" href="{e(url(path, **{**params, "page": page+1}))}">Next →</a>' if page < pages else '<span class="page-link disabled">Next →</span>'
    return f'''
    <div class="pagination-wrap">
      <span class="pagination-count">Showing {start}–{end} of {thousands(total)}</span>
      <nav class="pagination" aria-label="Pagination">{prev}{''.join(links)}{nxt}</nav>
    </div>'''


def empty_state(title, message, href="/jobs", label="Browse all jobs"):
    return f'''
    <div class="empty-state">
      <div class="empty-icon">{icon("search", 34)}</div>
      <h3>{e(title)}</h3><p>{e(message)}</p>
      <a class="btn btn-primary" href="{e(href)}">{e(label)} {icon("arrow", 16)}</a>
    </div>'''


def signin_required(next_path, title="Sign in to continue"):
    return f'''
    <section class="signin-gate-section">
      <div class="container">
        <div class="auth-card signin-gate-card">
          <div class="auth-gate-badge">
            <div class="auth-icon-wrap">
              <svg class="auth-gate-shield-svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
            </div>
            <span class="auth-gate-pill">MEMBER ACCESS REQUIRED</span>
          </div>

          <h1 class="signin-gate-title">{e(title)}</h1>
          <p class="signin-gate-desc">Sign in to sync your saved tech roles, track job applications with live statuses, customize real-time hiring alerts, or access employer portal tools.</p>

          <div class="signin-gate-perks">
            <div class="gate-perk-item">
              <div class="perk-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
              </div>
              <div class="perk-text">
                <strong>Application Tracker</strong>
                <span>Track interview stages, review notes, and live status updates across all applied jobs</span>
              </div>
            </div>

            <div class="gate-perk-item">
              <div class="perk-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.7-7.5 1.1-1.1a5.5 5.5 0 0 0 0-7.8z"></path>
                </svg>
              </div>
              <div class="perk-text">
                <strong>Saved Jobs & Companies</strong>
                <span>Bookmark top opportunities and follow innovative tech teams to get instant notifications</span>
              </div>
            </div>

            <div class="gate-perk-item">
              <div class="perk-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="1" x2="12" y2="23"></line>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </div>
              <div class="perk-text">
                <strong>Salary Insights & AI Fit</strong>
                <span>Explore verified compensation benchmarks and AI resume skill alignment</span>
              </div>
            </div>
          </div>

          <div class="auth-gate-actions">
            <a class="btn gate-action-btn" href="{url('/auth/login', next=next_path)}">
              Log In with Email
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </a>
            <span class="auth-gate-sep">·</span>
            <a class="btn gate-action-btn" href="{url('/auth/signup', next=next_path)}">
              Create Free Account
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </a>
          </div>


        </div>
      </div>
    </section>'''


# ---------- home ----------

def logistic_waves_today_section(conn):
    import json
    # Dynamically fetch from the backend database (articles with feature 'Logistic Waves Today' or is_today=1)
    db_episodes = conn.execute(
        """SELECT * FROM articles 
           WHERE is_today = 1
              OR tag IN ('Logistic Waves Today', 'Logistic Wave Today')
              OR category IN ('Logistic Waves Today', 'Logistic Wave Today')
           ORDER BY id DESC LIMIT 12"""
    ).fetchall()

    episodes = []
    for r in db_episodes:
        ep = dict(r)
        episodes.append({
            "id": ep["id"],
            "slug": ep.get("slug") or f"article-{ep['id']}",
            "title": ep.get("title") or "Logistic Waves Today",
            "series": "Logistic Waves Today",
            "date": ep.get("published") or "Nov 6, 2026",
            "thumb": ep.get("thumb") or ep.get("accent") or "/static/images/fw_today_1.jpg",
            "excerpt": ep.get("excerpt") or "",
            "duration": ep.get("duration") or ep.get("read_time", "").replace(" watch", "") or "24 min",
            "badge": "DAILY INTELLIGENCE",
            "guest": ep.get("guest") or (ep.get("author") or "Logistic Waves Newsroom").split("·")[0].strip(),
            "author": ep.get("author") or "Logistic Waves Desk",
        })

    cards_html = []
    for ep in episodes:
        art_url = f"/articles/{ep['slug']}"
        cards_html.append(f'''
        <article class="fwt-card" data-episode-id="{ep['id']}">
          <a class="fwt-thumb-wrap" href="{art_url}">
            <img src="{ep['thumb']}" alt="{e(ep['title'])}" class="fwt-thumb-img" width="480" height="270" loading="lazy" decoding="async">
            <div class="fwt-play-btn" aria-hidden="true">
              <i class="fa-solid fa-play"></i>
            </div>
            <button type="button" class="fwt-share-btn" onclick="event.stopPropagation(); shareFwtEpisode('{e(ep['title'])}', '{art_url}');" aria-label="Share episode">
              <i class="fa-solid fa-arrow-up-from-bracket"></i>
            </button>
          </a>
          <div class="fwt-body">
            <span class="fwt-series-tag">{e(ep['series'])}</span>
            <h3 class="fwt-card-title">
              <a href="{art_url}">{e(ep['title'])}</a>
            </h3>
            <span class="fwt-card-date">{e(ep['date'])}</span>
            <p class="fwt-card-excerpt">{e(ep['excerpt'])}</p>
            <a href="{art_url}" class="fwt-read-more-link">Read more...</a>
          </div>
        </article>''')

    episodes_json = json.dumps(episodes)

    return f'''
    <!-- 2.5. Logistic Waves Today Video Showcase (Under Today\'s Picks - Fetched from Backend Database) -->
    <section class="fwt-section" id="freightwaves-today" aria-label="Logistic Waves Today Videos">
      <div class="container">
        <div class="fwt-header-row">
          <div class="fwt-header-title-wrap">
            <h2 class="fwt-header-title">Logistic Waves Today</h2>
            <div class="fwt-header-bar"></div>
          </div>
          <div style="display:flex; align-items:center; gap:16px;">
            <a href="/article-blogs" class="fwt-view-all-link" style="font-size:12.5px; font-weight:700; color:#0066cc; text-decoration:none;">View All in Articles &rarr;</a>
            <div class="fwt-nav-controls">
              <button type="button" class="fwt-nav-btn" data-dir="prev" id="fwtPrevBtn" onclick="scrollFwtTrack(-1);" aria-label="Previous episode">&lt;</button>
              <button type="button" class="fwt-nav-btn" data-dir="next" id="fwtNextBtn" onclick="scrollFwtTrack(1);" aria-label="Next episode">&gt;</button>
            </div>
          </div>
        </div>

        <div class="fwt-track" id="fwtTrack">
          {"".join(cards_html)}
        </div>
      </div>
    </section>

    <!-- Interactive Video Player Modal -->
    <div class="fwt-modal-backdrop" id="fwtModal" style="display: none;" onclick="if(event.target===this)closeFwtModal();" role="dialog" aria-modal="true" aria-labelledby="fwtModalTitle">
      <div class="fwt-modal-card">
        <div class="fwt-modal-header">
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="fwt-badge-pill" id="fwtModalBadge">LIVE BROADCAST</span>
            <h3 class="fwt-modal-title" id="fwtModalTitle">Logistic Waves Broadcast</h3>
          </div>
          <button type="button" class="fwt-modal-close" onclick="closeFwtModal();" aria-label="Close modal">&times;</button>
        </div>
        <div class="fwt-modal-body">
          <div class="fwt-modal-player-box">
            <img src="/static/images/fw_today_1.jpg" id="fwtModalPoster" class="fwt-modal-player-bg" alt="Video poster" width="760" height="428" loading="lazy" decoding="async">
            <div class="fwt-modal-play-overlay">
              <div class="fwt-big-play-btn" onclick="startFwtPreview();" id="fwtModalPlayBtn">
                <i class="fa-solid fa-play"></i>
              </div>
              <span style="font-size:13px; font-weight:600; text-shadow:0 1px 4px rgba(0,0,0,0.8);" id="fwtModalStatus">Click to Stream Episode</span>
            </div>
          </div>
          <div class="fwt-modal-meta-row">
            <span style="font-size:12.5px; color:#64748b;" id="fwtModalDate"></span>
            <span style="color:#cbd5e1;">&bull;</span>
            <span style="font-size:12.5px; color:#64748b;" id="fwtModalDuration"></span>
            <span style="color:#cbd5e1;">&bull;</span>
            <span style="font-size:12.5px; font-weight:600; color:#1e3a8a;" id="fwtModalGuest">Featured Guest</span>
          </div>
          <p class="fwt-modal-desc" id="fwtModalDesc"></p>
          <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #e2e8f0; padding-top:14px; margin-top:14px;">
            <div style="display:flex; align-items:center; gap:14px;">
              <span style="font-size:12px; color:#64748b;">Series: <strong>Logistic Waves Today &bull; Daily Logistics Intelligence</strong></span>
              <a href="/article-blogs" id="fwtModalArticleBtn" class="fwt-read-more-link" style="font-size:12.5px; font-weight:700; color:#0066cc; text-decoration:none;">Open Full Article &rarr;</a>
            </div>
            <button type="button" class="fwt-read-more-link" onclick="shareCurrentModal();" style="display:inline-flex; align-items:center; gap:6px;">
              <i class="fa-solid fa-share-nodes"></i> Share Episode
            </button>
          </div>
        </div>
      </div>
    </div>

    <script>
      (function() {{
        const FWT_DATA = {episodes_json};
        let activeFwtId = 1;

        window.scrollFwtTrack = function(direction) {{
          const track = document.getElementById('fwtTrack');
          if (!track) return;
          const scrollDistance = track.clientWidth * 0.75;
          track.scrollBy({{ left: direction * scrollDistance, behavior: 'smooth' }});
        }};

        window.openFwtModal = function(id) {{
          const ep = FWT_DATA.find(x => x.id === id) || FWT_DATA[0];
          if (!ep) return;
          activeFwtId = ep.id;
          document.getElementById('fwtModalTitle').textContent = ep.title;
          document.getElementById('fwtModalBadge').textContent = ep.badge || 'SPECIAL EPISODE';
          document.getElementById('fwtModalPoster').src = ep.thumb;
          document.getElementById('fwtModalDate').textContent = ep.date;
          document.getElementById('fwtModalDuration').textContent = ep.duration;
          document.getElementById('fwtModalGuest').textContent = ep.guest || 'Featured Analyst';
          document.getElementById('fwtModalDesc').textContent = ep.excerpt + ' In this in-depth executive briefing, industry leaders examine supply chain resilience, commercial market momentum, and next-generation freight technologies.';
          
          const artBtn = document.getElementById('fwtModalArticleBtn');
          if (artBtn) artBtn.href = '/articles/' + ep.slug;

          const modal = document.getElementById('fwtModal');
          if (modal) modal.style.display = 'flex';
          document.body.style.overflow = 'hidden';
        }};

        window.closeFwtModal = function() {{
          const modal = document.getElementById('fwtModal');
          if (modal) modal.style.display = 'none';
          document.body.style.overflow = '';
        }};

        window.startFwtPreview = function() {{
          const status = document.getElementById('fwtModalStatus');
          const btn = document.getElementById('fwtModalPlayBtn');
          if (status) status.textContent = 'Buffering live high-definition stream...';
          if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
          setTimeout(() => {{
            if (status) status.textContent = 'Streaming Broadcast (00:01 / ' + (FWT_DATA.find(x => x.id === activeFwtId)?.duration || '24:00') + ')';
            if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i>';
            if (typeof showToast === 'function') showToast('Streaming preview started.');
          }}, 700);
        }};

        window.shareFwtEpisode = function(title, url) {{
          const shareUrl = url ? (window.location.origin + url) : (window.location.origin + '/#freightwaves-today');
          if (navigator.clipboard) {{
            navigator.clipboard.writeText(shareUrl).then(() => {{
              if (typeof showToast === 'function') showToast('Article link copied to clipboard!');
            }});
          }} else {{
            if (typeof showToast === 'function') showToast('Article: ' + title);
          }}
        }};

        window.shareCurrentModal = function() {{
          const ep = FWT_DATA.find(x => x.id === activeFwtId);
          shareFwtEpisode(ep ? ep.title : 'Logistic Waves Today', ep ? ('/articles/' + ep.slug) : '');
        }};
      }})();
    </script>
    '''

def home_page(conn, user):
    def _load_home_core():
        return (
            db.counts(conn),
            [db.as_dict(r) for r in conn.execute(
                "SELECT * FROM jobs WHERE status='active' ORDER BY id ASC LIMIT 9"
            ).fetchall()],
            [db.as_dict(r) for r in conn.execute(
                "SELECT * FROM companies ORDER BY open_jobs DESC"
            ).fetchall()],
            [db.as_dict(r) for r in conn.execute(
                "SELECT * FROM jobs WHERE status='active' ORDER BY id DESC LIMIT 6"
            ).fetchall()],
        )
    c, best_jobs, dir_companies, opp_jobs = db.cached_query("home_core", 60, _load_home_core)

    # 3x3 Best Jobs Cards
    best_jobs_html = []
    for j in best_jobs:
        company_slug = j.get("company_slug") or "company"
        company_name = j.get("company_name") or "Company"
        logo_markup = _brand_logo_markup(company_slug, company_name, initials=j.get("company_initials") or "CO", color=j.get("company_color") or "#003366")

        best_jobs_html.append(f'''
        <a href="/job/{e(j.get('slug') or 'job')}/{j['id']}" class="best-job-card">
          <div class="best-job-top">
            <div class="best-job-logo">{logo_markup}</div>
            <div>
              <h3 class="best-job-role-title">{e(j['title'])}</h3>
              <div class="best-job-company-name">
                <span>{e(company_name)}</span>
                <i class="fa-solid fa-circle-check" style="font-size: 11px; color: var(--blue);"></i>
              </div>
            </div>
          </div>
          <div class="best-job-salary">{e(j.get('salary_display') or 'Competitive')}</div>
          <div class="best-job-footer">
            <span class="best-job-pill">{e(j.get('workplace') or 'Hybrid')} &bull; {e(j.get('location') or 'Remote')}</span>
            <span class="best-job-action">View Details &rarr;</span>
          </div>
        </a>''')

    # Welcome-to-the-Jungle Style Company Showcase Cards
    followed_ids = db.followed_company_ids(conn, user["id"]) if user else set()
    tech_covers = [
        "/static/images/arch_office_team.jpg",
        "/static/images/arch_glass_office.jpg",
        "/static/images/arch_modern_2.jpg",
        "/static/images/glass_arch_2.jpg",
        "/static/images/glass_tower_1.jpg",
        "/static/images/arch_glass_tower.jpg",
    ]
    maritime_covers = [
        "/static/images/port_logistics_1.jpg",
        "/static/images/port_logistics_2.jpg",
        "/static/images/port_logistics_3.jpg",
        "/static/images/arch_glass_tower.jpg",
    ]
    cat_rules = [
        ("maritime", ("logistics", "maritime", "port", "freight", "supply chain", "ocean")),
        ("ai", ("artificial intelligence", "machine learning")),
        ("cloud", ("cloud",)),
        ("fintech", ("fintech", "financial", "payments")),
        ("security", ("security", "cybersecurity")),
        ("media", ("design", "media", "music", "gaming")),
    ]

    def _emp_range_label(emp):
        if not emp:
            return "250 to 2,000 employees"
        if emp > 2000:
            return "> 2,000 employees"
        if emp >= 250:
            return "250 to 2,000 employees"
        if emp >= 50:
            return "50 to 250 employees"
        if emp >= 15:
            return "15 to 50 employees"
        return "< 15 employees"

    dir_rows_html = []
    for idx, comp in enumerate(dir_companies):
        c_slug = comp["slug"]
        c_name = comp["name"]
        cid = comp["id"]
        logo_markup = _brand_logo_markup(
            c_slug, c_name,
            initials=comp.get("initials") or "CO",
            color=comp.get("color") or "#003366",
            size=72,
        )
        badge_cls = "wttj-logo-badge has-svg" if "<img " in logo_markup else "wttj-logo-badge"
        raw_ind = (comp.get("industries") or "").strip()
        ind_text = ", ".join(x.strip() for x in raw_ind.split(",") if x.strip()) or "Logistics & Technology"
        ind_lower = raw_ind.lower()
        cat_tokens = ["all"] + [k for k, words in cat_rules if any(w in ind_lower for w in words)]
        is_maritime = "maritime" in cat_tokens
        cover_url = maritime_covers[idx % len(maritime_covers)] if is_maritime else tech_covers[idx % len(tech_covers)]
        loc_text = (comp.get("location") or "Global / Remote").strip()
        emp_text = _emp_range_label(comp.get("employees"))
        open_n = comp.get("open_jobs") or 0
        jobs_text = f"{open_n} open role{'s' if open_n != 1 else ''}" if open_n > 0 else "Open applications"
        is_fol = cid in followed_ids

        dir_rows_html.append(f'''
        <article class="wttj-card" data-cats="{e(' '.join(cat_tokens))}">
          <a href="/company/{e(c_slug)}" class="wttj-cover-link">
            <img src="{cover_url}" alt="{e(c_name)} workplace" class="wttj-cover-img" width="900" height="600" loading="lazy" decoding="async">
          </a>
          <a href="/company/{e(c_slug)}" class="{badge_cls}" aria-label="{e(c_name)}">
            {logo_markup}
          </a>
          <div class="wttj-card-body">
            <h3 class="wttj-name">
              <a href="/company/{e(c_slug)}">{e(c_name)}</a>
            </h3>
            <div class="wttj-meta-list">
              <div class="wttj-meta-row" title="{e(ind_text)}">
                <i class="fa-solid fa-tag" aria-hidden="true"></i>
                <span>{e(ind_text)}</span>
              </div>
              <div class="wttj-meta-row" title="{e(loc_text)}">
                <i class="fa-solid fa-location-dot" aria-hidden="true"></i>
                <span>{e(loc_text)}</span>
              </div>
              <div class="wttj-meta-row">
                <i class="fa-solid fa-user-group" aria-hidden="true"></i>
                <span>{e(emp_text)}</span>
              </div>
            </div>
            <div class="wttj-footer">
              <a href="/company/{e(c_slug)}/jobs" class="wttj-jobs-link">{e(jobs_text)}</a>
              <button type="button" class="wttj-follow-btn li-btn follow-btn{' followed' if is_fol else ''}" data-company-id="{cid}" aria-pressed="{'true' if is_fol else 'false'}">
                <span>{'Following' if is_fol else 'Follow'}</span>
              </button>
            </div>
          </div>
        </article>''')

    wttj_tabs = [
        ("all", "Discover"),
        ("maritime", "Logistics & Maritime"),
        ("ai", "Artificial Intelligence"),
        ("cloud", "Cloud"),
        ("fintech", "Fintech"),
        ("security", "Cybersecurity"),
        ("media", "Design & Media"),
    ]
    wttj_tabs_html = "".join(
        f'<button type="button" class="wttj-tab{" active" if i == 0 else ""}" role="tab" '
        f'aria-selected="{"true" if i == 0 else "false"}" '
        f'onclick="filterWttjCompanies(\'{k}\', this)">{e(label)}</button>'
        for i, (k, label) in enumerate(wttj_tabs)
    )

    # Latest Opportunities Cards
    opp_cards_html = []
    opp_covers = [
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
    ]
    for idx, opp in enumerate(opp_jobs):
        o_slug = opp.get("company_slug") or "company"
        o_name = opp.get("company_name") or "Company"
        cover_img = opp_covers[idx % len(opp_covers)]
        logo_markup = _brand_logo_markup(o_slug, o_name, initials=opp.get("company_initials") or "CO", color=opp.get("company_color") or "#003366")

        opp_cards_html.append(f'''
        <article class="opp-card">
          <div class="opp-card-cover">
            <img src="{cover_img}" alt="{e(opp['title'])}" width="800" height="364" loading="lazy" decoding="async">
          </div>
          <div class="opp-card-body">
            <div class="opp-card-head">
              <div class="opp-company-logo">{logo_markup}</div>
              <div class="opp-company-name">
                <span>{e(o_name)}</span>
                <i class="fa-solid fa-circle-check" style="font-size: 11px; color: var(--blue);"></i>
              </div>
            </div>
            <h4 class="opp-job-title">
              <a href="/job/{e(opp.get('slug') or 'job')}/{opp['id']}">{e(opp['title'])}</a>
            </h4>
            <div class="opp-card-meta">
              <span><i class="fa-solid fa-location-dot"></i> {e(opp.get('location') or 'Remote')}</span>
              <span>&bull;</span>
              <span>{e(opp.get('workplace') or 'Hybrid')}</span>
            </div>
            <div class="opp-salary-badge">{e(opp.get('salary_display') or 'Competitive')}</div>
            <a href="/job/{e(opp.get('slug') or 'job')}/{opp['id']}" class="opp-apply-btn">
              View Details &amp; Apply &rarr;
            </a>
          </div>
        </article>''')

    body = f"""
    <!-- 1. Enterprise Hero: Insights for Smarter Logistics (HD Photographic Smoke-White Master Composition) -->
    <section class="lw-hero-banner-section smoke-white-hero">
      <div class="hero-shell">
        <div class="hero-photo-hd" aria-hidden="true"></div>
        <div class="hero-smoke-overlay" aria-hidden="true"></div>

        <div class="hero-inner-wrap">
          <div class="hero-content">
            <h1 class="hero-headline-smoke">
              Insights for<br>
              <span class="hero-hl-blue">Smarter</span> Logistics
            </h1>
            
            <p class="hero-subtitle-smoke">
              Industry briefings, supply chain intelligence, and active career opportunities across logistics and technology.
            </p>
            
            <div class="hero-actions">
              <a class="hero-btn-primary" href="/article-blogs">
                Explore Insights
              </a>
              <a class="hero-btn-secondary" href="#overview" onclick="openFwtModal(0); return false;" aria-label="Watch Overview Video">
                Watch Overview
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>"""

    editorial_articles = db.cached_query(
        "home_editorial_v2",
        60,
        lambda: [db.as_dict(r) for r in conn.execute(
            """SELECT * FROM articles
               ORDER BY CASE WHEN COALESCE(is_today, 0) = 0 THEN 0 ELSE 1 END ASC, id DESC
               LIMIT 8"""
        ).fetchall()],
    )
    _ed_img = _article_cover_url

    if editorial_articles:
        lead_art = editorial_articles[0]
        stacked_arts = editorial_articles[1:3]
        recent_arts = editorial_articles[:5]
        stacked_html = "".join(f'''
                <article class="stacked-story">
                  <a href="/articles/{e(a['slug'])}" class="stacked-img-wrap">
                    <img src="{e(_ed_img(a, i + 1))}" alt="{e(a['title'])}" width="400" height="225" loading="lazy" decoding="async">
                  </a>
                  <span class="article-kicker">{e((a.get('category') or 'EDITORIAL').upper())}</span>
                  <h3 class="stacked-title">
                    <a href="/articles/{e(a['slug'])}">{e(a['title'])}</a>
                  </h3>
                  <span class="article-author-tag">{e((a.get('author') or 'Editorial Staff').upper())}</span>
                </article>''' for i, a in enumerate(stacked_arts))
        lead_html = f'''
              <article class="article-lead-card">
                <a href="/articles/{e(lead_art['slug'])}" class="article-lead-img-wrap">
                  <img src="{e(_ed_img(lead_art, 0))}" alt="{e(lead_art['title'])}" width="720" height="405" loading="lazy" decoding="async">
                </a>
                <div class="article-lead-content">
                  <span class="article-kicker">{e((lead_art.get('tag') or lead_art.get('category') or 'FEATURED').upper())}</span>
                  <h2 class="article-lead-title">
                    <a href="/articles/{e(lead_art['slug'])}">{e(lead_art['title'])}</a>
                  </h2>
                  <p class="article-lead-excerpt">{e(lead_art.get('excerpt') or '')}</p>
                  <span class="article-author-tag">{e((lead_art.get('author') or 'Editorial Staff').upper())}</span>
                </div>
              </article>'''
        recent_html = "".join(f'''
              <a href="/articles/{e(a['slug'])}" class="recent-row-item">
                <div class="recent-row-left">
                  <span class="article-kicker" style="font-size: 10px;">{e((a.get('category') or 'NEWS').upper())}</span>
                  <h4 class="recent-row-title">{e(a['title'])}</h4>
                  <span class="article-author-tag" style="font-size: 9.5px;">{e((a.get('author') or 'Editorial Staff').upper())}</span>
                </div>
                <img src="{e(_ed_img(a, i))}" class="recent-thumb-img" alt="{e(a['title'])}" width="96" height="68" loading="lazy" decoding="async">
              </a>''' for i, a in enumerate(recent_arts))
        picks_inner_html = f'''
            <div class="todays-picks-layout">
              <div class="todays-picks-stacked">{stacked_html}</div>
              {lead_html}
            </div>'''
    else:
        picks_inner_html = empty_state("No editorial articles published yet", "Publish an article from the admin dashboard to feature it here.", "/article-blogs", "Explore Intelligence Hub")
        recent_html = '<p style="color:#64748b;font-size:13px;">No recent articles yet.</p>'

    body += f"""
    <!-- 2. Editorial Showcase: Today's Picks & Most Recent -->
    <section class="home-editorial-section">
      <div class="container">
        <div class="editorial-grid-12">
          
          <!-- Left 8 Columns: Today's Picks -->
          <div>
            <div class="editorial-sec-header">
              <span class="editorial-sec-title">TODAY'S PICKS</span>
              <span class="editorial-dot"></span>
            </div>
            {picks_inner_html}
          </div>

          <!-- Right 4 Columns: Most Recent -->
          <div>
            <div class="editorial-sec-header">
              <span class="editorial-sec-title">MOST RECENT</span>
              <span class="editorial-dot"></span>
            </div>
            <div class="most-recent-list">
              {recent_html}
            </div>
          </div>

        </div>
      </div>
    </section>

    {logistic_waves_today_section(conn)}

    <!-- 3. Best Tech & Engineering Jobs Showcase (3x3 Grid) -->
    <section class="home-best-jobs-section">
      <div class="container">
        <div class="best-jobs-header-row">
          <div class="best-jobs-title-wrap">
            <h2 class="best-jobs-title">Best Tech &amp; Engineering Jobs</h2>
            <span class="flame-pill"><i class="fa-solid fa-fire"></i> High Demand</span>
          </div>
          <a href="/jobs" class="subnav-explore-btn" style="font-size: 13px;">View All {c['jobs']} Jobs &rarr;</a>
        </div>
        <div class="best-jobs-grid-3x3">
          {"".join(best_jobs_html)}
        </div>
      </div>
    </section>

    <!-- 4 & 5. Company Showcase — replaces LATEST OPPORTUNITIES, white bg, sector tabs -->
    <section class="home-opportunities-section home-companies-wttj" id="companies-directory">
      <div class="container">
        <div class="fwt-header-row">
          <div class="fwt-header-title-wrap">
            <h2 class="fwt-header-title">Companies</h2>
            <div class="fwt-header-bar"></div>
          </div>
          <div style="display:flex; align-items:center; gap:16px;">
            <a href="/companies" class="fwt-view-all-link" style="font-size:12.5px; font-weight:700; color:#0066cc; text-decoration:none;">View All Companies &rarr;</a>
            <div class="fwt-nav-controls">
              <button type="button" class="fwt-nav-btn" onclick="scrollWttjCarousel(-1);" aria-label="Previous">&lt;</button>
              <button type="button" class="fwt-nav-btn" onclick="scrollWttjCarousel(1);" aria-label="Next">&gt;</button>
            </div>
          </div>
        </div>
        <div class="wttj-tabs-wrap">
          <div class="wttj-tabs" role="tablist" aria-label="Filter companies by sector">
            {wttj_tabs_html}
          </div>
        </div>
        <div class="wttj-carousel-shell">
          <button type="button" class="wttj-nav-btn wttj-nav-prev is-hidden" id="wttjPrevBtn" onclick="scrollWttjCarousel(-1);" aria-label="Previous companies">
            <i class="fa-solid fa-chevron-left" aria-hidden="true"></i>
          </button>
          <div class="wttj-carousel-track" id="wttj-track" onscroll="updateWttjNav();">
            {"".join(dir_rows_html)}
          </div>
          <button type="button" class="wttj-nav-btn wttj-nav-next" id="wttjNextBtn" onclick="scrollWttjCarousel(1);" aria-label="Next companies">
            <i class="fa-solid fa-chevron-right" aria-hidden="true"></i>
          </button>
        </div>
        <div class="wttj-section-foot">
          <a href="/companies" class="wttj-all-link">Explore all {c['companies']} companies &rarr;</a>
        </div>
      </div>
    </section>

    <script>
      function filterWttjCompanies(cat, btn) {{
        document.querySelectorAll('.wttj-tab').forEach(t => {{
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        }});
        if (btn) {{
          btn.classList.add('active');
          btn.setAttribute('aria-selected', 'true');
        }}
        const track = document.getElementById('wttj-track');
        if (!track) return;
        track.querySelectorAll('.wttj-card').forEach(card => {{
          const cats = (card.getAttribute('data-cats') || '').split(/\\s+/);
          card.style.display = (cat === 'all' || cats.includes(cat)) ? 'flex' : 'none';
        }});
        track.scrollTo({{ left: 0, behavior: 'auto' }});
        updateWttjNav();
      }}

      function updateWttjNav() {{
        const track = document.getElementById('wttj-track');
        const prev = document.getElementById('wttjPrevBtn');
        const next = document.getElementById('wttjNextBtn');
        if (!track) return;
        const maxScroll = track.scrollWidth - track.clientWidth;
        if (prev) prev.classList.toggle('is-hidden', track.scrollLeft <= 8);
        if (next) next.classList.toggle('is-hidden', maxScroll <= 8 || track.scrollLeft >= maxScroll - 8);
      }}

      function scrollWttjCarousel(dir) {{
        const track = document.getElementById('wttj-track');
        if (track) {{
          track.scrollBy({{ left: dir * 350, behavior: 'smooth' }});
          setTimeout(updateWttjNav, 320);
        }}
      }}
      window.addEventListener('resize', updateWttjNav);
      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', updateWttjNav);
      }} else {{
        updateWttjNav();
      }}

      function scrollOppTrack(dir) {{
        const track = document.getElementById('opp-track');
        if (track) {{
          track.scrollBy({{ left: dir * 360, behavior: 'smooth' }});
        }}
      }}
    </script>
    """

    extra_head = ""
    return layout("Logistic Waves | Logistics, Supply Chain & Tech Jobs Hub", body, user, active="home",
                  page_class="page-home",
                  description="Everything for your next move in tech: high-concurrency engineering roles, company insights, and editorial intelligence.",
                  extra_head=extra_head)




# ---------- jobs ----------

def jobs_page(conn, user, f, jobs, total, page, pages, heading=None):
    q = f.get("q", "")
    params = {k: v for k, v in f.items() if v not in (None, "", False, 0)}
    heading = heading or "Top Tech Jobs & Startup Jobs"
    remote_on = f.get("remote") in ("1", "true", True, 1)
    filters_json = e(json.dumps({k: v for k, v in f.items() if v not in (None, "", False, 0)}))
    cards = "".join(job_card(j) for j in jobs) or empty_state(
        "No jobs match those filters", "Try clearing a filter or searching a different keyword.", "/jobs", "Reset job search"
    )
    category_options = seed.CATEGORIES
    body = f'''
    <section class="search-hero">
      <div class="container">
        <form class="job-search-form" id="jobsFilterForm" method="get" action="/jobs">
          <div class="search-input-wrap">
            <input type="search" name="q" value="{e(q)}" placeholder="Job Title, Company or Keyword" aria-label="Job title, company or keyword">
            <button class="search-submit" type="submit" aria-label="Search jobs">{icon("search", 20)}</button>
          </div>
          <div class="select-wrap">{icon("briefcase", 18)}{select("workplace", ["Fully Remote", "Hybrid", "On Site", "Remote or Hybrid"], f.get("workplace", ""), "Remote / Hybrid", "auto-submit")}{icon("chevron", 16, "select-caret")}</div>
          <div class="location-wrap">{icon("pin", 18)}<input type="text" name="location" value="{e(f.get('location',''))}" placeholder="USA" aria-label="Location"></div>
          <div class="filter-pills">
            <div class="pill-select">{icon("filter", 15)}{select("posted", [("24h","Past 24 hours"),("3d","Past 3 days"),("week","Past week"),("month","Past month")], f.get("posted",""), "New Jobs", "auto-submit")}</div>
            <div class="pill-select">{select("category", category_options, f.get("category",""), "Job Category", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
            <div class="pill-select">{select("level", seed.LEVELS, f.get("level",""), "Experience", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
            <div class="pill-select">{select("industry", seed.INDUSTRIES, f.get("industry",""), "Industry", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
            <details class="all-filters"><summary>{icon("filter", 15)} All Filters</summary>
              <div class="all-filters-body">
                <label>Sort by {select("sort", [("newest","Newest first"),("salary_high","Highest salary"),("salary_low","Lowest salary"),("title","Title A–Z")], f.get("sort",""), "", "auto-submit")}</label>
                <label class="check-line"><input type="checkbox" name="remote" value="1" {'checked' if remote_on else ''} class="auto-submit"> Remote only</label>
                <button class="btn btn-primary btn-sm" type="submit">Apply Filters</button>
                <a class="text-link" href="/jobs">Clear all</a>
              </div>
            </details>
            <a class="text-link reset-link" href="/jobs">Reset</a>
            <button class="btn btn-outline save-alert-btn" type="button" id="saveAlertBtn" data-query="{e(q)}" data-filters="{filters_json}">{icon("bell", 16)} SAVE JOB ALERT</button>
          </div>
        </form>
      </div>
    </section>
    <section class="results-section"><div class="container">
      <div class="results-head"><div><h1>{e(heading)}</h1><p>{thousands(total)} open positions matching your search</p></div><span class="results-count">{thousands(total)} results</span></div>
      <div class="job-list">{cards}</div>
      {pagination('/jobs', params, page, pages, total, 12)}
    </div></section>
    <div class="modal" id="alertModal" hidden>
      <div class="modal-backdrop" data-close-modal></div>
      <div class="modal-card">
        <button class="icon-btn modal-close" type="button" data-close-modal aria-label="Close">{icon("close", 20)}</button>
        <h2>Save Job Alert</h2><p>Get notified when matching jobs are added.</p>
        <form id="alertForm">
          <label>Alert name<input name="query" value="{e(q or 'My job search')}" required></label>
          <label>Frequency {select("frequency", ["Daily", "Weekly", "Monthly"], "Daily", "", "")}</label>
          <input type="hidden" name="filters" value="{filters_json}">
          <button class="btn btn-primary btn-block" type="submit">Create Alert</button>
        </form>
      </div>
    </div>'''
    return layout(heading, body, user, active="jobs", page_class="jobs-page", description=f"Browse {total} tech jobs with filters for category, experience, workplace and location.")


# ---------- companies ----------

def companies_page(conn, user, f, companies, total, page, pages, heading=None):
    heading = heading or "Top Tech Companies"
    params = {k: v for k, v in f.items() if v not in (None, "", False, 0)}
    cards = "".join(linkedin_company_card(c, conn, user, variant=i) for i, c in enumerate(companies)) or empty_state(
        "No companies found", "Try a different location, industry or company size.", "/companies", "Reset company search"
    )
    sizes = ["1 - 10 Employees", "11 - 50 Employees", "51 - 200 Employees", "201 - 500 Employees", "501 - 1000 Employees", "1000+ Employees"]
    body = f'''
    <section class="search-hero companies-hero"><div class="container">
      <h1>Explore top tech companies</h1>
      <form class="company-search-form" method="get" action="/companies">
        <div class="location-wrap large">{icon("pin", 19)}<input type="text" name="q" value="{e(f.get('q',''))}" placeholder="Company name, industry or keyword" aria-label="Search companies"><button class="locate-btn" type="button" title="Use United States">{icon("pin", 18)}</button></div>
        <div class="pill-select">{select("office_type", ["Hybrid", "On-site", "Fully Remote"], f.get("office_type",""), "Office Type", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
        <div class="pill-select">{select("industry", seed.INDUSTRIES, f.get("industry",""), "Industry", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
        <div class="pill-select">{select("size", sizes, f.get("size",""), "Company Size", "auto-submit")}{icon("chevron", 14, "select-caret")}</div>
        <details class="all-filters"><summary>{icon("filter", 15)} All Filters</summary>
          <div class="all-filters-body">
            <label class="check-line"><input class="auto-submit" type="checkbox" name="hiring" value="1" {'checked' if f.get('hiring') in ('1','true',True,1) else ''}> Has open jobs</label>
            <label class="check-line"><input class="auto-submit" type="checkbox" name="remote" value="1" {'checked' if f.get('remote') in ('1','true',True,1) else ''}> Remote-friendly</label>
            <button class="btn btn-primary btn-sm" type="submit">Apply Filters</button><a class="text-link" href="/companies">Clear all</a>
          </div>
        </details>
        <button class="btn btn-magenta search-company-btn" type="submit">{icon("search", 18)}</button>
        <a class="text-link reset-link" href="/companies">Reset</a>
      </form>
    </div></section>
    <section class="results-section"><div class="container">
      <div class="results-head"><div><h2>{e(heading)} <span class="light-count">({thousands(total)}+)</span></h2><p>Research culture, benefits, teams and open roles.</p></div>
        <a class="btn btn-outline" href="/employers/post-job">{icon("plus", 16)} ADD COMPANY PROFILE</a></div>
      <div class="company-list">{cards}</div>
      {pagination('/companies', params, page, pages, total, 8)}
    </div></section>'''
    return layout(heading, body, user, active="companies", page_class="companies-page linkedin-style", description="Research top tech companies, benefits, culture and open jobs.")


TABS = [
    ("Overview", ""), ("Jobs", "jobs"), ("People", "people"), ("Posts", "posts"),
    ("Insights", "insights"), ("Offices", "offices"), ("Culture", "culture"),
    ("Perks + Benefits", "benefits"),
    # Legacy route keys kept so existing links keep working; hidden from the tab bar.
    ("Teams", "teams"), ("Articles", "articles"),
    ("Company Insights", "faq/workplace-perception"),
]

LI_TABS = [
    ("Overview", ""), ("Jobs", "jobs"), ("People", "people"), ("Posts", "posts"),
    ("Insights", "insights"), ("Offices", "offices"), ("Culture", "culture"),
    ("Perks + Benefits", "benefits"),
]

TAB_ALIASES = {"teams": "people", "articles": "posts"}


def canonical_tab(tab):
    if tab.startswith("faq/"):
        return "insights"
    return TAB_ALIASES.get(tab, tab)


# ---------- LinkedIn-style company & job views ----------

def linkedin_company_card(company, conn, user=None, breakdown=None, variant=0):
    followed = bool(company.get("followed"))
    cid = company["id"]
    breakdown = breakdown if breakdown is not None else db.company_job_breakdown(conn, company["slug"])
    industries = [x.strip() for x in (company.get("industries") or "").split(",") if x.strip()]
    open_jobs = company.get("open_jobs") or 0
    chips = "".join(
        f'<a class="li-chip" href="{url("/jobs", company_slug=company["slug"], category=b["category"])}">{e(b["category"])} · {b["n"]}</a>'
        for b in breakdown[:3]
    ) or '<span class="li-muted">Explore open roles</span>'
    return f'''
    <article class="li-card li-company-card" id="company-{cid}">
      <div class="li-company-top">
        <a class="li-avatar-link" href="/company/{e(company['slug'])}">{company_logo(company, 84, 'li-avatar')}</a>
        <div class="li-company-ident">
          <a class="li-company-name" href="/company/{e(company['slug'])}">{e(company['name'])}</a>
          <p class="li-company-tagline">{e(company['tagline'])}</p>
          <div class="li-meta">{" · ".join(e(x) for x in industries[:3])} · {e(company['location'])} · {thousands(company['employees'])} employees</div>
        </div>
        <button class="li-btn li-btn-outline li-follow-btn follow-btn{' followed' if followed else ''}" type="button" data-company-id="{cid}" aria-pressed="{'true' if followed else 'false'}">
          {icon("plus", 16)} <span>{'Following' if followed else 'Follow'}</span>
        </button>
      </div>
      <p class="li-company-desc">{e(company['description'])}</p>
      <div class="li-company-foot">
        <div class="li-chip-row">{chips}</div>
        <a class="li-link" href="/company/{e(company['slug'])}/jobs">{thousands(open_jobs)} jobs {icon("arrow", 14)}</a>
      </div>
      <div class="li-card-actions">
        <a class="li-link" href="/company/{e(company['slug'])}">View profile {icon("arrow", 14)}</a>
        <a class="li-link" href="{url('/alerts', company=company['slug'])}">{icon("bell", 14)} Create job alert</a>
      </div>
    </article>'''


def linkedin_job_card(job, compact=False):
    saved = bool(job.get("saved"))
    applied = bool(job.get("applied"))
    cid = job["id"]
    company = {
        "color": job.get("company_color"), "initials": job.get("company_initials"),
        "name": job.get("company_name"), "slug": job.get("company_slug"),
    }
    job_url = f'/job/{e(job.get("slug") or "job")}/{cid}'
    salary = job.get("salary_display") or "Competitive"
    applied_badge = f'<span class="li-applied">{icon("check", 12)} Applied</span>' if applied else ""
    return f'''
    <article class="li-job-card{' compact' if compact else ''}" id="job-{cid}">
      <a class="li-avatar-link" href="/company/{e(job['company_slug'])}">{company_logo(company, 84, 'li-avatar')}</a>
      <div class="li-job-body">
        <a class="li-job-title" href="{job_url}">{e(job['title'])}</a>
        <a class="li-job-company" href="/company/{e(job['company_slug'])}">{e(job['company_name'])}</a>
        <div class="li-meta">{e(job['location'])} · {e(job['workplace'])} · {e(job['posted_label'] or 'Recently')}</div>
        <div class="li-job-tags"><span>{e(salary)}</span><span>{e(job['level'])}</span>{applied_badge}</div>
      </div>
      <button class="save-btn li-save-btn{' saved' if saved else ''}" type="button" data-job-id="{cid}" aria-pressed="{'true' if saved else 'false'}" aria-label="Save job">{icon("heart", 21)}</button>
    </article>'''


def _li_office_grid(company):
    offices = [(company["location"], "Headquarters")]
    office_cnt = int(company.get("offices") or 1)
    if office_cnt > 1:
        offices.append((f"{office_cnt} Locations", "Regional & Global Offices"))
    policy = company.get("remote_policy") or company.get("office_type") or "Hybrid"
    offices.append((policy, "Workplace Policy"))
    return '<div class="li-office-grid">' + "".join(
        f'''<div class="li-office">{icon("building", 20)}<div><strong>{e(name)}</strong><span>{e(kind)}</span><small>{e(company['office_type'])} workplace</small></div></div>'''
        for name, kind in offices
    ) + "</div>"


def _li_culture_grid(company):
    return f'''<div class="li-culture-grid">
      <div>{icon("globe", 22)}<strong>How we work</strong><p>{e(company['office_type'])} teams use documented decisions, async updates and regular feedback loops.</p></div>
      <div>{icon("users", 22)}<strong>Growth</strong><p>Mentorship, internal mobility and learning stipends help people build durable careers.</p></div>
      <div>{icon("lightning", 22)}<strong>Impact</strong><p>Small teams own meaningful problems from discovery through launch and iteration.</p></div>
    </div>'''


def _li_faq_items(company):
    items = [
        ("What's It Like to Work Here?", "Teams describe a collaborative, documented and outcomes-focused environment."),
        ("Culture & Values", "Curiosity, ownership and clear communication show up in everyday rituals."),
        ("Inclusion & Diversity", "Employee resource groups, pay transparency and inclusive hiring practices are part of the profile."),
        ("Career Growth & Development", "Learning stipends, mentorship and internal mobility support long-term growth."),
        ("Compensation & Benefits", "Competitive pay, equity or bonus programs, health coverage and retirement benefits."),
        ("Work-Life Balance", "Flexible schedules and a {office_type} policy help people do their best work."),
    ]
    return "".join(
        f'<details class="li-faq" {"open" if i == 0 else ""}><summary>{e(q)} {icon("chevron", 17)}</summary><p>{e(a.format(office_type=company["office_type"]))}</p></details>'
        for i, (q, a) in enumerate(items)
    )


def linkedin_company_detail_page(conn, user, company, tab, jobs=None, related=None):
    active = canonical_tab(tab)
    cid = company["id"]
    followed = bool(user and cid in db.followed_company_ids(conn, user["id"]))
    industries = [x.strip() for x in (company.get("industries") or "").split(",") if x.strip()]
    perks = [x.strip() for x in (company.get("perks") or "").split(",") if x.strip()]
    stack = [x.strip() for x in (company.get("tech_stack") or "").split(",") if x.strip()]
    teams = [x.strip() for x in (company.get("teams") or "").split(",") if x.strip()]
    breakdown = db.company_job_breakdown(conn, company["slug"])
    jobs = jobs if jobs is not None else db.jobs_for_company(conn, company["slug"], 12)
    related = related if related is not None else db.list_articles(conn, limit=3)
    similar = [dict(r) for r in conn.execute(
        "SELECT * FROM companies WHERE slug<>? ORDER BY open_jobs DESC LIMIT 4", (company["slug"],)
    ).fetchall()]

    tabs = "".join(
        f'<a class="li-tab{' active' if active == key else ''}" href="/company/{e(company['slug'])}{'/' + key if key else ''}">{e(label)}{' <span class="li-tab-count">' + str(company['open_jobs']) + '</span>' if key == 'jobs' else ''}</a>'
        for label, key in LI_TABS
    )
    team_cards = "".join(
        f'<a class="li-team" href="{url("/jobs", company_slug=company['slug'], category=b['category'])}"><strong>{e(b['category'])}</strong><span>{b['n']} open roles</span>{icon("arrow", 17)}</a>'
        for b in breakdown
    ) or '<p class="li-muted">No open roles right now.</p>'
    chips = "".join(
        f'<a class="li-chip" href="{url("/jobs", company_slug=company['slug'], category=b['category'])}">{e(b['category'])} · {b['n']}</a>'
        for b in breakdown[:5]
    )
    perks_html = "".join(f'<div class="li-perk">{icon("check", 15)} {e(p)}</div>' for p in perks)
    stack_html = "".join(f'<span class="li-chip">{e(s)}</span>' for s in stack)
    industry_html = "".join(
        f'<a class="li-chip" href="{url("/companies", industry=x)}">{e(x)}</a>' for x in industries
    )
    similar_html = "".join(
        f'<a class="li-similar" href="/company/{e(c["slug"])}">{company_logo(c, 84, "li-avatar")}<span><strong>{e(c["name"])}</strong><small>{e(c["location"])} · {thousands(c["employees"])} employees</small></span></a>'
        for c in similar
    )
    post_cards = "".join(
        f'''<article class="li-post">{f'<img src="{e(a["thumb"])}" alt="{e(a["title"])}" width="480" height="270" decoding="async" style="width:100%;aspect-ratio:16/9;height:auto;object-fit:cover;border-radius:14px;display:block;" loading="lazy">' if a.get('thumb') else photo_placeholder(a['accent'], "Add post image", a['slug'], i, 150)}
          <div class="li-post-body"><a class="li-post-title" href="/articles/{e(a['slug'])}">{e(a['title'])}</a>
          <p>{e(a['excerpt'])}</p><div class="li-meta">{e(a['author'])} · {e(a['published'])} · {e(a['read_time'])}</div></div></article>'''
        for i, a in enumerate(related)
    )
    _no_jobs_msg = empty_state(
        f"No active openings at {company['name']}",
        "Create a job alert to get notified when new roles are published.",
        url("/alerts", company=company["slug"]),
        "Create job alert",
    )
    recent_jobs = "".join(linkedin_job_card(j, compact=True) for j in jobs[:4]) or _no_jobs_msg
    all_jobs = "".join(linkedin_job_card(j) for j in jobs) or _no_jobs_msg

    raw_website = safe_http_url(company.get("website") or "")
    has_website = bool(raw_website and "example.com" not in raw_website.lower())
    website_label = re.sub(r"^https?://(www\.)?", "", raw_website).rstrip("/") if has_website else ""
    details = []
    if has_website:
        details.append(("Website", f'<a class="li-link" href="{e(raw_website)}" target="_blank" rel="noopener">{e(website_label)} {icon("external", 13)}</a>'))
    details += [
        ("Industry", e(industries[0] if industries else "Technology")),
        ("Company size", f'{thousands(company["employees"])} employees'),
        ("Headquarters", e(company["location"])),
        ("Founded", e(company["founded"])),
        ("Specialties", ", ".join(e(x) for x in industries[:4])),
    ]
    details_html = "".join(
        f'<div class="li-detail"><dt>{e(label)}</dt><dd>{value}</dd></div>' for label, value in details
    )

    if active == "jobs":
        content = f'''
        <section class="li-card"><div class="li-card-head"><h2>Jobs at {e(company['name'])}</h2><span>{len(jobs)} recent roles</span></div>
          <div class="li-job-list">{all_jobs}</div></section>'''
    elif active == "people":
        content = f'''
        <section class="li-card"><h2>People at {e(company['name'])}</h2><p class="li-muted">Explore the disciplines hiring right now.</p>
          <div class="li-team-grid">{team_cards}</div></section>
        <section class="li-card"><h2>Locations</h2>{_li_office_grid(company)}</section>
        <section class="li-card"><h2>Life at {e(company['name'])}</h2>{_li_culture_grid(company)}</section>'''
    elif active == "posts":
        content = f'''
        <section class="li-card"><div class="li-card-head"><h2>Posts from {e(company['name'])}</h2><a class="li-link" href="/article-blogs">All articles {icon("arrow", 14)}</a></div>
          <div class="li-post-list">{post_cards}</div></section>'''
    elif active == "insights":
        content = f'''
        <section class="li-card"><h2>Company insights</h2><p class="li-muted">Signals candidates use to compare employers.</p>{_li_faq_items(company)}</section>
        <section class="li-card"><h2>At a glance</h2><dl class="li-detail-grid">{details_html}</dl></section>'''
    elif active == "offices":
        content = f'<section class="li-card"><h2>Offices</h2>{_li_office_grid(company)}</section>'
    elif active == "culture":
        content = f'''
        <section class="li-card"><h2>Life at {e(company['name'])}</h2><p>{e(company['description'])}</p>{_li_culture_grid(company)}</section>'''
    elif active == "benefits":
        content = f'''
        <section class="li-card"><h2>Perks + Benefits</h2><p class="li-muted">{e(company['benefits'])} employer benefits and workplace programs.</p>
          <div class="li-perks-grid">{perks_html}</div></section>
        <section class="li-card"><h2>Tech stack</h2><div class="li-chip-row">{stack_html}</div></section>'''
    else:
        content = f'''
        <section class="li-card"><h2>About us</h2><p class="li-lead">{e(company['tagline'])}</p>
          <p>{e(company['description'])}</p><div class="li-chip-row">{industry_html}</div></section>
        <section class="li-card"><h2>Details</h2><dl class="li-detail-grid">{details_html}</dl></section>
        <section class="li-card"><div class="li-card-head"><h2>People</h2><a class="li-link" href="/company/{e(company['slug'])}/people">See all {icon("arrow", 14)}</a></div>
          <div class="li-team-grid">{team_cards}</div></section>
        <section class="li-card"><div class="li-card-head"><h2>Locations</h2><a class="li-link" href="/company/{e(company['slug'])}/offices">See all {icon("arrow", 14)}</a></div>
          {_li_office_grid(company)}</section>
        <section class="li-card"><div class="li-card-head"><h2>Benefits</h2><a class="li-link" href="/company/{e(company['slug'])}/benefits">See all {icon("arrow", 14)}</a></div>
          <div class="li-perks-grid">{perks_html}</div></section>
        <section class="li-card"><div class="li-card-head"><h2>Recently posted jobs</h2><a class="li-link" href="/company/{e(company['slug'])}/jobs">Show all {icon("arrow", 14)}</a></div>
          <div class="li-job-list">{recent_jobs}</div></section>'''

    sidebar = f'''
      <section class="li-card li-side-card"><h3>About the company</h3>
        <div class="li-side-logo">{company_logo(company, 84, 'li-avatar')}</div>
        <p class="li-muted">{e(company['tagline'])}</p>
        <dl class="li-side-list"><div><dt>Industry</dt><dd>{e(industries[0] if industries else 'Technology')}</dd></div>
          <div><dt>Size</dt><dd>{thousands(company['employees'])}</dd></div>
          <div><dt>Type</dt><dd>{e(company['office_type'])}</dd></div>
          <div><dt>Open jobs</dt><dd>{thousands(company['open_jobs'])}</dd></div></dl>
        <a class="li-btn li-btn-primary li-btn-block" href="/company/{e(company['slug'])}/jobs">{icon("briefcase", 16)} View jobs</a>
      </section>
      <section class="li-card li-side-card"><h3>Stay in the loop</h3><p class="li-muted">Get an alert when {e(company['name'])} posts a new role.</p>
        <a class="li-btn li-btn-outline li-btn-block" href="{url('/alerts', company=company['slug'])}">{icon("bell", 16)} Create job alert</a></section>
      <section class="li-card li-side-card"><h3>Similar pages</h3><div class="li-similar-list">{similar_html}</div></section>'''

    body = f'''
    <section class="li-cover" style="--cover-accent:{e(company['color'])}">
      <div class="li-cover-art"><span></span><span></span><span></span></div>
      <div class="container li-cover-inner">{breadcrumb([("Home", "/"), ("Companies", "/companies"), (company["name"], "")])}
        <span class="li-cover-badge">{icon("star", 14)} Company profile · 2026</span></div>
    </section>
    <section class="li-profile-wrap"><div class="container">
      <div class="li-card li-profile-card">
        <div class="li-profile-top">
          {company_logo(company, 84, 'li-profile-logo')}
          <div class="li-profile-ident">
            <h1>{e(company['name'])}</h1>
            <p class="li-profile-tagline">{e(company['tagline'])}</p>
            <div class="li-meta">{e(industries[0] if industries else 'Technology')} · {e(company['location'])} · {thousands(company['employees'])} employees · {e(company['office_type'])}</div>
            <div class="li-meta">Founded {e(company['founded'])} · {e(company['benefits'])} benefits · {thousands(company['open_jobs'])} open jobs</div>
          </div>
          <div class="li-profile-actions">
            <button class="li-btn li-btn-primary li-follow-btn follow-btn{' followed' if followed else ''}" type="button" data-company-id="{cid}" aria-pressed="{'true' if followed else 'false'}">
              {icon("plus", 16)} <span>{'Following' if followed else 'Follow'}</span>
            </button>
            <a class="li-btn li-btn-outline" href="/company/{e(company['slug'])}/jobs">{icon("briefcase", 16)} View jobs</a>
            {f'<a class="li-btn li-btn-subtle" href="{e(raw_website)}" target="_blank" rel="noopener">Website {icon("external", 15)}</a>' if has_website else ''}
          </div>
        </div>
      </div>
      <nav class="li-tabs" aria-label="Company sections">{tabs}</nav>
    </div></section>
    <section class="li-content"><div class="container li-grid">
      <div class="li-col-main">{content}</div>
      <aside class="li-col-side">{sidebar}</aside>
    </div></section>'''
    return layout(f'{company["name"]} | Company Profile', body, user, active="companies",
                  page_class="company-detail-page linkedin-style",
                  description=f"Explore {company['name']} jobs, people, culture and benefits.")


def linkedin_job_detail_page(conn, user, job, similar):
    return job_detail_page(conn, user, job, similar)


def job_detail_page(conn, user, job, similar):
    if user:
        db_saved = job["id"] in db.saved_job_ids(conn, user["id"])
        applied = bool(conn.execute("SELECT 1 FROM applications WHERE user_id=? AND job_id=?", (user["id"], job["id"])).fetchone())
    else:
        db_saved = applied = False

    company = db.get_company(conn, job["company_slug"]) or {}
    company_name = job.get("company_name") or company.get("name") or "Company"
    company_slug = job.get("company_slug") or company.get("slug") or "company"
    company_color = job.get("company_color") or company.get("color") or "#003366"
    company_initials = job.get("company_initials") or company.get("initials") or "CO"
    company_tagline = company.get("tagline") or f"{company_name} — Accredited Multimodal Terminal Operator"
    company_hq = company.get("location") or job.get("location") or "Ho Chi Minh City, VN"
    company_founded = company.get("founded") or 1985
    company_employees = company.get("employees") or 2500
    company_offices = company.get("offices") or 5
    company_desc = company.get("description") or f"{company_name} is an accredited leader in {job.get('category') or 'multimodal logistics'}."

    logo_html = _brand_logo_markup(company_slug, company_name, initials=company_initials, color=company_color, img_id="hero-logo-img", lazy=False)

    job_title = job["title"]
    location = job.get("location") or "Ho Chi Minh City, VN"
    workplace = job.get("workplace") or "Hybrid"
    salary = job.get("salary_display") or "Competitive"
    level = job.get("level") or "Senior level"
    posted_label = job.get("posted_label") or "Posted Recently"
    if not (posted_label.lower().startswith("posted") or posted_label.lower().startswith("reposted")):
        posted_label = f"Posted {posted_label}"

    raw_cats = [x.strip() for x in (job.get("industries") or "").split(",") if x.strip()]
    if not raw_cats:
        raw_cats = [job.get("category") or "Logistics & Supply Chain"]
    categories_text = " &bull; ".join(raw_cats[:4])

    skills = [x.strip() for x in (job.get("skills") or "").split(",") if x.strip()]
    if not skills:
        skills = ["Strategy & Planning", "Cross-Functional Leadership", "Stakeholder Communication", "Execution & Quality"]

    if company_slug == "viconship" and ("freight" in job.get("slug", "") or job.get("id") == 1):
        role_summary = "Viconship is seeking a seasoned Ocean Freight Forwarding Specialist to manage end-to-end container booking, multimodal carrier negotiations, and freight optimization for multinational manufacturing accounts in Southern Vietnam."
        role_intro = "Viconship is one of Vietnam's leading integrated container seaport and terminal operators. We drive multimodal freight forwarding, container terminal management, bonded warehousing, and logistics supply chain services connecting Vietnam with major world trade lanes."
        role_job_summary = "Responsible for managing container ocean freight forwarding, FMC carrier contracts, port dispatch operations, and customer supply chain delivery across Southeast Asia, North America, and European trade corridors."
        responsibilities = [
            "Coordinate ocean freight routing, rate negotiations, and space allocation with major maritime alliances (2M, Ocean Alliance, THE Alliance).",
            "Manage complex customs clearance, FMC bill-of-lading (B/L) documentation, and cross-border demurrage/detention minimization.",
            "Act as direct strategic escalation lead for Tier-1 automotive and electronics enterprise shippers.",
            "Supervise electronic EDI declarations under Decree 163/2017/ND-CP and international shipping conventions.",
        ]
        skills_required = [
            "Bachelor's degree in Foreign Trade, Maritime Economics, or International Logistics.",
            "3+ years of experience in ocean freight forwarding or container shipping lines.",
            "Proficiency in Incoterms 2020, customs brokerage, and maritime bill-of-lading documentation.",
            "Bilingual communication in Vietnamese and English.",
            "Customer-focused approach and ability to build and retain commercial business relationships.",
        ]
        team_quote = "“At Viconship, managing real-time vessel berthing and cross-border maritime logistics alongside an elite team gives you immediate operational impact. There's real pride in moving Vietnam's industrial exports to the world every day.”"
        quote_name = "Nguyen Minh Tri"
        quote_title = "Director of Ocean Freight & Port Operations, Viconship"
        comp_what_we_do = "Viconship operates multimodal container seaport terminals, bonded logistics depots, inland container depots (ICDs), and international freight forwarding networks connecting Vietnam with global maritime trade lanes."
        comp_why_work = "Join an accredited maritime and logistics leader driving Vietnam's national supply chain infrastructure. We empower our logistics teams with career mentoring, international shipping academy certifications (FIATA / VLA), and performance incentives."
        offices_desc = "Hai Phong VIP Green Port, Cat Lai Terminal (HCMC), and Da Nang Port Logistics Center."
    else:
        role_summary = job.get("description") or f"{company_name} is seeking a qualified {job_title} to join our high-performing team."
        role_intro = company_desc
        role_job_summary = f"Responsible for leading strategic {job.get('category') or 'initiatives'}, driving scalable product and business results, and collaborating closely with cross-functional partners."
        responsibilities = [
            f"Partner with team leads to define, execute, and deliver high-impact {raw_cats[0] if raw_cats else 'business'} outcomes.",
            f"Leverage hands-on experience in {', '.join(skills[:2])} to build resilient and scalable solutions.",
            f"Break down ambiguous challenges into structured execution plans and measurable milestones.",
            f"Mentor teammates, advocate best practices, and contribute to continuous team improvement.",
        ]
        skills_required = [
            f"Demonstrated proficiency in {', '.join(skills[:4])}.",
            f"3+ years of professional experience as a {level} contributor in a related discipline.",
            "Strong problem-solving capability, technical rigor, and clear communication skills.",
            "Experience operating in fast-paced collaborative environments with cross-functional teams.",
            "Bachelor's degree in a relevant field or equivalent practical experience.",
        ]
        team_quote = f"“At {company_name}, driving innovation in {raw_cats[0] if raw_cats else 'our industry'} alongside an elite team gives you immediate operational impact. There's real ownership and support to do your best work every day.”"
        quote_name = f"{company_name} Team"
        quote_title = f"{job.get('category') or 'Engineering & Operations'}"
        comp_what_we_do = company_desc
        comp_why_work = f"Join an industry leader driving modern innovation. We empower our teams with career mentoring, competitive compensation, and clear growth pathways."
        offices_desc = f"Main campus in {company_hq} and distributed collaborative teams."

    # Similar jobs
    if not similar:
        similar = [db.as_dict(r) for r in conn.execute("SELECT * FROM jobs WHERE status='active' AND id != ? LIMIT 3", (job["id"],)).fetchall()]
    similar_items_html = []
    for s in similar[:4]:
        s_cats = [x.strip() for x in (s.get("industries") or "").split(",") if x.strip()]
        s_cat_display = " &bull; ".join(s_cats[:2]) if s_cats else (s.get("category") or "General")
        similar_items_html.append(f'''
        <a href="/job/{e(s.get('slug') or 'job')}/{s['id']}" class="similar-job-item">
          <div class="similar-job-left">
            <div class="similar-job-company">{e(s.get('company_name') or 'Company')}</div>
            <div class="similar-job-title">{e(s['title'])}</div>
            <div class="similar-job-cats">{e(s_cat_display)}</div>
          </div>
          <div class="similar-job-right">
            <strong>{e(s.get('salary_display') or 'Competitive')}</strong>
            <span>{e(s.get('location') or 'Remote')}</span>
          </div>
        </a>''')
    similar_jobs_html = "".join(similar_items_html) if similar_items_html else '<p style="padding:16px;color:#64748b;font-size:12px;">No similar jobs found.</p>'

    skills_badges_html = "".join(f'<span class="skill-pill" style="display:inline-block;padding:4px 10px;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:4px;font-size:11.5px;font-weight:600;margin:3px 4px 3px 0;">{e(s)}</span>' for s in skills)
    responsibilities_html = "".join(f'<li>{e(r)}</li>' for r in responsibilities)
    skills_req_html = "".join(f'<li>{e(r)}</li>' for r in skills_required)

    save_btn_label = "Saved" if db_saved else "Save"
    save_btn_icon = "fa-solid fa-bookmark" if db_saved else "fa-regular fa-bookmark"
    apply_btn_label = "Application Submitted" if applied else "Easy Apply with CV"
    apply_btn_class = "btn-builtin-apply" + (" btn-applied-disabled" if applied else "")

    user_name = user.get("name") if user else ""
    user_email = user.get("email") if user else ""

    if user:
        auth_header_snippet = f'''
        <div class="user-profile-menu-wrap" style="position:relative;">
          <button type="button" class="header-user-avatar-circle" onclick="toggleUserMenu();" style="width:36px;height:36px;border-radius:50%;background:#003366;color:#ffffff;border:2px solid #e2e8f0;font-weight:700;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;">
            <span>{e(user['name'][:1].upper())}</span>
          </button>
          <div id="user-menu-dropdown" style="display:none;position:absolute;right:0;top:44px;background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,0.15);width:190px;z-index:1001;padding:6px 0;">
            <div style="padding:8px 14px;border-bottom:1px solid #f1f5f9;font-size:12px;"><strong>{e(user['name'])}</strong><div style="color:#64748b;font-size:11px;">{e(user['email'])}</div></div>
            <a href="/profile" style="display:block;padding:7px 14px;font-size:12.5px;color:#1e293b;text-decoration:none;">Dashboard</a>
            <a href="/tracker" style="display:block;padding:7px 14px;font-size:12.5px;color:#1e293b;text-decoration:none;">Applications</a>
            <a href="/saved" style="display:block;padding:7px 14px;font-size:12.5px;color:#1e293b;text-decoration:none;">Saved Jobs</a>
            <a href="/alerts" style="display:block;padding:7px 14px;font-size:12.5px;color:#1e293b;text-decoration:none;">Job Alerts</a>
            <form method="post" action="/logout" style="margin:0;">{csrf_input()}<button type="submit" style="display:block;width:100%;text-align:left;padding:7px 14px;font-size:12.5px;color:#ef4444;background:none;border:none;border-top:1px solid #f1f5f9;cursor:pointer;">Log Out</button></form>
          </div>
        </div>
        '''
    else:
        auth_header_snippet = f'''
        <a href="{url('/auth/login', next=f'/job/{job.get('slug') or 'job'}/{job['id']}')}" class="wt-btn-header-login" title="Sign In">
          <i class="fa-solid fa-arrow-right-to-bracket"></i>
          <span>Log In</span>
        </a>
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(company_name)} | {e(job_title)}</title>
  <meta name="description" content="Apply for {e(job_title)} at {e(company_name)}. {e(workplace)} role in {e(location)} with competitive compensation ({e(salary)}).">
  <meta name="author" content="Logistic Waves">
  <meta name="csrf-token" content="{e(_get_csrf())}">
  <link rel="icon" type="image/png" href="/static/favicon.png">

  <!-- FontAwesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <!-- Apple SF Pro Display / Text + Inter optical fallback -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..800&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="/static/styles.css?v=20261127_wttj_v4">
  <link rel="stylesheet" href="/static/home-recreation.css?v=20261126_apple2">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="/static/thesandbox-css/builtin-theme.css">
  <link rel="stylesheet" href="/static/job-detail-sandbox.css?v=20261126_apple2">
</head>
<body data-logged-in="{'true' if user else 'false'}">

  <!-- Unified Built In Site Navigation Header -->
  {header(user, active="jobs")}

  <main id="main-content">
  <!-- Built In Breadcrumbs Strip -->
  <div class="builtin-breadcrumb-wrap" aria-label="Breadcrumb Bar">
    <div class="builtin-breadcrumb-inner">
      <a href="/">Home</a>
      <span class="builtin-breadcrumb-sep">&rsaquo;</span>
      <a href="/jobs">Jobs</a>
      <span class="builtin-breadcrumb-sep">&rsaquo;</span>
      <a href="/company/{e(company_slug)}" id="crumb-company">{e(company_name)}</a>
      <span class="builtin-breadcrumb-sep">&rsaquo;</span>
      <span class="builtin-breadcrumb-current" id="crumb-title">{e(job_title)}</span>
    </div>
  </div>

  <!-- Built In Flagship Hero Section -->
  <section class="builtin-hero" aria-label="Job Overview and Action Hero">
    <div class="flagship-hero-container">
      <div class="flagship-job-card">
        
        <!-- Top Row: Logo Box, Company Meta, New Badge & Bookmark -->
        <div class="flagship-top-row">
          <div class="flagship-brand-group">
            <div class="flagship-logo-box" id="hero-logo-box">
              {logo_html}
            </div>
            <div class="flagship-company-meta">
              <div class="flagship-company-name-row">
                <a href="/company/{e(company_slug)}" class="flagship-company-name" id="hero-company-name">
                  {e(company_name)}
                </a>
                <span class="flagship-verified-badge" title="Verified Employer">
                  <i class="fa-solid fa-circle-check" style="font-size: 15px; color: #0A66C2;"></i>
                </span>
              </div>
              <div class="flagship-company-sub">
                <span id="hero-department">{e(categories_text.replace("&bull;", "•").replace("&amp;bull;", "•") if categories_text else "M&E Engineering")}</span>
                <span class="sub-dot">•</span>
                <span id="hero-company-size">{thousands(company_employees)} employees</span>
              </div>
            </div>
          </div>

          <div class="flagship-top-actions">
            <span class="flagship-badge-new">
              <span class="new-dot"></span>
              New
            </span>
            <button type="button" class="flagship-save-btn{' saved' if db_saved else ''}" id="hero-save-btn" title="Save job" onclick="toggleSaveHeroJob && toggleSaveHeroJob(this)">
              <i class="{e(save_btn_icon)}"></i>
            </button>
          </div>
        </div>

        <!-- Main Job Title -->
        <h1 class="flagship-job-title" id="hero-title">{e(job_title)}</h1>

        <!-- Attributes Strip with | dividers -->
        <div class="flagship-specs-strip">
          <div class="flagship-spec-cell">
            <i class="fa-solid fa-location-dot spec-icon"></i>
            <span id="hero-location-text">{e(location)}</span>
          </div>
          <span class="flagship-pipe">|</span>
          <div class="flagship-spec-cell">
            <i class="fa-solid fa-briefcase spec-icon"></i>
            <span id="hero-workplace-text">{e(workplace)}</span>
          </div>
          <span class="flagship-pipe">|</span>
          <div class="flagship-spec-cell">
            <i class="fa-solid fa-chart-simple spec-icon"></i>
            <span id="hero-seniority-text">{e(level)}</span>
          </div>
        </div>

        <!-- Bottom Row: Salary & Posted Date | Apply Now Button -->
        <div class="flagship-bottom-row">
          <div class="flagship-bottom-left">
            <div class="flagship-salary-cell">
              <i class="fa-solid fa-sack-dollar" style="color: #0052cc; font-size: 16px;"></i>
              <strong class="flagship-salary-text" id="hero-salary-text">{e(salary)}</strong>
            </div>
            <span class="flagship-pipe">|</span>
            <div class="flagship-posted-cell">
              <i class="fa-regular fa-clock spec-icon"></i>
              <span id="hero-posted-time-text">{e(posted_label)}</span>
            </div>
          </div>

          <div class="flagship-bottom-right">
            <a href="#apply-section" class="flagship-apply-btn" onclick="openApplyModal && openApplyModal(event); return false;">
              <span>Apply Now</span>
              <i class="fa-solid fa-chevron-right" style="font-size: 13px;"></i>
            </a>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- Built In 2-Column Main Section -->
  <div class="builtin-layout">
    
    <!-- Left Column: Role Details, Description, Skills, Culture -->
    <div class="builtin-column">
      
      <!-- Section 1: The Role -->
      <div class="builtin-card" id="card-the-role">
        <div class="builtin-card-header">
          <span>The Role</span>
        </div>
        <div class="builtin-card-body">
          <p class="role-summary-p" id="role-summary-p">
            {e(role_summary)}
          </p>
          <div class="role-generated-tag">
            &mdash; Summary Generated by Logistic Waves &amp; Industry Intelligence &mdash;
          </div>

          <!-- Action Buttons -->
          <div class="role-actions-row">
            <button type="button" class="{e(apply_btn_class)}" id="btn-hero-easy-apply" onclick="handlePrimaryApply();">
              <i class="fa-solid fa-paper-plane"></i>
              <span>{e(apply_btn_label)}</span>
            </button>
            <button type="button" class="btn-builtin-save" id="btn-hero-save-job" onclick="handleSaveJob();" data-job-id="{job['id']}">
              <i class="{e(save_btn_icon)}" id="save-btn-icon"></i>
              <span id="save-btn-label">{e(save_btn_label)}</span>
            </button>
          </div>

          <div style="border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 6px;">
            <p class="desc-body-p" id="desc-intro-p">
              {e(role_intro)}
            </p>

            <div class="desc-subheading">Job Summary</div>
            <p class="desc-body-p" id="desc-summary-p">
              {e(role_job_summary)}
            </p>

            <div class="desc-subheading">Job Description &amp; Core Responsibilities</div>
            <ul class="desc-bullets-list" id="desc-responsibilities-ul">
              {responsibilities_html}
            </ul>

            <div id="desc-extra-content" style="display: none;">
              <div class="desc-subheading">Operational Standards &amp; Impact</div>
              <p class="desc-body-p">
                At {e(company_name)}, this role acts as an integral operational anchor. You will liaise directly with regional stakeholders, internal departments, and strategic partners to ensure timely, compliant, and exceptional execution across all deliverables.
              </p>
            </div>

            <button type="button" class="btn-read-more-toggle" onclick="toggleReadMore(this);">
              <span>Read Full Description</span>
              <i class="fa-solid fa-chevron-down"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Section 2: Skills Required -->
      <div class="builtin-card" id="card-skills-required">
        <div class="builtin-card-body">
          <div class="skills-header-simple">Skills Required</div>
          <ul class="desc-bullets-list" id="skills-required-ul" style="margin-bottom: 0;">
            {skills_req_html}
          </ul>
        </div>
      </div>

      <!-- Section 3: What The Team Is Saying -->
      <div class="builtin-card" id="card-team-saying">
        <div class="builtin-card-body">
          <div class="skills-header-simple">What The Team Is Saying</div>
          
          <div class="quote-box-wrap">
            <div class="quote-white-card" id="team-quote-text">
              {e(team_quote)}
            </div>
            <div class="quote-navy-card">
              <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80" alt="Team member" class="quote-avatar" id="team-quote-avatar" width="56" height="56" loading="lazy" decoding="async" data-fallback-kind="avatar">
              <div>
                <div class="quote-person-name" id="team-quote-name">{e(quote_name)}</div>
                <div class="quote-person-title" id="team-quote-title">{e(quote_title)}</div>
              </div>
            </div>
          </div>

          <div class="quote-faces-row">
            <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
            <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
            <img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
            <img src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
            <img src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=80&q=80" alt="Team member" class="quote-face-avatar" width="40" height="40" loading="lazy" decoding="async" data-fallback-kind="avatar">
          </div>
        </div>
      </div>

      <!-- Section 4: Compensation & Benefits Highlights -->
      <div class="builtin-card" id="card-benefits">
        <div class="builtin-card-body">
          <div class="skills-header-simple" id="benefits-title-lead">{e(company_name)} Compensation &amp; Benefits Highlights</div>
          
          <div class="benefit-item-row">
            <strong>Healthcare Strength</strong> &mdash; Comprehensive healthcare insurance, annual executive medical checkups, 24/7 accident coverage, and mental-wellbeing support for all full-time personnel.
          </div>
          <div class="benefit-item-row">
            <strong>Performance Rewards</strong> &mdash; Competitive base compensation plus guaranteed 13th-month salary, quarterly performance KPI bonuses, and annual profit-sharing distribution.
          </div>
          <div class="benefit-item-row">
            <strong>Professional Certification</strong> &mdash; 100% company-sponsored professional development programs, industry certifications (e.g. FIATA / VLA), and leadership advancement pathways.
          </div>
          <div class="benefit-item-row">
            <strong>Workplace Flexibility</strong> &mdash; Flexible {e(workplace).lower()} work arrangements, ergonomic workspace stipends, and company retreats.
          </div>

          <div style="margin-top: 16px;">
            <a href="/company/{e(company_slug)}/benefits" class="insight-link" id="benefits-learn-more-link">Learn more about {e(company_name)}'s Compensation &amp; Benefits &rarr;</a>
          </div>
        </div>
      </div>

      <!-- Section 5: Company Insights -->
      <div class="builtin-card" id="card-insights">
        <div class="builtin-card-header">
          <span id="insights-header-label">{e(company_name)} Insights</span>
        </div>
        <div class="insights-list">
          <a href="/company/{e(company_slug)}/insights" class="insight-link">What's It Like to Work at {e(company_name)}?</a>
          <a href="/company/{e(company_slug)}/culture" class="insight-link">{e(company_name)} Culture &amp; Values</a>
          <a href="/company/{e(company_slug)}/people" class="insight-link">{e(company_name)} Career Growth &amp; Development</a>
          <a href="/company/{e(company_slug)}/offices" class="insight-link">What's the Work-Life Balance Like at {e(company_name)}?</a>
          <a href="/company/{e(company_slug)}/people" class="insight-link">{e(company_name)} Leadership &amp; Management</a>
          <a href="/company/{e(company_slug)}/insights" class="insight-link">{e(company_name)} Company Growth, Stability &amp; Outlook</a>
        </div>
        
        <div class="job-utility-links">
          <a href="/jobs?q={urllib.parse.quote(company_name)}" id="utility-view-all-jobs">
            <i class="fa-solid fa-briefcase"></i>
            <span>View all jobs at {e(company_name)}</span>
          </a>
          <a href="/company/{e(company_slug)}" id="utility-view-profile">
            <i class="fa-solid fa-building"></i>
            <span>View {e(company_name)} Profile</span>
          </a>
          <button type="button" style="background:none;border:none;padding:0;font:inherit;color:inherit;cursor:pointer;display:inline-flex;align-items:center;gap:6px;" onclick="showToast('Listing flagged for editorial review.');">
            <i class="fa-regular fa-flag"></i>
            <span>Report Job</span>
          </button>
        </div>
      </div>

    </div>

    <!-- Right Sticky Column: AI Fit Radar, Company Dossier, Gallery, Similar Jobs -->
    <div class="builtin-column">
      <div class="sticky-sidebar-wrap">
        
        <!-- Panel 1: Am I A Good Fit? -->
        <div class="ai-fit-card">
          <div class="ai-fit-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-wand-magic-sparkles"></i>
              <span>Am I A Good Fit?</span>
              <i class="fa-solid fa-circle-info" style="font-size: 11px; opacity: 0.85;"></i>
            </div>
          </div>
          <div class="ai-fit-body">
            <div class="ai-insights-lead">
              <div class="ai-symbol-star">&#10022;</div>
              <div>
                <div class="ai-title-lead">Get Personalized Job Insights.</div>
                <p class="ai-desc-lead">Our AI-powered fit analysis compares your resume with a job listing so you know if your skills &amp; experience align.</p>
              </div>
            </div>

            <div class="ai-dropzone-box" onclick="document.getElementById('ai-cv-upload-input').click();">
              <input type="file" id="ai-cv-upload-input" style="display: none;" accept=".pdf,.doc,.docx" onchange="handleAiCvUpload(this);">
              <i class="fa-solid fa-cloud-arrow-up" style="font-size: 24px; color: var(--blue); margin-bottom: 8px;"></i>
              <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 8px;">Drag &amp; drop resume or click to select</div>
              <button type="button" class="btn-ai-upload">Upload Resume</button>
            </div>

            <!-- Analysis Result Output Container -->
            <div id="ai-analysis-feedback" style="display: none; margin-top: 14px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 12px; font-size: 12px; color: #1e3a8a;">
              <div style="font-weight: 800; display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <i class="fa-solid fa-circle-check" style="color: #2563eb;"></i>
                <span>Match Score: 94% &bull; Strong Fit</span>
              </div>
              <div>Your operational expertise and domain qualifications align exceptionally with this {e(job_title)} opening!</div>
            </div>
          </div>
        </div>

        <!-- Panel 2: The Company -->
        <div class="builtin-card">
          <div class="builtin-card-header">
            <span>The Company</span>
          </div>
          <div class="builtin-card-body">
            <!-- Quick Stats -->
            <div class="company-stats-grid">
              <div class="company-stat-cell">
                <i class="fa-solid fa-building-columns"></i>
                <span id="comp-hq-label">HQ: {e(company_hq)}</span>
              </div>
              <div class="company-stat-cell">
                <i class="fa-regular fa-calendar"></i>
                <span id="comp-founded-label">Founded: {e(company_founded)}</span>
              </div>
              <div class="company-stat-cell" style="grid-column: 1 / -1;">
                <i class="fa-solid fa-users"></i>
                <span id="comp-headcount-label">{thousands(company_employees)}+ Team Members</span>
              </div>
            </div>

            <div class="desc-subheading" style="margin-top: 0;">What We Do</div>
            <p class="desc-body-p" id="comp-what-we-do">
              {e(comp_what_we_do)}
            </p>

            <div class="desc-subheading">Why Work With Us</div>
            <p class="desc-body-p" id="comp-why-work">
              {e(comp_why_work)}
            </p>

            <!-- Gallery -->
            <div class="desc-subheading">Gallery</div>
            <div class="company-gallery-grid">
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=350&q=80');"></div>
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=350&q=80');"></div>
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=350&q=80');"></div>
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=350&q=80');"></div>
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=350&q=80');"></div>
              <div class="gallery-photo-thumb" style="background-image: url('https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=350&q=80');"></div>
            </div>

            <!-- Offices -->
            <div style="border-top: 1px solid var(--border-light); padding-top: 12px; margin-top: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div class="desc-subheading" style="margin: 0;" id="comp-offices-title">{e(company_name)} Offices</div>
                <a href="/company/{e(company_slug)}" class="insight-link" style="font-size: 11px;">LEARN MORE &rarr;</a>
              </div>
              <div style="font-size: 12.5px; font-weight: 700; color: var(--navy); display: flex; align-items: center; gap: 6px;">
                <i class="fa-solid fa-house-laptop" style="color: var(--blue);"></i>
                <span>{e(workplace)} Workspace</span>
              </div>
              <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 2px;">
                {e(offices_desc)}
              </div>
              <div class="workplace-pill-row">
                Accredited Hub &bull; {e(company_offices)} Facilities
              </div>
            </div>
          </div>
        </div>

        <!-- Panel 3: Similar Jobs -->
        <div class="builtin-card">
          <div class="builtin-card-header">
            <span>Similar Jobs</span>
          </div>
          <div id="similar-jobs-container">
            {similar_jobs_html}
          </div>
        </div>

      </div>
    </div>
    </div>

  <!-- Quick Application Modal (Easy Apply) - kept inside #main-content for SPA navigation -->
  <div class="modal-backdrop" id="modal-apply" role="dialog" aria-modal="true" aria-labelledby="apply-modal-title" style="display: none;">
    <div class="modal-container" style="max-width: 580px;">
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div class="modal-header-icon"><i class="fa-solid fa-paper-plane"></i></div>
          <div>
            <h2 class="modal-title" id="apply-modal-title" style="font-size: 16px;">Quick Application &bull; Logistic Waves</h2>
            <div class="modal-subtitle" id="apply-modal-subtitle" style="font-size: 11.5px; color: #93C5FD;">{e(job_title)}, {e(company_name)}</div>
          </div>
        </div>
        <button type="button" class="modal-close-btn" id="btn-close-apply-modal" onclick="closeApplyModal();" aria-label="Close modal">&times;</button>
      </div>

      <div style="background: #EFF6FF; border-bottom: 1px solid #DBEAFE; padding: 8px 20px; font-size: 11.5px; color: #1E40AF; display: flex; align-items: center; gap: 8px;">
        <i class="fa-solid fa-circle-info"></i>
        <span><strong>Live Application:</strong> Dossier will be recorded in the database, stored in your Application Tracker, and transmitted directly to the hiring team.</span>
      </div>

      <form id="form-job-apply" novalidate>
        <div class="modal-body" style="padding: 16px 20px;">
          <div style="margin-bottom: 14px;">
            <label style="display: block; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 5px;">Candidate Full Name *</label>
            <input type="text" id="apply-input-name" required value="{e(user_name)}" placeholder="e.g. Nguyễn Minh Trí" style="width: 100%; padding: 9px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 13px;">
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div>
              <label style="display: block; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 5px;">Work Email *</label>
              <input type="email" id="apply-input-email" required value="{e(user_email)}" placeholder="alex@domain.com" style="width: 100%; padding: 9px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 13px;">
            </div>
            <div>
              <label style="display: block; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 5px;">Phone Number</label>
              <input type="tel" id="apply-input-phone" placeholder="+84 901 234 567" style="width: 100%; padding: 9px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 13px;">
            </div>
          </div>
          <div style="margin-bottom: 14px;">
            <label style="display: block; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 5px;">Attach Resume / Portfolio (PDF or DOCX, max 10MB)</label>
            <input type="file" id="apply-input-file" accept=".pdf,.doc,.docx" style="width: 100%; padding: 8px; border: 1px dashed #94A3B8; border-radius: 6px; font-size: 12px; background: #F8FAFC;">
          </div>
          <div style="margin-bottom: 8px;">
            <label style="display: block; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 5px;">Candidate Cover Note (Optional)</label>
            <textarea id="apply-input-note" rows="3" placeholder="Highlight relevant accomplishments, certifications, or why this role excites you..." style="width: 100%; padding: 9px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 12.5px;"></textarea>
          </div>
        </div>
        <div class="modal-footer" style="padding: 12px 20px; background: #F8FAFC; border-top: 1px solid #E2E8F0; display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" onclick="closeApplyModal();" style="padding: 8px 16px; border: none; background: #F1F5F9; color: #475569; border-radius: 6px; font-weight: 700; cursor: pointer;">Cancel</button>
          <button type="submit" id="btn-submit-job-apply" class="btn-apply-primary">
            <span>Submit Application</span> &rarr;
          </button>
        </div>
      </form>
    </div>
  </div>



  <script>
    (function() {{
      const jobId = {job['id']};
      const jobTitle = {json.dumps(job_title)};
      const jobSkills = {json.dumps(skills)};

      function redirectToLogin() {{
        const nextUrl = window.location.pathname + window.location.search;
        window.location.href = '/auth/login?next=' + encodeURIComponent(nextUrl);
      }}

      window.toggleLangMenu = function() {{
        const m = document.getElementById('lang-dropdown-menu');
        if (m) m.style.display = m.style.display === 'none' ? 'block' : 'none';
      }};
      window.switchLang = function(lang) {{
        const l = document.getElementById('lang-current-label');
        if (l) l.textContent = lang === 'vn' ? 'Tiếng Việt' : 'English';
        window.toggleLangMenu();
        window.showToast(lang === 'vn' ? 'Đã đổi ngôn ngữ sang Tiếng Việt' : 'Language switched to English');
      }};
      window.toggleUserMenu = function() {{
        const m = document.getElementById('user-menu-dropdown');
        if (m) m.style.display = m.style.display === 'none' ? 'block' : 'none';
      }};
      window.handlePrimaryApply = function() {{
        const modal = document.getElementById('modal-apply');
        if (modal) modal.style.display = 'flex';
      }};
      window.openApplyModal = function(ev) {{
        if (ev) ev.preventDefault();
        window.handlePrimaryApply();
      }};
      window.closeApplyModal = function() {{
        const modal = document.getElementById('modal-apply');
        if (modal) modal.style.display = 'none';
      }};

      const _origToast = window.showToast;
      window.showToast = function(msg, isError) {{
        if (typeof _origToast === 'function' && document.getElementById('toast')) {{
          _origToast(msg, isError);
          return;
        }}
        const t = document.getElementById('toast');
        if (!t) return;
        const iconCls = isError ? 'fa-circle-exclamation' : 'fa-circle-check';
        const iconColor = isError ? '#ef4444' : '#10b981';
        t.innerHTML = '';
        const iconEl = document.createElement('i');
        iconEl.className = 'fa-solid ' + iconCls;
        iconEl.style.color = iconColor;
        const msgEl = document.createElement('span');
        msgEl.textContent = msg;
        t.appendChild(iconEl);
        t.appendChild(document.createTextNode(' '));
        t.appendChild(msgEl);
        t.style.display = 'flex';
        t.style.opacity = '1';
        clearTimeout(window.__toastTimer);
        window.__toastTimer = setTimeout(() => {{
          t.style.opacity = '0';
          setTimeout(() => {{ t.style.display = 'none'; }}, 300);
        }}, 3500);
      }};

      window.toggleReadMore = function(btn) {{
        const extra = document.getElementById('desc-extra-content');
        if (!extra) return;
        const isHidden = extra.style.display === 'none';
        if (isHidden) {{
          extra.style.display = 'block';
          btn.innerHTML = '<span>Collapse Description</span> <i class="fa-solid fa-chevron-up"></i>';
        }} else {{
          extra.style.display = 'none';
          btn.innerHTML = '<span>Read Full Description</span> <i class="fa-solid fa-chevron-down"></i>';
        }}
      }};

      window.handleAiCvUpload = function(input) {{
        if (input.files && input.files[0]) {{
          const file = input.files[0];
          const fb = document.getElementById('ai-analysis-feedback');
          const fname = file.name.toLowerCase();
          const matched = jobSkills.filter(s => fname.includes(s.toLowerCase().split(' ')[0]));
          const score = Math.min(96, 72 + Math.min(20, matched.length * 6) + (file.size > 15000 ? 4 : 0));
          const skillNote = matched.length ? ('Matched keywords: ' + matched.join(', ')) : ('Target skills: ' + jobSkills.slice(0, 4).join(', '));
          if (fb) {{
            fb.style.display = 'block';
            const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            fb.innerHTML = '<div style="font-weight:800;display:flex;align-items:center;gap:6px;margin-bottom:4px;color:#1e3a8a;"><i class="fa-solid fa-circle-check" style="color:#2563eb;"></i><span>Estimated Fit Score: ' + score + '%</span></div><div>Analyzed <strong>' + esc(file.name) + '</strong> (' + (file.size/1024).toFixed(1) + ' KB) for ' + esc(jobTitle) + '. ' + esc(skillNote) + '.</div>';
          }}
          window.showToast('CV analysis complete (' + score + '% alignment).');
        }}
      }};

      function applySaveVisual(saved) {{
        const label = document.getElementById('save-btn-label');
        const icon = document.getElementById('save-btn-icon');
        const heroBtn = document.getElementById('hero-save-btn');
        if (label) label.textContent = saved ? 'Saved' : 'Save';
        if (icon) icon.className = saved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
        if (heroBtn) {{
          heroBtn.classList.toggle('saved', !!saved);
          const hi = heroBtn.querySelector('i');
          if (hi) hi.className = saved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
        }}
      }}

      window.handleSaveJob = function() {{
        const label = document.getElementById('save-btn-label');
        const wasSaved = label && label.textContent === 'Saved';
        applySaveVisual(!wasSaved);
        const csrfTok = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        fetch('/api/saved/' + jobId + '/toggle', {{
          method: 'POST',
          credentials: 'same-origin',
          headers: Object.assign({{'Content-Type': 'application/json'}}, csrfTok ? {{'X-CSRF-Token': csrfTok}} : {{}}),
          body: '{{}}'
        }})
          .then(async r => {{
            if (r.status === 401) {{
              applySaveVisual(wasSaved);
              window.showToast('Please sign in to save jobs.', true);
              setTimeout(redirectToLogin, 700);
              return null;
            }}
            const data = await r.json();
            if (!r.ok || !data.ok) throw new Error(data.error || 'Could not update saved state.');
            return data;
          }})
          .then(data => {{
            if (!data) return;
            applySaveVisual(!!data.saved);
            window.showToast(data.saved ? 'Job saved to your profile.' : 'Job removed from saved list.');
          }})
          .catch(err => {{
            applySaveVisual(wasSaved);
            window.showToast(err.message || 'Unable to save right now.', true);
          }});
      }};
      window.toggleSaveHeroJob = window.handleSaveJob;

      const form = document.getElementById('form-job-apply');
      if (form) {{
        form.addEventListener('submit', async (ev) => {{
          ev.preventDefault();
          const name = (document.getElementById('apply-input-name')?.value || '').trim();
          const email = (document.getElementById('apply-input-email')?.value || '').trim();
          const phone = (document.getElementById('apply-input-phone')?.value || '').trim();
          const note = (document.getElementById('apply-input-note')?.value || '').trim();
          if (!name || !email) {{
            window.showToast('Please fill in your full name and email.', true);
            return;
          }}
          const submitBtn = document.getElementById('btn-submit-job-apply');
          if (submitBtn) {{
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Submitting...';
          }}
          try {{
            const csrfTok = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            const res = await fetch('/api/apply/' + jobId, {{
              method: 'POST',
              credentials: 'same-origin',
              headers: Object.assign({{'Content-Type': 'application/json'}}, csrfTok ? {{'X-CSRF-Token': csrfTok}} : {{}}),
              body: JSON.stringify({{note: note || (name + ' <' + email + '>' + (phone ? ' · ' + phone : ''))}})
            }});
            if (res.status === 401) {{
              window.showToast('Please sign in to submit your application.', true);
              setTimeout(redirectToLogin, 750);
              return;
            }}
            const data = await res.json();
            if (!res.ok || !data.ok) throw new Error(data.error || 'Application failed.');
            window.closeApplyModal();
            const heroApply = document.getElementById('btn-hero-easy-apply');
            if (heroApply) {{
              heroApply.classList.add('btn-applied-disabled');
              heroApply.innerHTML = '<i class="fa-solid fa-check"></i> <span>Application Submitted</span>';
            }}
            window.showToast(data.already ? 'You already applied — view in Tracker.' : 'Application submitted and saved to Tracker!');
          }} catch (err) {{
            window.showToast(err.message || 'Unable to submit application.', true);
          }} finally {{
            if (submitBtn) {{
              submitBtn.disabled = false;
              submitBtn.innerHTML = '<span>Submit Application</span> &rarr;';
            }}
          }}
        }});
      }}
    }})();
  </script>
  </main>

  <!-- Built In Standard Site Footer -->
  {footer()}
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script src="/static/app.js?v=20261126_perf" defer></script>
</body>
</html>'''
    return html_content


# ---------- salaries ----------

def salaries_page(conn, user, q="", category=""):
    rows = db.list_salaries(conn, q, category)
    max_median = max([r["median"] for r in rows] or [1])
    categories = seed.CATEGORIES
    table_rows = "".join(
        f'''<tr>
          <td><a href="/salaries/{e(slugify(r['title']))}">{e(r['title'])}</a><span>{e(r['category'])}</span></td>
          <td><div class="salary-bar"><i style="width:{round(r['median']/max_median*100)}%"></i></div><span class="range-text">{money(r['low'])} – {money(r['high'])}</span></td>
          <td><strong>{money(r['median'])}</strong></td><td>{thousands(r['samples'])}</td><td class="trend">{e(r['trend'])}</td>
        </tr>''' for r in rows
    ) or '<tr><td colspan="5">No salary data matches your search.</td></tr>'
    body = f'''
    <section class="page-hero salaries-hero"><div class="container">
      {breadcrumb([("Home", "/"), ("Salaries", "")])}
      <h1>US Tech + Startup Salaries</h1><p class="hero-sub">See how your salary stacks up</p>
      <form class="salary-form" method="get" action="/salaries">
        <div class="pill-select large">{icon("layers", 17)}{select("category", categories, category, "Job Category", "auto-submit")}{icon("chevron", 16, "select-caret")}</div>
        <div class="search-input-wrap"><input type="search" name="q" value="{e(q)}" placeholder="Job title, e.g. Software Engineer" aria-label="Job title"></div>
        <button class="btn btn-magenta" type="submit">Compare Salaries {icon("arrow", 16)}</button>
      </form>
    </div></section>
    <section class="section"><div class="container">
      <div class="results-head"><div><h2>Average salaries by role</h2><p>{len(rows)} roles &middot; 2026 compensation benchmarks</p></div><span class="results-count">{len(rows)} results</span></div>
      <div class="table-card"><table class="salary-table"><thead><tr><th>Role</th><th>Salary range</th><th>Median</th><th>Reports</th><th>YoY</th></tr></thead><tbody>{table_rows}</tbody></table></div>
      <div class="info-grid">
        <div class="info-card">{icon("chart", 26)}<h3>How we calculate</h3><p>Median base salary is displayed alongside the typical low-to-high compensation range and report count.</p></div>
        <div class="info-card">{icon("globe", 26)}<h3>Location matters</h3><p>Remote and hybrid policies can shift ranges significantly. Compare offers using both the role and the workplace policy.</p></div>
        <div class="info-card">{icon("sparkle", 26)}<h3>Negotiate with context</h3><p>Use salary ranges alongside benefits, equity and growth opportunities to evaluate the full package.</p></div>
      </div>
      <div class="faq-block"><h2>Salary FAQ</h2>
        <details><summary>What is included in these salaries? {icon("chevron", 18)}</summary><p>Figures reflect base salary bands. Bonus, equity and benefits are detailed on employer profiles.</p></details>
        <details><summary>How often is the data updated? {icon("chevron", 18)}</summary><p>Compensation benchmarks are maintained for 2026 alongside employer compensation records.</p></details>
        <details><summary>Can I compare by category? {icon("chevron", 18)}</summary><p>Yes — use the Job Category filter above, or browse salary detail pages from the table.</p></details>
      </div>
    </div></section>'''
    return layout("US Tech + Startup Salaries", body, user, description="Compare median tech salaries, ranges and market trends by role.")


def salary_detail_page(conn, user, salary, related_jobs):
    other = db.list_salaries(conn, "", salary["category"])[:4]
    body = f'''
    <section class="page-hero"><div class="container">
      {breadcrumb([("Home", "/"), ("Salaries", "/salaries"), (salary["title"], "")])}
      <h1>{e(salary["title"])} Salary</h1><p class="hero-sub">{e(salary["category"])} · United States · 2026</p>
    </div></section>
    <section class="section"><div class="container detail-grid">
      <div class="detail-main">
        <div class="content-card salary-summary"><div><span>Median base salary</span><strong>{money(salary["median"])}</strong><em>{e(salary["trend"])} year over year</em></div>
          <div><span>Typical range</span><strong>{money(salary["low"])} – {money(salary["high"])}</strong><em>{thousands(salary["samples"])} reports</em></div></div>
        <div class="content-card"><h2>About this role</h2><p>{e(salary["title"])} compensation varies with experience, scope, location and company size. Use this sample range as a starting point when comparing offers, then research the specific team and level.</p>
          <h3>Related openings</h3><div class="compact-job-list">{"".join(job_card(j, compact=True) for j in related_jobs) or "<p>No matching roles right now.</p>"}</div></div>
      </div>
      <aside class="detail-side"><div class="side-card"><h3>Other {e(salary["category"])} roles</h3><ul class="mini-list">{"".join(f'<li><a href="/salaries/{e(slugify(o["title"]))}">{e(o["title"])}</a><span>{money(o["median"])}</span></li>' for o in other)}</ul>
        <a class="btn btn-outline btn-block" href="/salaries">All salaries {icon("arrow", 15)}</a></div></aside>
    </div></section>'''
    return layout(f'{salary["title"]} Salary', body, user, description=f"Median salary and range for {salary['title']} roles.")


# ---------- articles ----------

def articles_page(conn, user, q="", category="", tag="", featured=None):
    extra_head = '''<link rel="stylesheet" href="/static/article.css?v=20261127_uniform">
    <style>
      #view-article {
        display: block !important;
        background: #fafafa !important;
        width: 100% !important;
        min-height: 100vh !important;
        padding: 0 0 60px 0 !important;
      }
      #view-article .container,
      #view-article .editorial-carousels-container {
        width: 100% !important;
        max-width: 1200px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
      }
      #view-article .video-card {
        flex: 0 0 calc((100% - 66px) / 4) !important;
        width: calc((100% - 66px) / 4) !important;
      }
      @media (max-width: 900px) {
        #view-article .video-card {
          flex: 0 0 calc((100% - 22px) / 2) !important;
          width: calc((100% - 22px) / 2) !important;
        }
      }
      @media (max-width: 560px) {
        #view-article .video-card {
          flex: 0 0 82vw !important;
          width: 82vw !important;
        }
      }
      .lw-db-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      }
    </style>'''

    has_filter = bool((q or "").strip() or (category or "").strip() or (tag or "").strip())
    if has_filter:
        matched = db.list_articles(conn, q=q, category=category, tag=tag, limit=60)
        cards = "".join(
            f'''<article class="lw-db-card" style="background:#fff;border:1px solid #e2e8f0;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;transition:all 0.2s;">
              <a href="/articles/{e(a['slug'])}" style="display:block;aspect-ratio:16/9;overflow:hidden;background:#f1f5f9;">
                <img src="{e(_article_cover_url(a, i))}" alt="{e(a['title'])}" width="400" height="175" decoding="async" style="width:100%;height:100%;object-fit:cover;display:block;" loading="lazy">
              </a>
              <div style="padding:16px;display:flex;flex-direction:column;gap:8px;flex:1;">
                <div style="font-size:11px;font-weight:700;color:#0284c7;text-transform:uppercase;letter-spacing:0.05em;">{e(a.get('category') or 'Editorial')} &middot; {e(a.get('tag') or 'Article')}</div>
                <h3 style="margin:0;font-size:17px;line-height:1.35;"><a href="/articles/{e(a['slug'])}" style="color:#0f172a;text-decoration:none;">{e(a['title'])}</a></h3>
                <p style="margin:0;font-size:13.5px;color:#475569;line-height:1.5;flex:1;">{e(a.get('excerpt') or '')}</p>
                <div style="font-size:12px;color:#64748b;padding-top:8px;border-top:1px solid #f1f5f9;">{e(a.get('author') or 'Editorial Staff')} &middot; {e(a.get('published') or '')}</div>
              </div>
            </article>''' for i, a in enumerate(matched)
        )
        filter_parts = [p for p in [f'Search: "{q}"' if q else "", category, tag] if p]
        filter_label = " &middot; ".join(e(p) for p in filter_parts)
        results_html = f'<div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(290px, 1fr));gap:20px;">{cards}</div>' if cards else empty_state(
            "No articles match your filter",
            "Try a different search term or reset filters to browse all briefings.",
            "/article-blogs",
            "Browse All Articles",
        )
        body = f'''
        <div id="view-article">
          <div class="container" style="padding:36px 0 60px;">
            <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px;margin-bottom:24px;border-bottom:2px solid #0f172a;padding-bottom:14px;">
              <div>
                <h1 style="margin:0;font-size:28px;color:#0f172a;">Articles &amp; Briefings</h1>
                <p style="margin:6px 0 0;color:#475569;font-size:14px;">{len(matched)} matching articles ({filter_label})</p>
              </div>
              <form method="get" action="/article-blogs" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                <input type="search" name="q" value="{e(q)}" placeholder="Search articles..." style="padding:9px 14px;border:1px solid #cbd5e1;border-radius:6px;font-size:14px;min-width:220px;">
                <button class="btn btn-primary btn-sm" type="submit">Filter</button>
                <a class="btn btn-outline btn-sm" href="/article-blogs">Clear Filters</a>
              </form>
            </div>
            {results_html}
          </div>
        </div>
        '''
        return layout("Articles & Briefings", body, user, active="articles",
                      page_class="page-article-blogs",
                      description="Search articles, industry briefings, and logistics intelligence.",
                      extra_head=extra_head)

    hub_file = STATIC / "article_blogs.html"
    hub_content = ""
    if hub_file.is_file():
        try:
            with open(hub_file, "r", encoding="utf-8") as f:
                hub_content = f.read()
        except Exception as ex:
            hub_content = f"<!-- Error loading editorial hub: {ex} -->"

    latest_editorial = conn.execute(
        """SELECT id, slug, title, category, tag, thumb, accent FROM articles
           WHERE COALESCE(is_today, 0) = 0
           ORDER BY id DESC LIMIT 4"""
    ).fetchall()
    if latest_editorial and '<div class="nav-cards">' in hub_content:
        nav_cards_html = []
        for idx, r in enumerate(latest_editorial):
            a = dict(r)
            slug = a.get("slug") or f"article-{a['id']}"
            title = a.get("title") or "Editorial Briefing"
            cat = a.get("category") or a.get("tag") or "Logistics"
            thumb = _article_cover_url(a, idx)
            nav_cards_html.append(f'''<article class="card">
<a class="card-media" href="/articles/{e(slug)}"><img alt="{e(title)}" src="{e(thumb)}" decoding="async" width="674" height="368" loading="lazy"/></a>
<span class="cat">{e(cat)}</span>
<h3><a href="/articles/{e(slug)}">{e(title)}</a></h3>
</article>''')
        hub_content = re.sub(
            r'<div class="nav-cards">.*?</div>',
            '<div class="nav-cards">\n' + "\n".join(nav_cards_html) + '\n</div>',
            hub_content,
            count=1,
            flags=re.DOTALL,
        )

    today_articles = conn.execute(
        """SELECT id, slug, title, excerpt, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest FROM articles 
           WHERE is_today = 1
              OR tag IN ('Logistic Waves Today', 'Logistic Wave Today')
              OR category IN ('Logistic Waves Today', 'Logistic Wave Today')
           ORDER BY id DESC LIMIT 12"""
    ).fetchall()

    if today_articles and '<div class="carousel-track" id="carouselTrack">' in hub_content:
        cards_html = []
        for r in today_articles:
            a = dict(r)
            slug = a.get("slug") or f"article-{a['id']}"
            title = a.get("title") or "Logistic Waves Today"
            thumb = a.get("thumb") or "/static/images/fw_today_1.jpg"
            date = a.get("published") or ""
            excerpt = a.get("excerpt") or ""
            cards_html.append(f'''<article class="video-card">
<a class="video-media" href="/articles/{e(slug)}"><img alt="{e(title)}" src="{e(thumb)}" width="320" height="190" loading="lazy" decoding="async"><span class="play"></span></a>
<span class="cat">Logistic Wave Today</span>
<h3><a href="/articles/{e(slug)}">{e(title)}</a></h3>
<div class="date">{e(date)}</div>
<p>{e(excerpt)}</p>
<a class="read-more" href="/articles/{e(slug)}">Read more…</a>
</article>''')
        dynamic_track = '<div class="carousel-track" id="carouselTrack">\n' + "\n".join(cards_html) + '\n</div>\n</div>'
        track_pattern = re.compile(r'<div class="carousel-track" id="carouselTrack">.*?</div>\s*</div>', re.DOTALL)
        hub_content = track_pattern.sub(dynamic_track, hub_content, count=1)

    body = f'''
    <div id="view-article">
      {hub_content}
    </div>
    '''
    return layout("Articles & Logistics Intelligence", body, user, active="articles",
                  page_class="page-article-blogs",
                  description="Leading logistics, maritime shipping news, Logistic Wave intelligence, video broadcasts, and freight market analysis.",
                  extra_head=extra_head)


def format_editorial_body(raw_body):
    raw_body = (raw_body or "").strip()
    if not raw_body:
        return ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw_body) if b.strip()]
    out = []
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        img_matches = [re.match(r"^!\[(.*?)\]\((.*?)\)$", l) for l in lines]
        # Multi-image gallery (2 or more photos together)
        if all(img_matches) and len(img_matches) > 1:
            grid_items = []
            for m in img_matches:
                cap = m.group(1).strip()
                src = safe_media_url(m.group(2).strip())
                if not src:
                    continue
                grid_items.append(f'''
                <figure style="margin:0;display:flex;flex-direction:column;">
                  <img src="{e(src)}" alt="{e(cap or 'Article Photo')}" width="400" height="260" decoding="async" style="width:100%;aspect-ratio:16/9;height:auto;object-fit:cover;border-radius:14px;box-shadow:0 4px 16px rgba(0,0,0,0.06);display:block;" loading="lazy">
                  {f'<figcaption style="font-size:12.5px;color:#64748b;margin-top:7px;font-style:italic;text-align:center;">{e(cap)}</figcaption>' if cap else ''}
                </figure>''')
            if grid_items:
                out.append(f'''
            <div class="editorial-image-gallery" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin:32px 0;">
              {"".join(grid_items)}
            </div>''')
            continue

        img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", block)
        if img_match:
            cap = img_match.group(1).strip()
            src = safe_media_url(img_match.group(2).strip())
            if src:
                out.append(f'''
            <figure class="editorial-inline-figure" style="margin:28px 0;">
              <img src="{e(src)}" alt="{e(cap or 'Article Image')}" class="editorial-inline-image" width="800" height="450" decoding="async" style="width:100%;aspect-ratio:16/9;max-height:460px;object-fit:cover;border-radius:14px;box-shadow:0 4px 20px rgba(0,0,0,0.08);display:block;" loading="lazy">
              {f'<figcaption class="editorial-inline-caption" style="font-size:13px;color:#64748b;margin-top:8px;font-style:italic;text-align:center;">{e(cap)}</figcaption>' if cap else ''}
            </figure>''')
            continue
        if block.startswith("### "):
            out.append(f'<h3 class="editorial-subheading" style="font-size:19px;font-weight:700;color:#0f172a;margin:28px 0 12px;">{e(block[4:])}</h3>')
            continue
        if block.startswith("## "):
            out.append(f'<h2 class="editorial-subheading" style="font-size:24px;font-weight:800;color:#0f172a;margin:34px 0 14px;">{e(block[3:])}</h2>')
            continue
        if block.startswith("# "):
            out.append(f'<h2 class="editorial-subheading" style="font-size:26px;font-weight:800;color:#0f172a;margin:36px 0 16px;">{e(block[2:])}</h2>')
            continue
        if block.startswith("> "):
            out.append(f'''
            <blockquote class="editorial-pull-quote" style="border-left:4px solid #3874ff;padding:14px 22px;margin:28px 0;background:#f0f7ff;border-radius:0 10px 10px 0;">
              <p class="editorial-quote-p" style="font-size:16px;font-weight:600;color:#1e3a8a;margin:0;">{e(block[2:].strip())}</p>
            </blockquote>''')
            continue
        out.append(f'<p class="editorial-para" style="font-size:16.5px;line-height:1.8;color:#334155;margin-bottom:22px;">{e(block)}</p>')
    return "".join(out)



# Module-level constant: preset metadata for featured articles
EDITORIAL_PRESETS = {
    "the-2026-state-of-tech-salaries": {
        "hero_img": "/static/images/editorial_tech_salaries_hd.png",
        "hero_caption": "Global technology compensation benchmarks reflect skyrocketing premiums for specialized AI and distributed systems engineers. (Photo: Tech Intelligence Global Desk)",
        "kicker_pill": "SPECIAL INVESTIGATION",
        "topic_tag": "COMPENSATION & TALENT",
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        "author_role": "Editor-in-Chief · Tech Intelligence Desk",
        "author_bio": "Investigative tech columnist and contributor specializing in distributed engineering compensation, cloud infrastructure economics, and enterprise foundation models.",
        "readers": "18,900 readers",
        "sub_1": "The Macro Shift in Engineering Compensation & AI Specialization",
        "sub_2": "High-Concurrency vs. Generalist Development Demand",
        "sub_3": "Global Tax Treaties & Cross-Border Equity Realities",
        "sub_4": "What Engineering Leaders Are Prioritizing for 2026",
        "inline_img1": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
        "inline_cap1": "Infrastructure scaling and GPU scheduling clusters are driving massive capital investments across multinational computing facilities. (Photo: Cloud Insights)",
        "inline_img2": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
        "inline_cap2": "Collaborative systems engineering teams are transitioning from monoliths to event-driven compound architectures. (Photo: Logistic Waves)",
        "stats": [
            ("2.4x", "Premium for Distributed Systems"),
            ("+28%", "YoY Senior Systems Pay Surge"),
            ("$380k+", "Median Staff Total Package"),
            ("1,200", "Tech Organizations Surveyed")
        ],
        "quote_text": "Companies that attempt to compensate high-concurrency systems engineers at standard web developer bands are experiencing near 100% offer rejection rates. The talent market has definitively spoken.",
        "quote_cite": "Sarah Jenkins — GitLab Head of Talent",
        "tags": ["TechSalaries2026", "DistributedSystems", "EngineeringCompensation", "AIEngineering", "EquityPackages"],
        "sources": "Sources & Fact Verification: Cross-referenced against 1,200 verified corporate payroll datasets, SEC Form 10-K disclosures, and candidate placement offer records across Tier-1 technology hubs."
    },
    "cross-border-tech-hiring": {
        "hero_img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
        "hero_caption": "Multinational tech enterprises navigate shifting bilateral tax treaties and cross-border IP licensing agreements. (Photo: Global Policy Desk)",
        "kicker_pill": "POLICY & REMOTE TRENDS",
        "topic_tag": "GLOBAL WORKFORCE",
        "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
        "author_role": "Global Policy Desk & Compensation Analysts",
        "author_bio": "Specializing in international labor compliance, cross-border corporate taxation, and asynchronous talent management frameworks.",
        "readers": "12,450 readers",
        "sub_1": "OECD 2026 Economic Nexus Regulations & Permanent Establishment Thresholds",
        "sub_2": "The Surge in Direct Multi-Currency & Equity Compensation",
        "sub_3": "Mitigating Permanent Establishment (PE) Risk in Remote Clusters",
        "sub_4": "Structuring Compliant Contracts across Southeast Asia and the US",
        "inline_img1": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1200&q=80",
        "inline_cap1": "Cross-border legal and payroll frameworks must balance local social security mandates with competitive USD-denominated compensation packages. (Photo: Financial Gazette)",
        "inline_img2": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1200&q=80",
        "inline_cap2": "Distributed engineering headquarters in Singapore, Ho Chi Minh City, and Tokyo continue to attract top-tier remote talent. (Photo: Asia Tech Chronicle)",
        "stats": [
            ("45", "Bilateral Treaties Modernized"),
            ("62%", "Tech Firms with Multi-Country R&D"),
            ("183 Days", "Strict Physical Nexus Limit"),
            ("2.4x", "Surge in Direct Multi-Currency Payroll")
        ],
        "quote_text": "Engineering leaders can no longer treat international tax and labor compliance as an afterthought. Designing tax-optimized, legally resilient contracts is now as vital as software architecture.",
        "quote_cite": "Logistic Waves — Global Policy Desk",
        "tags": ["RemoteHiring", "TaxTreaties", "GlobalTalent", "Compliance2026", "CrossBorderPayroll"],
        "sources": "Sources & Fact Verification: OECD International Tax Directives (2026 Revision), ASEAN Digital Economic Integration Framework, and primary filings across 45 national labor ministries."
    },
    "gitlab-autonomous-ai-duo": {
        "hero_img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
        "hero_caption": "GitLab showcases autonomous agentic workflows integrating code review, vulnerability mitigation, and CI/CD pipelines. (Photo: GitLab DevSecOps)",
        "kicker_pill": "AUTONOMOUS DEV WORKFLOWS",
        "topic_tag": "ARTIFICIAL INTELLIGENCE",
        "author_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80",
        "author_role": "Principal AI Researcher & DevSecOps Contributor",
        "author_bio": "Author and machine learning systems engineer focused on autonomous agentic development, compiler optimizations, and automated vulnerability triage.",
        "readers": "14,800 readers",
        "sub_1": "From Code Autocomplete to Autonomous Agent Orchestration",
        "sub_2": "Automating Vulnerability Patching in Production Pipelines",
        "sub_3": "Developer Sentiment and the Future of Pull Request Velocity",
        "sub_4": "Enterprise Governance and Guardrails for Autonomous Agents",
        "inline_img1": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
        "inline_cap1": "Cloud-native CI/CD runners process automated test suites generated by agentic orchestration models. (Photo: Cloud World)",
        "inline_img2": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80",
        "inline_cap2": "Engineers review multi-modal agent suggestions with complete git commit history and audit trails. (Photo: AI Dev Insights)",
        "stats": [
            ("4.8x", "Faster Pull Request Resolution"),
            ("78%", "Automated Security Patch Rate"),
            ("99.2%", "Static Analysis Precision"),
            ("14k+", "Organizations Enrolled in Beta")
        ],
        "quote_text": "The next frontier in software engineering is not writing code faster; it is enabling autonomous agents to verify, secure, and deliver features while humans focus on high-level architecture.",
        "quote_cite": "Sarah Jenkins — GitLab Principal AI Researcher",
        "tags": ["AutonomousAI", "DevSecOps", "GitLabDuo", "SoftwareEngineering", "AIAgents"],
        "sources": "Sources & Fact Verification: GitLab Enterprise Benchmark Suite, Autonomous Code Completion Field Reports (Q3 2026), and developer telemetry across 14,000 corporate repositories."
    }
}

def article_detail_page(conn, user, article, related):
    slug = article.get("slug") or "article"
    title = article.get("title") or "Editorial Briefing"
    category = article.get("category") or "Industry"
    author = article.get("author") or "Editorial Staff"
    published = article.get("published") or "November 04, 2026"
    read_time = article.get("read_time") or "7 min read"
    excerpt = article.get("excerpt") or "In-depth investigation and industry intelligence."
    
    # 1. Preset Rich Metadata — loaded from module-level constant
    editorial_presets = EDITORIAL_PRESETS

    # Fallback preset for all other articles in database
    default_meta = {
        "hero_img": _article_cover_url(article, 0),
        "hero_caption": f"{title} ({category})",
        "kicker_pill": category.upper(),
        "topic_tag": category.upper(),
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        "author_role": f"{category} Contributor",
        "author_bio": f"Contributor covering {category.lower()} analysis, operations, and industry developments.",
        "readers": "",
        "sub_1": f"Overview: {category}",
        "sub_2": "Key Operational Developments",
        "sub_3": "Industry Outlook",
        "sub_4": "What Comes Next",
        "inline_img1": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
        "inline_cap1": "",
        "inline_img2": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1200&q=80",
        "inline_cap2": "",
        "stats": [],
        "quote_text": excerpt,
        "quote_cite": author,
        "tags": [category.replace(" ", ""), "LogisticWaves"],
        "sources": ""
    }

    meta = editorial_presets.get(slug)
    is_preset = (meta is not None)
    if not meta:
        meta = default_meta.copy()
    else:
        meta = meta.copy()

    if article.get("thumb"):
        meta["hero_img"] = article.get("thumb")
    if article.get("tag") == "Logistic Waves Today" or article.get("category") == "Logistic Waves Today":
        meta["kicker_pill"] = "LOGISTIC WAVES TODAY · VIDEO BROADCAST"
        meta["topic_tag"] = "DAILY LOGISTICS INTELLIGENCE"
        meta["readers"] = f"{article.get('read_time', '15 min')}"
        guest_name = article.get("guest") or article.get("author") or "Featured Guest"
        meta["author_role"] = f"Featured Guest: {guest_name}"
        meta["quote_text"] = article.get("excerpt") or ""
        meta["quote_cite"] = f"{article.get('author')} — Executive Briefing"
        meta["tags"] = ["LogisticWavesToday", "Aviation", "Maritime", "SupplyChain", "Mobility2026"]

    # 2. Extract or format paragraphs
    raw_body = article.get("body") or ""
    clean_body = re.sub(r"<[^>]+>", "", raw_body)
    body_paras = [p.strip() for p in re.split(r"\n\s*\n", clean_body) if p.strip()]
    custom_body_html = format_editorial_body(raw_body)
    if custom_body_html and (not is_preset or len(raw_body) > 350):
        story_inner_html = f'''
        <p class="editorial-lead-para" style="font-size:18px;font-weight:500;line-height:1.75;color:#1e293b;margin-bottom:26px;">{e(excerpt)}</p>
        {custom_body_html}
        '''
    elif is_preset and len(body_paras) >= 2:
        lead_para = body_paras[0]
        story_inner_html = f'''
        <p class="editorial-lead-para">{e(lead_para)}</p>
        {"".join(f'<p class="editorial-para">{e(p)}</p>' for p in body_paras[1:])}
        <blockquote class="editorial-pull-quote">
          <p class="editorial-quote-p">{e(meta["quote_text"])}</p>
          <cite class="editorial-quote-cite">{e(meta["quote_cite"])}</cite>
        </blockquote>
        '''
    else:
        story_inner_html = f'<p class="editorial-lead-para" style="font-size:18px;font-weight:500;line-height:1.75;color:#1e293b;margin-bottom:26px;">{e(excerpt)}</p>' 

    # 3. Stat Card HTML
    stat_cells_html = "".join(f'''
      <div class="stat-metric-cell">
        <div class="stat-metric-val">{s_val}</div>
        <div class="stat-metric-lbl">{s_lbl}</div>
      </div>''' for s_val, s_lbl in meta["stats"])

    # 4. Tags HTML
    tags_html = "".join(f'''
      <a href="{url('/article-blogs', q=t)}" class="tag-pill-link">#{e(t)}</a>''' for t in meta["tags"])

    # 5. Right-Hand Popular / Recommended Articles Sidebar (Matching User Reference)
    sidebar_articles = [db.as_dict(r) for r in conn.execute(
        "SELECT * FROM articles WHERE id != ? ORDER BY id DESC LIMIT 8", (article["id"],)
    ).fetchall()]

    # Featured top popular card
    feat_card = sidebar_articles[0] if sidebar_articles else article
    feat_slug = feat_card.get("slug") or "article"
    feat_title = feat_card.get("title") or "Industry Briefing"
    feat_pub = feat_card.get("published") or ""
    feat_time = feat_card.get("read_time") or ""
    feat_img = e(_article_cover_url(feat_card, 0))

    # Popular list items (thumbs left, title right)
    sidebar_items_html = []
    for s_idx, s_art in enumerate(sidebar_articles[1:], start=1):
        s_slug = s_art.get("slug") or "article"
        s_title = s_art.get("title") or "Industry Report"
        s_cat = s_art.get("category") or "Editorial"
        s_time = s_art.get("read_time") or ""
        s_thumb = e(_article_cover_url(s_art, s_idx))

        sidebar_items_html.append(f'''
        <a href="/articles/{e(s_slug)}" class="sidebar-popular-item">
          <div class="sidebar-item-thumb-wrap">
            <img src="{s_thumb}" alt="{e(s_title)}" class="sidebar-item-thumb" width="96" height="66" loading="lazy" decoding="async">
          </div>
          <div class="sidebar-item-content">
            <h4 class="sidebar-item-title">{e(s_title)}</h4>
            <div class="sidebar-item-meta">
              <span class="sidebar-meta-cat">{e(s_cat)}</span>
              <span class="sidebar-meta-dot">&bull;</span>
              <span class="sidebar-meta-time">{e(s_time)}</span>
            </div>
          </div>
        </a>''')

    body = f'''
    <!-- 1. Breadcrumb Bar -->
    <div class="article-breadcrumb-bar">
      <div class="container article-breadcrumb-inner">
        <a href="/">Home</a>
        <span class="crumb-sep">/</span>
        <a href="/article-blogs">News &amp; Articles</a>
        <span class="crumb-sep">/</span>
        <a href="/article-blogs?category={e(category)}">{e(category)}</a>
        <span class="crumb-sep">/</span>
        <span class="crumb-current">{e(title)}</span>
      </div>
    </div>

    <!-- 2. Editorial Canvas with 2-Column Responsive Layout -->
    <article class="article-detail-page-container">
      <div class="editorial-canvas-wrapper">
        <div class="container editorial-two-col-container">

          <!-- MAIN LEFT COLUMN: Article Content -->
          <div class="editorial-main-column">

            <!-- Category Badge (Matching User's Reference) & Topic Row -->
            <div class="editorial-kicker-row">
              <span class="editorial-category-badge">{e(category)}</span>
              <span class="editorial-topic-text">{e(meta["topic_tag"])}</span>
            </div>

            <!-- Main Headline -->
            <h1 class="editorial-star-headline">{e(title)}</h1>

            <!-- Excerpt Lead -->
            <p class="editorial-excerpt-lead">{e(excerpt)}</p>

            <!-- Author Byline Bar -->
            <div class="editorial-byline-bar">
              <div class="byline-left">
                <img src="{meta["author_avatar"]}" alt="{e(author)}" class="byline-avatar" width="40" height="40" decoding="async" data-fallback-kind="avatar">
                <div class="byline-meta-text">
                  <div class="byline-author-name">{e(author)}</div>
                  <div class="byline-sub-role">{e(meta["author_role"])}</div>
                </div>
              </div>
              <div class="byline-right-meta">
                <span class="byline-timestamp"><i class="fa-regular fa-calendar"></i> {e(published)}</span>
                <span class="byline-read-time"><i class="fa-regular fa-clock"></i> {e(read_time)}</span>
                {f'<span class="byline-readers-count"><i class="fa-solid fa-eye"></i> {e(meta["readers"])}</span>' if meta.get("readers") else ''}
              </div>
            </div>

            <!-- Audio Listen Bar (Matching User's Screenshot Exactly) -->
            <div class="article-audio-bar">
              <button type="button" class="audio-play-btn" id="audioToggleBtn" onclick="toggleArticleAudio()" aria-label="Listen to audio briefing">
                <i class="fa-solid fa-play" id="audioPlayIcon"></i>
              </button>
              <div class="audio-track-wrap">
                <div class="audio-track-fill" id="audioTrackFill" style="width: 24%;"></div>
              </div>
              <span class="audio-time-label" id="audioTimeLabel">00:35 / 02:38</span>
              <div class="audio-volume-badge"><i class="fa-solid fa-volume-high"></i></div>
            </div>

            <!-- Social Share Bar -->
            <div class="editorial-share-bar">
              <div class="share-links-group">
                <span style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;">Share this article:</span>
                <a href="https://twitter.com/intent/tweet?text={e(title)}" target="_blank" rel="noopener" class="share-btn">
                  <i class="fa-brands fa-x-twitter"></i> Share to X
                </a>
                <a href="https://www.linkedin.com/sharing/share-offsite/" target="_blank" rel="noopener" class="share-btn">
                  <i class="fa-brands fa-linkedin"></i> LinkedIn
                </a>
                <a href="https://www.facebook.com/sharer/sharer.php" target="_blank" rel="noopener" class="share-btn">
                  <i class="fa-brands fa-facebook"></i> Facebook
                </a>
                <button type="button" class="share-btn" onclick="navigator.clipboard.writeText(window.location.href); if(window.showToast) window.showToast('Article link copied to clipboard!');">
                  <i class="fa-regular fa-copy"></i> Copy Link
                </button>
              </div>
            </div>

            <!-- Hero Media Figure with Caption -->
            <figure class="editorial-hero-figure">
              <img src="{meta["hero_img"]}" alt="{e(title)}" class="editorial-hero-image" width="800" height="450" decoding="async" fetchpriority="high">
              <figcaption class="editorial-hero-caption">{meta["hero_caption"]}</figcaption>
            </figure>

            <!-- Story Narrative Body -->
            <div class="editorial-story-body">
              {story_inner_html}
              <!-- Tags Strip -->
              <div class="editorial-tags-strip">
                <span class="tags-label"><i class="fa-solid fa-tags" style="color: #0284c7; margin-right: 4px;"></i> Related Topics:</span>
                {tags_html}
              </div>

              <!-- Author Bio Card -->
              <div class="editorial-author-card">
                <img src="{meta["author_avatar"]}" alt="{e(author)}" class="author-card-avatar" width="64" height="64" loading="lazy" decoding="async" data-fallback-kind="avatar">
                <div class="author-card-info">
                  <h4 class="author-card-name">{e(author)}</h4>
                  <div class="author-card-role">{e(meta["author_role"])}</div>
                  <p class="author-card-bio">{e(meta["author_bio"])}</p>
                </div>
              </div>

            </div>

          </div>

          <!-- RIGHT SIDEBAR COLUMN: Popular & Related Stories (Matching User's Example) -->
          <aside class="editorial-sidebar-column">
            
            <div class="sidebar-popular-block">
              <h3 class="sidebar-popular-header">Popular</h3>
              
              <!-- Top Featured Popular Card (Large Image with Title Overlay) -->
              <a href="/articles/{e(feat_slug)}" class="sidebar-popular-hero">
                <div class="sidebar-hero-media">
                  <img src="{feat_img}" alt="{e(feat_title)}" class="sidebar-hero-img" width="350" height="200" loading="lazy" decoding="async">
                  <div class="sidebar-hero-overlay">
                    <h4 class="sidebar-hero-headline">{e(feat_title)}</h4>
                    <div class="sidebar-hero-date">
                      <span><i class="fa-regular fa-calendar"></i> {e(feat_pub)}</span>
                      <span><i class="fa-regular fa-clock"></i> {e(feat_time)}</span>
                    </div>
                  </div>
                </div>
              </a>

              <!-- Popular Stories Vertical List (Thumb left, title right) -->
              <div class="sidebar-popular-list">
                {"".join(sidebar_items_html)}
              </div>

            </div>

          </aside>

        </div>
      </div>
    </article>

    <script>
      let isAudioPlaying = false;
      let synthUtterance = null;
      function toggleArticleAudio() {{
        const btn = document.getElementById('audioToggleBtn');
        const icon = document.getElementById('audioPlayIcon');
        const fill = document.getElementById('audioTrackFill');
        const timeLbl = document.getElementById('audioTimeLabel');
        
        if (!('speechSynthesis' in window)) {{
          if (window.showToast) window.showToast('Audio reader is unavailable in this browser.', true);
          return;
        }}

        if (!isAudioPlaying) {{
          window.speechSynthesis.cancel();
          const headline = document.querySelector('.editorial-star-headline');
          const lead = document.querySelector('.editorial-excerpt-lead');
          const textToRead = (headline ? headline.innerText : '') + '. ' + (lead ? lead.innerText : '');
          synthUtterance = new SpeechSynthesisUtterance(textToRead);
          synthUtterance.rate = 1.0;
          synthUtterance.onstart = function() {{
            isAudioPlaying = true;
            if (icon) icon.className = 'fa-solid fa-pause';
            if (fill) fill.style.width = '65%';
            if (timeLbl) timeLbl.innerText = '01:15 / 02:38';
          }};
          synthUtterance.onend = function() {{
            isAudioPlaying = false;
            if (icon) icon.className = 'fa-solid fa-play';
            if (fill) fill.style.width = '100%';
            if (timeLbl) timeLbl.innerText = '02:38 / 02:38';
          }};
          synthUtterance.onerror = function() {{
            isAudioPlaying = false;
            if (icon) icon.className = 'fa-solid fa-play';
          }};
          window.speechSynthesis.speak(synthUtterance);
        }} else {{
          window.speechSynthesis.cancel();
          isAudioPlaying = false;
          if (icon) icon.className = 'fa-solid fa-play';
        }}
      }}
    </script>
    '''
    return layout(title, body, user, active="articles", description=excerpt)



# ---------- discovery pages ----------

def tech_hubs_page(conn, user, hub=None):
    if hub:
        jobs, total = db.list_jobs(conn, {"location": hub["name"].split(",")[0]}, limit=6)
        companies, _ = db.list_companies(conn, {"location": hub["name"].split(",")[0]}, limit=4)
        body = f'''
        <section class="page-hero"><div class="container">{breadcrumb([("Home", "/"), ("Tech Hubs", "/tech-hubs"), (hub["name"], "")])}
          <h1>Tech Jobs in {e(hub["name"])}</h1><p class="hero-sub">{thousands(hub["jobs"])} open roles across {thousands(hub["companies"])} employers</p></div></section>
        <section class="section"><div class="container"><div class="results-head"><h2>Recent roles</h2><a class="btn btn-outline" href="{url('/jobs', location=hub['name'].split(',')[0])}">Search jobs {icon("arrow", 15)}</a></div>
          <div class="job-list">{"".join(job_card(j) for j in jobs) or empty_state('No sample jobs in this hub', 'Try the full job search instead.')}</div>
          <h2 class="section-title">Companies to know</h2><div class="hub-company-grid">{"".join(f'<a class="hub-company" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<span>{e(c["name"])}</span></a>' for c in companies)}</div>
        </div></section>'''
        return layout(f'Tech Hub: {hub["name"]}', body, user, description=f"Tech jobs and companies in {hub['name']}.")
    cards = "".join(
        f'''<a class="hub-card" style="--hub:{e(h['color'])}" href="/tech-hubs/{e(h['slug'])}">
          <span class="hub-icon">{icon("building", 24)}</span><h3>{e(h["name"])}</h3>
          <p>{thousands(h["jobs"])} jobs · {thousands(h["companies"])} companies</p><span class="hub-arrow">{icon("arrow", 18)}</span></a>'''
        for h in seed.TECH_HUBS
    )
    body = f'''
    <section class="page-hero"><div class="container">{breadcrumb([("Home", "/"), ("Tech Hubs", "")])}
      <h1>Tech Hubs Across the U.S.</h1><p class="hero-sub">Explore the cities shaping the next generation of technology work.</p></div></section>
    <section class="section"><div class="container"><div class="hub-grid">{cards}</div></div></section>'''
    return layout("Tech Hubs", body, user, description="Explore tech jobs and companies by city.")


def dictionary_page(conn, user, q=""):
    entries = [(a, b, c) for a, b, c in seed.DICTIONARY if not q or q.lower() in (a + b + c).lower()]
    items = "".join(
        f'<div class="dict-entry" data-term="{e((a + " " + b + " " + c).lower())}"><div class="dict-letter">{e(a[0])}</div><div><h3>{e(a)} <span>{e(b)}</span></h3><p>{e(c)}</p></div></div>'
        for a, b, c in entries
    ) or empty_state("No definitions found", "Try a different term.", "/tech-dictionary", "All terms")
    body = f'''
    <section class="page-hero"><div class="container">{breadcrumb([("Home", "/"), ("Tech Dictionary", "")])}
      <h1>Tech Dictionary</h1><p class="hero-sub">Plain-English definitions for the words you hear in every standup.</p>
      <form class="dict-search" method="get" action="/tech-dictionary">{icon("search", 20)}<input type="search" name="q" value="{e(q)}" placeholder="Search a term, acronym or concept" aria-label="Search dictionary"><button class="btn btn-magenta" type="submit">Search</button></form>
    </div></section>
    <section class="section"><div class="container narrow"><div class="dict-list">{items}</div></div></section>'''
    return layout("Tech Dictionary", body, user, description="A plain-English glossary of technology terms.")


COURSE_LINES = [
    {
        "id": "line-freightwaves",
        "title": "Logistic Wave Today",
        "courses": [
            {
                "id": "fw-1",
                "title": "Logistic Wave Today | November 3",
                "date": "Nov 4, 2026",
                "duration": "24m",
                "thumb": "/static/images/fw_today_1.svg",
                "desc": "Freight markets are tightening, diesel prices are creating new challenges for carriers, and the latest economic indicators suggest shifting contract volumes across national routes.",
                "link_text": "Read more...",
                "channel": "Logistic Wave Media",
                "instructor": "Andy Kuchar • Senior Market Analyst",
                "avatar": "/static/images/expert_david.png",
                "chapters": [
                    {"title": "1. Market Overview & Spot Rate Fluctuations", "duration": "06:15"},
                    {"title": "2. Outbound Tender Volume Index (OTVI) Analysis", "duration": "08:40"},
                    {"title": "3. Carrier Capacity & Rejection Rates", "duration": "09:05"}
                ]
            },
            {
                "id": "fw-2",
                "title": "Diesel Prices Collapse, Then Rebound: What's Driving Volatility?",
                "date": "Nov 4, 2026",
                "duration": "18m",
                "thumb": "/static/images/fw_today_2.svg",
                "desc": "The diesel market is experiencing extreme volatility, dropping sharply then rebounding on geopolitical news. Zach Strickland breaks down refinery spreads and wholesale impacts.",
                "link_text": "Read more...",
                "channel": "Logistic Wave SONAR",
                "instructor": "Zach Strickland • Market Expert",
                "avatar": "/static/images/expert_marcus.png",
                "chapters": [
                    {"title": "1. Global Crude Benchmark Movements", "duration": "05:10"},
                    {"title": "2. Refinery Crack Spreads & Inventory Levels", "duration": "07:20"},
                    {"title": "3. Surcharge Forecasting for Fleets", "duration": "05:30"}
                ]
            },
            {
                "id": "fw-3",
                "title": "Why Your Trucking Insurance Costs Are Rising & How to Fight Back",
                "date": "Nov 4, 2026",
                "duration": "22m",
                "thumb": "/static/images/fw_today_3.svg",
                "desc": "Control your trucking insurance costs by focusing on risk reduction before losses occur. Peter Niro from Progressive Insurance shares underwriting metrics and safety tips.",
                "link_text": "Read more...",
                "channel": "Logistic Wave Today",
                "instructor": "Peter Niro • Risk Specialist",
                "avatar": "/static/images/expert_david_full.png",
                "chapters": [
                    {"title": "1. Underwriting Climate & Nuclear Verdicts", "duration": "06:45"},
                    {"title": "2. Telematics & Dashcam Premium Discounts", "duration": "08:15"},
                    {"title": "3. Driver Safety Audit Checklists", "duration": "07:00"}
                ]
            },
            {
                "id": "fw-4",
                "title": "Logistics Alert: Capacity SHRINKS for 11 Straight Months",
                "date": "Nov 4, 2026",
                "duration": "19m",
                "thumb": "/static/images/fw_today_4.svg",
                "desc": "The latest ISM Manufacturing PMI and LMI reports confirm what many in logistics already feel: demand is strong, but capacity is heavily constrained across dry van and reefer.",
                "link_text": "Read more...",
                "channel": "SONAR Market Intelligence",
                "instructor": "Julie Van De Kamp • VP Logistics",
                "avatar": "/static/images/expert_elina.png",
                "chapters": [
                    {"title": "1. Logistics Managers' Index (LMI) Breakdown", "duration": "05:50"},
                    {"title": "2. Warehousing Space Utilization & Costs", "duration": "07:30"},
                    {"title": "3. Contract Pricing Strategy for Q1", "duration": "05:40"}
                ]
            },
            {
                "id": "fw-5",
                "title": "Truckload Rates Explode: How Shippers Adapt to Rising Costs",
                "date": "Nov 4, 2026",
                "duration": "26m",
                "thumb": "/static/images/fw_today_5.svg",
                "desc": "The freight market is experiencing an inflationary leg in its current cycle, pushing truckload rates up over 4% across major lanes. Chris Pickett details defensive routing strategies.",
                "link_text": "Read more...",
                "channel": "Logistic Wave Today",
                "instructor": "Chris Pickett • Chief Strategy Officer",
                "avatar": "/static/images/expert_marcus_full.png",
                "chapters": [
                    {"title": "1. Rate Benchmarking Across Golden Triangle Lanes", "duration": "08:10"},
                    {"title": "2. Dedicated Fleet Conversion ROI", "duration": "09:30"},
                    {"title": "3. Mini-Bids & Spot Market Hedging", "duration": "08:20"}
                ]
            },
            {
                "id": "fw-6",
                "title": "Global Ocean Freight & Port Operations Engineering",
                "date": "Nov 4, 2026",
                "duration": "4h 50m",
                "thumb": "/static/images/yt_thumb_1.jpg",
                "desc": "Master container alliance freight routing, deep-draft terminal berthing, customs EDI clearance with VNACCS, Incoterms 2020 legal obligations, and demurrage dispute arbitration.",
                "link_text": "Read more...",
                "channel": "Viconship Supply Chain Guild",
                "instructor": "David Sterling • VP Terminal Operations",
                "avatar": "/static/images/expert_david.png",
                "chapters": [
                    {"title": "1. Ocean Freight Alliances & Vessel Berthing Windows", "duration": "18:20"},
                    {"title": "2. Container Yard Optimization with Navis N4 Systems", "duration": "27:45"},
                    {"title": "3. Customs Clearance EDI, Bonded Warehousing & Demurrage", "duration": "31:10"}
                ]
            }
        ]
    },
    {
        "id": "line-ai",
        "title": "AI & Autonomous Systems Masterclasses",
        "courses": [
            {
                "id": "ai-1",
                "title": "Autonomous Multi-Agent AI Systems & LLMOps",
                "date": "Nov 4, 2026",
                "duration": "6h 45m",
                "thumb": "/static/images/editorial_laptop_dashboard.jpg",
                "desc": "Learn to architect, evaluate, and orchestrate autonomous multi-agent loops in production CI/CD pipelines. Covers LangGraph swarm dynamics, function calling, vector RAG retrieval, and enterprise guardrails.",
                "link_text": "Read more...",
                "channel": "GitLab DevSecOps Institute",
                "instructor": "Dr. Sarah Jenkins • Lead AI Systems Architect",
                "avatar": "/static/images/expert_sarah.png",
                "chapters": [
                    {"title": "1. ReAct Loops & Autonomous Tool Calling Fundamentals", "duration": "14:20"},
                    {"title": "2. High-Dimension RAG Retrieval & Vector Chunking", "duration": "28:45"},
                    {"title": "3. LangGraph Swarm Consensus & State Machines", "duration": "34:10"},
                    {"title": "4. Automated PR Generation, Self-Healing Code & Tests", "duration": "42:30"}
                ]
            },
            {
                "id": "ai-2",
                "title": "Generative AI with PyTorch, CUDA & TensorRT",
                "date": "Nov 4, 2026",
                "duration": "11h 10m",
                "thumb": "/static/images/course_2.jpg",
                "desc": "From FlashAttention-3 kernels to multi-GPU pipeline parallelism: pretraining decoder transformers, LoRA/QLoRA parameter-efficient fine-tuning, and speculative decoding.",
                "link_text": "Read more...",
                "channel": "OpenAI Research Community",
                "instructor": "Dr. Sarah Jenkins • Principal AI Research Scientist",
                "avatar": "/static/images/expert_sarah_full.png",
                "chapters": [
                    {"title": "1. FlashAttention GPU Memory Hierarchies & Kernel Fusion", "duration": "32:15"},
                    {"title": "2. Distributed Tensor Parallelism with Megatron-LM", "duration": "46:40"},
                    {"title": "3. LoRA, QLoRA & 4-bit Quantization Math", "duration": "36:20"}
                ]
            },
            {
                "id": "ai-3",
                "title": "Machine Learning for Autonomous Vehicles & Robotics",
                "date": "Nov 4, 2026",
                "duration": "9h 30m",
                "thumb": "/static/images/yt_thumb_3.jpg",
                "desc": "Design real-time object detection models for LiDAR, RADAR, and multi-camera sensor fusion pipelines. Covers Kalman filtering, ROS 2 robotics middleware, and Edge TPUs.",
                "link_text": "Read more...",
                "channel": "General Motors Mobility AI",
                "instructor": "David Sterling • Robotics & Computer Vision Lead",
                "avatar": "/static/images/expert_david.png",
                "chapters": [
                    {"title": "1. Sensor Fusion: Camera, Radar & 3D LiDAR Point Clouds", "duration": "26:30"},
                    {"title": "2. Real-Time 3D Bounding Box Regression with PointPillars", "duration": "38:15"},
                    {"title": "3. Extended Kalman Filters & SLAM State Estimation", "duration": "44:00"}
                ]
            },
            {
                "id": "ai-4",
                "title": "Clinical Genomics & Healthcare Data Intelligence",
                "date": "Nov 4, 2026",
                "duration": "7h 30m",
                "thumb": "/static/images/course_1.jpg",
                "desc": "Analyze whole-genome sequencing (WGS) variant calls, patient cohort stratification models, HIPAA-compliant bioinformatics pipelines, and multimodal medical image diagnosis.",
                "link_text": "Read more...",
                "channel": "Pfizer Digital Research",
                "instructor": "Elena Rostova • Director of Computational Biology",
                "avatar": "/static/images/expert_elina.png",
                "chapters": [
                    {"title": "1. Next-Generation Sequencing Telemetry & Variant Calling", "duration": "22:15"},
                    {"title": "2. Clinical Data Standards: FHIR, HL7 & HIPAA Guardrails", "duration": "29:40"},
                    {"title": "3. Deep Learning on Histopathology & Medical Imaging", "duration": "36:10"}
                ]
            },
            {
                "id": "ai-5",
                "title": "High-Performance LLM Serving & Model Inference",
                "date": "Nov 4, 2026",
                "duration": "5h 15m",
                "thumb": "/static/images/topic_real_2.jpg",
                "desc": "Deploy ultra-low latency vLLM and TensorRT-LLM inference engines on Kubernetes with speculative decoding, continuous batching, and KV-cache optimization.",
                "link_text": "Read more...",
                "channel": "Logistic Waves Academy",
                "instructor": "Alex Mercer • Lead MLOps Engineer",
                "avatar": "/static/images/expert_sarah.png",
                "chapters": [
                    {"title": "1. Continuous Batching & PagedAttention Internals", "duration": "24:30"},
                    {"title": "2. Speculative Decoding with Draft Models", "duration": "28:15"},
                    {"title": "3. Multi-GPU vLLM Deployments on Kubernetes", "duration": "31:00"}
                ]
            }
        ]
    },
    {
        "id": "line-cloud",
        "title": "Cloud Architecture & DevOps Series",
        "courses": [
            {
                "id": "cloud-1",
                "title": "Kubernetes, Terraform & Cloud Native DevOps",
                "date": "Nov 4, 2026",
                "duration": "10h 15m",
                "thumb": "/static/images/live_player.jpg",
                "desc": "Production infrastructure automation from scratch: multi-region Kubernetes clusters, GitOps continuous delivery with ArgoCD, eBPF telemetry, and zero-downtime canary rollouts.",
                "link_text": "Read more...",
                "channel": "Datadog Cloud Academy",
                "instructor": "Marcus Vance • Director of Cloud Infrastructure",
                "avatar": "/static/images/expert_marcus.png",
                "chapters": [
                    {"title": "1. Declarative Infrastructure with Terraform & OpenTofu", "duration": "22:10"},
                    {"title": "2. Kubernetes Cluster Internals & CNI Networking Deep Dive", "duration": "35:40"},
                    {"title": "3. GitOps Deployment Pipelines with ArgoCD & Helm Charts", "duration": "29:15"}
                ]
            },
            {
                "id": "cloud-2",
                "title": "Distributed Systems & High-Concurrency Rust",
                "date": "Nov 4, 2026",
                "duration": "7h 50m",
                "thumb": "/static/images/yt_thumb_4.jpg",
                "desc": "Master memory safety without garbage collection: Tokio asynchronous runtime, Raft consensus consensus engines, distributed key-value stores, and SIMD optimizations.",
                "link_text": "Read more...",
                "channel": "ByteDance Systems Labs",
                "instructor": "David Sterling • Staff Systems Engineer",
                "avatar": "/static/images/expert_david_full.png",
                "chapters": [
                    {"title": "1. Ownership, Borrow Checker & Unsafe Rust Demystified", "duration": "20:45"},
                    {"title": "2. Asynchronous Event Loops with Tokio & Futures", "duration": "31:10"},
                    {"title": "3. Raft Leader Election, Log Replication & Heartbeats", "duration": "45:30"}
                ]
            },
            {
                "id": "cloud-3",
                "title": "Enterprise Cybersecurity, Zero Trust & DevSecOps",
                "date": "Nov 4, 2026",
                "duration": "5h 40m",
                "thumb": "/static/images/course_3.jpg",
                "desc": "Implement zero-trust security postures: mutual TLS (mTLS), SPIFFE/SPIRE workload identities, runtime container defense with Falco, and OWASP Top 10 API mitigations.",
                "link_text": "Read more...",
                "channel": "Axon Defense Cyber Lab",
                "instructor": "Marcus Vance • Chief Information Security Architect",
                "avatar": "/static/images/expert_marcus_full.png",
                "chapters": [
                    {"title": "1. BeyondCorp Architecture: Zero Trust Workload Principles", "duration": "16:20"},
                    {"title": "2. Mutual TLS, Certificate Authority PKI & SPIFFE Identities", "duration": "28:30"},
                    {"title": "3. Runtime Kernel Tracing with Falco & eBPF Security Probes", "duration": "34:15"}
                ]
            },
            {
                "id": "cloud-4",
                "title": "Modern Full-Stack Architecture with React 19 & Next.js",
                "date": "Nov 4, 2026",
                "duration": "8h 45m",
                "thumb": "/static/images/lead_story.jpg",
                "desc": "Deep dive into production web architecture: React Server Components, server actions, streaming SSR, PostgreSQL database indexing, Redis session management, and edge deployment.",
                "link_text": "Read more...",
                "channel": "Logistic Waves Academy",
                "instructor": "Dr. Sarah Jenkins • VP Engineering & Web Architect",
                "avatar": "/static/images/expert_sarah.png",
                "chapters": [
                    {"title": "1. React 19 RSC Mental Model & Streaming SSR Architecture", "duration": "24:10"},
                    {"title": "2. Server Actions, Optimistic UI & Mutations Without Client JS", "duration": "31:40"},
                    {"title": "3. High-Performance PostgreSQL Indexing & Connection Pooling", "duration": "39:15"}
                ]
            },
            {
                "id": "cloud-5",
                "title": "High-Performance Document Databases & NoSQL Internals",
                "date": "Nov 4, 2026",
                "duration": "5h 25m",
                "thumb": "/static/images/contest_banner.jpg",
                "desc": "Master enterprise document modeling, distributed replica set quorum, shard key selection strategies, aggregation pipeline optimizations, and native vector search.",
                "link_text": "Read more...",
                "channel": "MongoDB Developer Guild",
                "instructor": "Marcus Vance • Staff Database Systems Architect",
                "avatar": "/static/images/expert_marcus.png",
                "chapters": [
                    {"title": "1. Document Schema Antipatterns & Polymorphic Modeling", "duration": "18:30"},
                    {"title": "2. Sharding Topologies, Chunks & Distributed Balancing", "duration": "31:45"},
                    {"title": "3. Multi-Stage Aggregation Pipeline Performance Tuning", "duration": "25:20"}
                ]
            }
        ]
    },
    {
        "id": "line-fintech",
        "title": "Fintech, Payment Rails & Stream Processing",
        "courses": [
            {
                "id": "fin-1",
                "title": "Fintech Payment Rails & Real-Time Processing",
                "date": "Nov 4, 2026",
                "duration": "8h 20m",
                "thumb": "/static/images/yt_thumb_2.jpg",
                "desc": "Architect high-concurrency double-entry transaction ledgers, idempotent webhook consumers, ISO 20022 message parsers, and fault-tolerant financial settlement rails under strict compliance.",
                "link_text": "Read more...",
                "channel": "Stripe Developer Platform",
                "instructor": "Elena Rostova • Principal Fintech Architect",
                "avatar": "/static/images/expert_elina.png",
                "chapters": [
                    {"title": "1. Double-Entry Accounting Ledgers & Exact-Once Semantics", "duration": "18:15"},
                    {"title": "2. Card Networks, Interchange Mechanics & Real-Time ACH", "duration": "24:30"},
                    {"title": "3. PCI-DSS Level 1 Cryptography, Vaults & Tokenization", "duration": "32:00"}
                ]
            },
            {
                "id": "fin-2",
                "title": "Real-Time Stream Processing with Apache Flink & Kafka",
                "date": "Nov 4, 2026",
                "duration": "6h 15m",
                "thumb": "/static/images/yt_thumb_5.jpg",
                "desc": "Construct low-latency streaming analytics platforms: event-time processing, sliding session windows, checkpointing recovery algorithms, and real-time fraud scoring.",
                "link_text": "Read more...",
                "channel": "Grab Platform Guild",
                "instructor": "Elena Rostova • Staff Data Infrastructure Engineer",
                "avatar": "/static/images/expert_elina_full.png",
                "chapters": [
                    {"title": "1. Event Time, Processing Time & Watermark Propagation", "duration": "19:40"},
                    {"title": "2. Stateful Stream Processing & RocksDB Checkpointing", "duration": "33:15"},
                    {"title": "3. Joining High-Velocity Streams & Dynamic CEP Patterns", "duration": "28:50"}
                ]
            },
            {
                "id": "fin-3",
                "title": "Double-Entry Accounting Ledgers & Idempotent Systems",
                "date": "Nov 4, 2026",
                "duration": "4h 40m",
                "thumb": "/static/images/topic_real_1.jpg",
                "desc": "Design resilient financial transaction ledgers with strict ACID guarantees, multi-region replication, and automated reconciliation against banking network clearings.",
                "link_text": "Read more...",
                "channel": "Stripe Engineering Guild",
                "instructor": "Liam Chen • Senior Financial Systems Engineer",
                "avatar": "/static/images/expert_sarah.png",
                "chapters": [
                    {"title": "1. Immutable Ledger Entries & Debit-Credit Balances", "duration": "16:40"},
                    {"title": "2. Distributed Locking & Consensus on Hot Accounts", "duration": "22:15"},
                    {"title": "3. Automated Reconciliation Pipelines with Apache Spark", "duration": "26:30"}
                ]
            },
            {
                "id": "fin-4",
                "title": "PCI-DSS Compliance, Key Vaults & HSM Cryptography",
                "date": "Nov 4, 2026",
                "duration": "5h 10m",
                "thumb": "/static/images/topic_real_3.jpg",
                "desc": "Master hardware security module (HSM) integration, end-to-end tokenization vaults, and payment compliance architectures for multi-currency digital checkout systems.",
                "link_text": "Read more...",
                "channel": "Modern Banking Guild",
                "instructor": "Elena Rostova • Principal Architect",
                "avatar": "/static/images/expert_elina.png",
                "chapters": [
                    {"title": "1. HSM Key Custody, Pin Blocks & AES-GCM Encryption", "duration": "18:20"},
                    {"title": "2. Tokenization Vault Isolation & Ephemeral Card Pan", "duration": "24:10"},
                    {"title": "3. Zero-Knowledge Auditing for Global Card Brands", "duration": "20:30"}
                ]
            },
            {
                "id": "fin-5",
                "title": "The Logistics of Amazon Deliveries & Real-Time Tracking",
                "date": "Nov 4, 2026",
                "duration": "3h 50m",
                "thumb": "/static/images/course_4.jpg",
                "desc": "Inspect real-time package tracking architectures, automated fulfillment center robotics, and last-mile route-optimization algorithms at hyperscale.",
                "link_text": "Read more...",
                "channel": "Supply Chain Engineering Guild",
                "instructor": "David Sterling • Logistics Lead",
                "avatar": "/static/images/expert_david.png",
                "chapters": [
                    {"title": "1. Fulfillment Center Robotics & Sortation Matrix", "duration": "15:20"},
                    {"title": "2. Last-Mile Dispatching & Traveling Salesperson Routing", "duration": "21:40"},
                    {"title": "3. Real-Time Telematics & Delivery ETA Prediction", "duration": "18:00"}
                ]
            }
        ]
    }
]

# Flatten all courses for easy modal lookup
ALL_COURSES = {}
for line in COURSE_LINES:
    for c in line["courses"]:
        ALL_COURSES[c["id"]] = c


def courses_page(conn, user, f=None):
    # Render lines of course lessons matching the Logistic Wave / simple carousel look
    lines_html = []
    for line in COURSE_LINES:
        line_id = line["id"]
        cards_html = []
        for c in line["courses"]:
            cid = c["id"]
            cards_html.append(f'''
            <article class="course-simple-card" onclick="openCourseModal(\'{cid}\');">
              <div class="course-simple-thumb">
                <img src="{e(c["thumb"])}" alt="{e(c["title"])}" width="480" height="270" loading="lazy" decoding="async">
                <button class="course-share-btn" type="button" onclick="event.stopPropagation(); shareCourse(\'{e(c["title"])}\');" title="Share lesson">
                  <i class="fa-solid fa-arrow-up-from-bracket"></i>
                </button>
                <span class="course-thumb-duration">{e(c["duration"])}</span>
              </div>
              <div class="course-simple-info">
                <h3 class="course-simple-title">{e(c["title"])}</h3>
                <div class="course-simple-meta">{e(c["date"])}</div>
                <p class="course-simple-desc">{e(c["desc"])}</p>
                <a class="course-read-more" href="javascript:void(0);" onclick="event.stopPropagation(); openCourseModal(\'{cid}\');">{e(c["link_text"])}</a>
              </div>
            </article>
            ''')

        cards_row = "".join(cards_html)
        lines_html.append(f'''
        <section class="course-line-section">
          <div class="course-line-header">
            <h2 class="course-line-title">{e(line["title"])}</h2>
            <div class="course-nav-controls">
              <button class="course-nav-btn prev-btn" type="button" onclick="scrollCourseLine(\'{line_id}\', -1);" aria-label="Previous">
                <i class="fa-solid fa-chevron-left"></i>
              </button>
              <button class="course-nav-btn next-btn" type="button" onclick="scrollCourseLine(\'{line_id}\', 1);" aria-label="Next">
                <i class="fa-solid fa-chevron-right"></i>
              </button>
            </div>
          </div>
          <div class="course-line-row" id="{line_id}" onscroll="updateScrollTrack(\'{line_id}\');">
            {cards_row}
          </div>
          <div class="course-scroll-indicator">
            <i class="fa-solid fa-chevron-left course-arrow-icon"></i>
            <div class="course-scroll-track">
              <div class="course-scroll-thumb" id="thumb-{line_id}"></div>
            </div>
            <i class="fa-solid fa-chevron-right course-arrow-icon"></i>
          </div>
        </section>
        ''')

    all_lines_html = "".join(lines_html)
    courses_lookup_json = json.dumps(ALL_COURSES)

    body = f'''
    <div class="course-simple-page">
      <!-- Clean Minimal Header (No dark hero banner) -->
      <div class="course-page-top">
        <div class="container">
          <div class="course-header-flex">
            <div>
              <h1 class="course-main-heading">Courses &amp; Masterclasses</h1>
              <p class="course-sub-heading">Browse engineering video series, systems architectures, and industry deep dives.</p>
            </div>
            <div class="course-quick-search">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input type="text" id="courseSimpleSearch" placeholder="Search lessons, instructors..." oninput="filterSimpleCourses();" autocomplete="off">
            </div>
          </div>
        </div>
      </div>

      <!-- Lines of Course Lessons -->
      <div class="container">
        {all_lines_html}
      </div>
    </div>

    <!-- Interactive Watch Modal -->
    <div class="course-modal-backdrop" id="courseModalBackdrop" onclick="handleModalBackdropClick(event);">
      <div class="course-modal-dialog">
        <div class="course-modal-header">
          <div class="course-modal-brand">
            <i class="fa-solid fa-circle-play" style="color:#ff0000;font-size:16px;"></i>
            <span>Tech Masterclass Player</span>
          </div>
          <button class="course-modal-close" type="button" onclick="closeCourseModal();" aria-label="Close">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
        <div class="course-modal-body">
          <div class="course-player-side">
            <div class="course-screen-box">
              <img src="/static/images/editorial_laptop_dashboard.jpg" alt="Preview" id="modalVideoPoster" width="840" height="472" loading="lazy" decoding="async">
              <div class="course-screen-overlay">
                <span style="background:rgba(0,0,0,0.7);padding:3px 8px;border-radius:4px;font-size:11px;color:#38bdf8;font-weight:700;align-self:flex-start;">HD 1080p</span>
                <div class="course-screen-play-btn" onclick="toggleModalPlay();">
                  <i class="fa-solid fa-play" id="modalPlayIcon"></i>
                </div>
                <div class="course-screen-controls">
                  <div class="course-screen-scrubber">
                    <div class="course-screen-fill" id="modalProgressFill" style="width:35%;"></div>
                  </div>
                  <div class="course-screen-bar">
                    <span id="modalTimeCounter" style="font-size:12px;color:#cbd5e1;">04:15 / 24:00</span>
                    <span style="font-size:11px;background:rgba(255,255,255,0.15);padding:2px 6px;border-radius:4px;">1.0x</span>
                  </div>
                </div>
              </div>
            </div>
            <div style="margin-top:16px;">
              <h2 id="modalTitle" style="font-size:18px;font-weight:800;color:#ffffff;margin:0 0 8px;line-height:1.35;">Course Title</h2>
              <div style="font-size:12px;color:#94a3b8;margin-bottom:12px;" id="modalMeta">Channel • Instructor</div>
              <p id="modalDesc" style="font-size:13px;line-height:1.55;color:#cbd5e1;margin:0;"></p>
            </div>
          </div>
          <div class="course-playlist-side">
            <div class="course-playlist-header">
              <i class="fa-solid fa-list-ul" style="margin-right:6px;color:#38bdf8;"></i> Lesson Chapters
            </div>
            <div class="course-playlist-list" id="modalChaptersList">
            </div>
          </div>
        </div>
      </div>
    </div>

    <script>
      (function() {{
        const COURSES_LOOKUP = {courses_lookup_json};
        let isPlaying = false;
        let progressTimer = null;
        let curProgress = 35;

        window.scrollCourseLine = function(lineId, dir) {{
          const el = document.getElementById(lineId);
          if (!el) return;
          const scrollAmount = 260 * 2;
          el.scrollBy({{ left: dir * scrollAmount, behavior: "smooth" }});
        }};

        window.updateScrollTrack = function(lineId) {{
          const el = document.getElementById(lineId);
          const thumb = document.getElementById("thumb-" + lineId);
          if (!el || !thumb) return;
          const maxScroll = el.scrollWidth - el.clientWidth;
          if (maxScroll <= 0) {{
            thumb.style.left = "0px";
            return;
          }}
          const pct = el.scrollLeft / maxScroll;
          const maxLeft = 100 - 40;
          thumb.style.left = (pct * maxLeft) + "px";
        }};

        window.openCourseModal = function(courseId) {{
          const c = COURSES_LOOKUP[courseId];
          if (!c) return;

          document.getElementById("modalTitle").textContent = c.title;
          document.getElementById("modalVideoPoster").src = c.thumb;
          document.getElementById("modalMeta").textContent = c.channel + " • " + c.instructor + " • " + c.duration;
          document.getElementById("modalDesc").textContent = c.desc;
          document.getElementById("modalTimeCounter").textContent = "00:00 / " + c.duration;

          const chaptersList = document.getElementById("modalChaptersList");
          if (c.chapters && c.chapters.length) {{
            chaptersList.innerHTML = c.chapters.map((ch, idx) => `
              <div class="course-playlist-item${{idx === 0 ? " active" : ""}}" onclick="selectModalChapter(this, '${{ch.title.replace(/'/g, "\\\'")}}', '${{ch.duration}}');">
                <div class="course-item-thumb">
                  <img src="${{c.thumb}}" alt="Thumb" width="100" height="56" loading="lazy" decoding="async">
                </div>
                <div style="flex:1;min-width:0;">
                  <div class="course-item-title">${{ch.title}}</div>
                  <div class="course-item-duration">${{ch.duration}}</div>
                </div>
              </div>
            `).join("");
          }} else {{
            chaptersList.innerHTML = `
              <div class="course-playlist-item active">
                <div class="course-item-thumb"><img src="${{c.thumb}}" alt="Thumb" width="100" height="56" loading="lazy" decoding="async"></div>
                <div style="flex:1;min-width:0;">
                  <div class="course-item-title">Full Video Masterclass</div>
                  <div class="course-item-duration">${{c.duration}}</div>
                </div>
              </div>
            `;
          }}

          const modal = document.getElementById("courseModalBackdrop");
          modal.classList.add("active");
          document.body.style.overflow = "hidden";
        }};

        window.closeCourseModal = function() {{
          const modal = document.getElementById("courseModalBackdrop");
          if (modal) modal.classList.remove("active");
          document.body.style.overflow = "";
          pauseModalPlay();
        }};

        window.handleModalBackdropClick = function(e) {{
          if (e.target.id === "courseModalBackdrop") window.closeCourseModal();
        }};

        window.selectModalChapter = function(item, title, duration) {{
          document.querySelectorAll(".course-playlist-item").forEach(el => el.classList.remove("active"));
          item.classList.add("active");
          document.getElementById("modalTitle").textContent = title;
          document.getElementById("modalTimeCounter").textContent = "00:00 / " + duration;
          curProgress = 0;
          updateModalProgress(0);
          startModalPlay();
        }};

        window.toggleModalPlay = function() {{
          if (isPlaying) pauseModalPlay();
          else startModalPlay();
        }};

        function startModalPlay() {{
          isPlaying = true;
          const iconEl = document.getElementById("modalPlayIcon");
          if (iconEl) iconEl.className = "fa-solid fa-pause";
          if (progressTimer) clearInterval(progressTimer);
          progressTimer = setInterval(() => {{
            curProgress += 0.5;
            if (curProgress > 100) curProgress = 0;
            updateModalProgress(curProgress);
          }}, 500);
        }}

        function pauseModalPlay() {{
          isPlaying = false;
          const iconEl = document.getElementById("modalPlayIcon");
          if (iconEl) iconEl.className = "fa-solid fa-play";
          if (progressTimer) {{
            clearInterval(progressTimer);
            progressTimer = null;
          }}
        }}

        function updateModalProgress(pct) {{
          const el = document.getElementById("modalProgressFill");
          if (el) el.style.width = pct + "%";
        }}

        window.shareCourse = function(title) {{
          if (navigator.clipboard) navigator.clipboard.writeText(window.location.href);
          if (typeof window.showToast === "function") window.showToast('Course link copied: "' + title + '"');
        }};

        window.filterSimpleCourses = function() {{
          const q = (document.getElementById("courseSimpleSearch").value || "").trim().toLowerCase();
          document.querySelectorAll(".course-simple-card").forEach(card => {{
            const text = card.textContent.toLowerCase();
            card.style.display = (!q || text.includes(q)) ? "flex" : "none";
          }});
        }};

        document.addEventListener("keydown", (e) => {{
          if (e.key === "Escape") window.closeCourseModal();
        }});
      }})();
    </script>
    '''

    extra_css = '<link rel="stylesheet" href="/static/courses.css?v=20261127_no_play">';
    return layout("Engineering Courses & Masterclasses", body, user, active="courses", page_class="course-simple-page", description="Browse video courses and engineering lessons.", extra_head=extra_css)


def awards_page(conn, user, city=None):
    companies, _ = db.list_companies(conn, {"hiring": "1"}, limit=6)
    award_cards = "".join(
        f'<a class="award-link" href="/awards/{e(slug)}/current/best-places-to-work"><span>{icon("trophy", 18)} {e(title)}</span>{icon("arrow", 18)}</a>'
        for title, slug, _ in seed.AWARDS
    )
    winner_cards = "".join(
        f'<a class="winner-card" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<div><strong>{e(c["name"])}</strong><span>{e(c["location"])} · {thousands(c["employees"])} employees</span></div><span class="rank">#{i+1}</span></a>'
        for i, c in enumerate(companies)
    )
    title = "Best Places To Work" if not city else f'Best Places To Work in {city.replace("-", " ").title()}'
    body = f'''
    <section class="page-hero awards-hero"><div class="container">{breadcrumb([("Home", "/"), ("Best Places To Work", "/awards"), (title if city else "2026", "")])}
      <span class="hero-badge light">{icon("star", 15)} 2026 Awards</span><h1>{e(title)}</h1>
      <p class="hero-sub">Celebrating employers that set the standard for culture, compensation and growth.</p></div></section>
    <section class="section"><div class="container detail-grid"><div class="detail-main">
      <div class="content-card"><h2>2026 winners</h2><div class="winner-list">{winner_cards}</div></div>
      <div class="content-card"><h2>Explore awards by location</h2><div class="award-grid">{award_cards}</div></div>
    </div><aside class="detail-side"><div class="side-card"><h3>How winners are chosen</h3><p>Rankings evaluate employer benefits, workplace policies, active hiring volume, and team signals.</p><a class="btn btn-outline btn-block" href="/companies">Explore companies</a></div></aside></div></section>'''
    return layout(title, body, user, description="Explore best places to work awards and top employers.")


def remote_page(conn, user):
    jobs, total = db.list_jobs(conn, {"remote": "1"}, limit=6)
    companies, ctotal = db.list_companies(conn, {"remote": "1"}, limit=4)
    body = f'''
    <section class="page-hero remote-hero"><div class="container">{breadcrumb([("Home", "/"), ("Remote", "")])}
      <h1>Remote Tech Jobs &amp; Companies</h1><p class="hero-sub">Find distributed teams, fully remote employers and work-from-anywhere roles.</p>
      <div class="hero-buttons"><a class="btn btn-magenta btn-lg" href="/jobs/remote">SEE ALL REMOTE JOBS</a><a class="btn btn-white btn-lg" href="/companies/location/fully-remote">FULLY REMOTE COMPANIES</a></div></div></section>
    <section class="section"><div class="container"><div class="results-head"><h2>Recently posted remote roles</h2><span class="results-count">{total} remote jobs</span></div>
      <div class="job-list">{"".join(job_card(j) for j in jobs)}</div>
      <h2 class="section-title">Remote-friendly companies</h2><div class="hub-company-grid">{"".join(f'<a class="hub-company" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<span>{e(c["name"])}</span></a>' for c in companies)}</div>
    </div></section>'''
    return layout("Remote Tech Jobs", body, user, description="Browse remote jobs and fully remote companies.")


def search_page(conn, user, q):
    results = db.global_search(conn, q, 12)
    jobs, total = db.list_jobs(conn, {"q": q}, limit=8)
    body = f'''
    <section class="page-hero"><div class="container">{breadcrumb([("Home", "/"), ("Search", "")])}
      <h1>Search results for “{e(q)}”</h1><p class="hero-sub">Matching jobs, companies, and articles across Logistic Waves.</p>
      <form method="get" action="/search" class="article-search">{icon("search", 18)}<input type="search" name="q" value="{e(q)}" placeholder="Search everything"><button class="btn btn-magenta btn-sm" type="submit">Search</button></form>
    </div></section>
    <section class="section"><div class="container">
      <div class="search-result-columns">
        <div><h2>Companies</h2>{''.join(f'<a class="search-result" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<span>{e(c["name"])}<small>{e(c["location"])}</small></span></a>' for c in results["companies"]) or '<p>No company matches.</p>'}</div>
        <div><h2>Articles</h2>{''.join(f'<a class="search-result" href="/articles/{e(a["slug"])}">{icon("book", 22)}<span>{e(a["title"])}<small>{e(a["category"])}</small></span></a>' for a in results["articles"]) or '<p>No article matches.</p>'}</div>
      </div>
      <h2 class="section-title">Matching jobs</h2><div class="job-list">{"".join(job_card(j) for j in jobs) or empty_state('No matching jobs', 'Try a broader keyword.')}</div>
    </div></section>'''
    return layout(f'Search: {q or "Everything"}', body, user, description=f"Search results for {q}.")


# ---------- account pages ----------

def auth_page(kind, next_path="", error="", message="", preset_role="candidate"):
    is_login = kind == "login"
    title = "Log In" if is_login else "Join Logistic Waves"
    action = "/auth/login" if is_login else "/auth/signup"
    title_text = "Welcome back" if is_login else "Create an account"
    subtitle_text = "Sign in to continue your journey." if is_login else "Start your global logistics journey today."
    switch_prefix = "Don't have an account yet?" if is_login else "Already have an account?"
    switch_label = "Create an account" if is_login else "Sign in"
    switch_href = e(url("/auth/signup", next=next_path)) if is_login else e(url("/auth/login", next=next_path))
    submit_btn_text = "Sign In" if is_login else "Create Account"
    
    if preset_role not in ("candidate", "employer", "admin"):
        preset_role = "candidate"
        
    signup_name_field = "" if is_login else f'''
      <div class="auth-input-group">
        <div class="auth-input-wrapper">
          <i class="fa-regular fa-user input-leading-icon"></i>
          <input id="nameInput" type="text" name="name" class="auth-field-control" placeholder="Enter your full name" required autocomplete="name">
        </div>
      </div>'''

    err_html = f'''
      <div class="auth-alert-box alert-error">
        <i class="fa-solid fa-circle-exclamation"></i>
        <span>{e(error)}</span>
      </div>''' if error else ""
      
    msg_html = f'''
      <div class="auth-alert-box alert-success">
        <i class="fa-solid fa-circle-check"></i>
        <span>{e(message)}</span>
      </div>''' if message else ""

    body = f'''
    <style>
      :root {{
        --header-promo-offset: 0px !important;
      }}
      body.auth-page-shell {{
        background: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
      }}
      /* Standard site header & promo bar are preserved cleanly */
      body.auth-page-shell footer {{
        display: none !important;
      }}
      body.auth-page-shell #main-content {{
        flex: 1 0 auto !important;
        display: flex !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
      }}

      /* Standard site header is preserved without shape distortions */
      body.auth-page-shell .site-header {{
        /* Keeps official site header brand styling and standard container layout */
      }}

      /* Split Screen Layout (Balanced 50/50 Half-and-Half) */
      .auth-split-wrapper {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        width: 100% !important;
        min-height: calc(100vh - 110px) !important;
        background: #ffffff !important;
      }}

      /* Left Hero Panel (Clean Cinematic Port Visual - Zero Text Overlay) */
      .auth-split-hero {{
        position: relative !important;
        background: url("/static/images/login_concept_hero_bg.jpg") center center / cover no-repeat !important;
        min-height: 520px !important;
        overflow: hidden !important;
      }}
      .sr-only {{
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0,0,0,0) !important;
        border: 0 !important;
      }}

      /* Right Card Column (Form) */
      .auth-split-card-col {{
        background: #f8fafc !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 36px 32px !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
      }}
      .auth-card-inner {{
        width: 100% !important;
        max-width: 440px !important;
        margin: 0 auto !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px !important;
        padding: 36px 36px 32px !important;
        box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04) !important;
        box-sizing: border-box !important;
      }}
      .auth-brand-badge {{
        display: flex !important;
        align-items: center !important;
        gap: 9px !important;
        margin-bottom: 12px !important;
      }}
      .auth-brand-logo-img {{
        width: 28px !important;
        height: 28px !important;
        object-fit: contain !important;
      }}
      .auth-brand-title {{
        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 0.04em !important;
        color: #003875 !important;
      }}
      .auth-form-title {{
        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 0 0 4px !important;
        letter-spacing: -0.03em !important;
        line-height: 1.15 !important;
      }}
      .auth-form-subtitle {{
        font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 14px !important;
        color: #64748b !important;
        margin: 0 0 16px !important;
      }}

      /* Role Selector Tabs (Job Seeker / Employer) */
      .auth-role-tabs {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 6px !important;
        background: #f1f5f9 !important;
        padding: 4px !important;
        border-radius: 9999px !important;
        margin-bottom: 16px !important;
      }}
      .role-tab {{
        border: none !important;
        background: transparent !important;
        padding: 9px 16px !important;
        border-radius: 9999px !important;
        font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
      }}
      .role-tab.active {{
        background: #0060cc !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0, 96, 204, 0.25) !important;
      }}

      
      /* Inputs */
      .auth-input-group {{
        margin-bottom: 12px !important;
      }}
      .auth-input-wrapper {{
        position: relative !important;
        display: flex !important;
        align-items: center !important;
      }}
      .input-leading-icon {{
        position: absolute !important;
        left: 16px !important;
        font-size: 15px !important;
        color: #94a3b8 !important;
        pointer-events: none !important;
      }}
      .auth-field-control {{
        width: 100% !important;
        height: 48px !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0 16px 0 44px !important;
        font-size: 14.5px !important;
        color: #0f172a !important;
        background: #ffffff !important;
        box-sizing: border-box !important;
        outline: none !important;
        transition: all 0.2s ease !important;
      }}
      .auth-field-control:focus {{
        border-color: #0060cc !important;
        box-shadow: 0 0 0 3.5px rgba(0, 96, 204, 0.12) !important;
      }}
      .auth-field-control.has-toggle {{
        padding-right: 48px !important;
      }}
      .pwd-toggle-btn {{
        position: absolute !important;
        right: 12px !important;
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        cursor: pointer !important;
        padding: 6px !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: color 0.15s ease !important;
      }}
      .pwd-toggle-btn:hover {{
        color: #0f172a !important;
      }}

      /* Meta Options (Remember me / Forgot password) */
      .auth-meta-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin: 10px 0 16px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
        gap: 10px !important;
      }}
      .auth-remember-checkbox {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        user-select: none !important;
      }}
      .auth-remember-checkbox input[type="checkbox"] {{
        width: 16px !important;
        height: 16px !important;
        accent-color: #0060cc !important;
        cursor: pointer !important;
        margin: 0 !important;
      }}
      .auth-forgot-link {{
        color: #0060cc !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        font-size: 13px !important;
      }}
      .auth-forgot-link:hover {{
        text-decoration: underline !important;
      }}

      /* Submit Button */
      .auth-submit-btn {{
        width: 100% !important;
        height: 48px !important;
        background: #0060cc !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 14px rgba(0, 96, 204, 0.3) !important;
      }}
      .auth-submit-btn:hover {{
        background: #004fb0 !important;
        box-shadow: 0 6px 18px rgba(0, 96, 204, 0.45) !important;
        transform: translateY(-1px) !important;
      }}
      .auth-submit-btn .btn-arrow {{
        display: inline-block !important;
        transition: transform 0.2s ease !important;
      }}
      .auth-submit-btn:hover .btn-arrow {{
        transform: translateX(4px) !important;
      }}

      /* SSO Divider */
      .auth-sso-divider {{
        display: flex !important;
        align-items: center !important;
        text-align: center !important;
        margin: 14px 0 10px !important;
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
      }}
      .auth-sso-divider::before,
      .auth-sso-divider::after {{
        content: "" !important;
        flex: 1 !important;
        border-bottom: 1px solid #e2e8f0 !important;
      }}
      .auth-sso-divider span {{
        padding: 0 12px !important;
      }}

      /* SSO Row */
      .auth-sso-row {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 12px !important;
        margin-bottom: 16px !important;
      }}
      .sso-btn {{
        height: 46px !important;
        background: #ffffff !important;
        border: 1.5px solid #d0dce8 !important;
        border-radius: 24px !important;
        padding: 0 16px !important;
        font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #0f2c4d !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
      }}
      .sso-btn:hover {{
        background: #f8fbff !important;
        border-color: #034f9a !important;
        box-shadow: 0 3px 8px rgba(3, 79, 154, 0.12) !important;
        transform: translateY(-1px) !important;
      }}
      .sso-icon {{
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        min-height: 20px !important;
        object-fit: contain !important;
        display: block !important;
      }}

      /* Bottom Switch */
      .auth-bottom-switch {{
        text-align: center !important;
        font-size: 13.5px !important;
        color: #475569 !important;
      }}
      .switch-link {{
        color: #0060cc !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        margin-left: 4px !important;
      }}
      .switch-link:hover {{
        text-decoration: underline !important;
      }}

      /* Alert Boxes */
      .auth-alert-box {{
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 12px 14px !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-bottom: 14px !important;
      }}
      .alert-error {{
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #b91c1c !important;
      }}
      .alert-success {{
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #15803d !important;
      }}
      .demo-highlight {{
        background-color: #ecfdf5 !important;
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3.5px rgba(16, 185, 129, 0.15) !important;
      }}

      @media (max-width: 992px) {{
        .auth-split-wrapper {{
          grid-template-columns: 1fr !important;
        }}
        .auth-split-hero {{
          min-height: 280px !important;
        }}
        .auth-split-card-col {{
          padding: 24px 16px !important;
        }}
        .auth-card-inner {{
          padding: 28px 20px 24px !important;
          max-width: 100% !important;
          border-radius: 12px !important;
        }}
      }}
    </style>

    <div class="auth-split-wrapper">
      <!-- Left Column: Pure Cinematic Port Visual (No Text Overlay) -->
      <div class="auth-split-hero" aria-label="Global Maritime Logistics Hub"></div>

      <!-- Right Column: Login Card -->
      <div class="auth-split-card-col">
        <div class="auth-card-inner">
          
          <!-- Brand Logo at top of form -->
          <div class="auth-brand-badge">
            <img src="/static/images/logo_emblem.png" alt="Logistics Waves" class="auth-brand-logo-img" width="44" height="46" decoding="async">
            <span class="auth-brand-title">LOGISTICS WAVES</span>
          </div>

          <!-- Welcome Title -->
          <h2 class="auth-form-title">{title_text}</h2>
          <p class="auth-form-subtitle">{subtitle_text}</p>

          <!-- Role Selector Capsule Tabs -->
          <div class="auth-role-tabs">
            <button type="button" class="role-tab {'active' if preset_role != 'employer' else ''}" id="roleCandidateBtn" onclick="selectAuthRole('candidate')">
              <i class="fa-solid fa-user"></i>
              <span>Job Seeker</span>
            </button>
            <button type="button" class="role-tab {'active' if preset_role == 'employer' else ''}" id="roleEmployerBtn" onclick="selectAuthRole('employer')">
              <i class="fa-solid fa-building"></i>
              <span>Employer</span>
            </button>
          </div>

          {err_html}
          {msg_html}

          <!-- Main Form -->
          <form method="post" action="{action}" id="authMainForm">
            <input type="hidden" name="next" value="{e(next_path)}">
            <input type="hidden" name="role" id="authRoleInput" value="{preset_role}">
            {csrf_input()}

            {signup_name_field}

            <!-- Email Field -->
            <div class="auth-input-group">
              <div class="auth-input-wrapper">
                <i class="fa-regular fa-envelope input-leading-icon"></i>
                <input id="emailInput" type="email" name="email" class="auth-field-control" placeholder="Enter your email address" required autocomplete="username">
              </div>
            </div>

            <!-- Password Field -->
            <div class="auth-input-group">
              <div class="auth-input-wrapper">
                <i class="fa-solid fa-lock input-leading-icon"></i>
                <input id="pwdInput" type="password" name="password" class="auth-field-control has-toggle" placeholder="Enter your password" required autocomplete="current-password">
                <button type="button" class="pwd-toggle-btn" onclick="togglePasswordVisibility()" aria-label="Toggle password visibility">
                  <i id="eyeIcon" class="fa-regular fa-eye-slash"></i>
                </button>
              </div>
            </div>

            <!-- Options row -->
            <div class="auth-meta-row">
              <label class="auth-remember-checkbox">
                <input type="checkbox" name="remember" checked>
                <span>Remember me for 30 days</span>
              </label>
              <a href="javascript:void(0)" onclick="forgotPasswordHint()" class="auth-forgot-link">Forgot password?</a>
            </div>

            <!-- Submit Button -->
            <button class="auth-submit-btn" type="submit">
              <span>{submit_btn_text}</span>
              <span class="btn-arrow">&rarr;</span>
            </button>
          </form>

          <!-- SSO Divider -->
          <div class="auth-sso-divider">
            <span>or continue with</span>
          </div>

          <!-- SSO Buttons -->
          <div class="auth-sso-row">
            <button type="button" class="sso-btn" onclick="window.showToast ? showToast('Google Workspace SSO is not enabled. Sign in with email and password.') : null">
              <img src="/static/images/google_icon.png" alt="Google" class="sso-icon" width="20" height="20" decoding="async">
              <span>Google</span>
            </button>
            <button type="button" class="sso-btn" onclick="window.showToast ? showToast('LinkedIn SSO is enabled for verified corporate members.') : null">
              <img src="/static/images/linkedin_icon.png" alt="LinkedIn" class="sso-icon" width="20" height="20" decoding="async">
              <span>LinkedIn</span>
            </button>
          </div>

          <!-- Bottom Account Switch -->
          <div class="auth-bottom-switch">
            <span>{switch_prefix}</span>
            <a href="{switch_href}" class="switch-link">{switch_label} &rarr;</a>
          </div>

        </div>
      </div>
    </div>

    <script>
      function selectAuthRole(role) {{
        var roleInput = document.getElementById('authRoleInput');
        if (roleInput) roleInput.value = role;
        
        var candBtn = document.getElementById('roleCandidateBtn');
        var empBtn = document.getElementById('roleEmployerBtn');
        if (role === 'employer') {{
          if (candBtn) candBtn.classList.remove('active');
          if (empBtn) empBtn.classList.add('active');
        }} else {{
          if (candBtn) candBtn.classList.add('active');
          if (empBtn) empBtn.classList.remove('active');
        }}
      }}

      function togglePasswordVisibility() {{
        var pwd = document.getElementById('pwdInput');
        var icon = document.getElementById('eyeIcon');
        if (!pwd || !icon) return;
        if (pwd.type === 'password') {{
          pwd.type = 'text';
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }} else {{
          pwd.type = 'password';
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        }}
      }}

      function forgotPasswordHint() {{
        if (typeof window.showToast === 'function') {{
          window.showToast('Use your email & password or contact admin@logisticwaves.com for reset.');
        }}
      }}
    </script>
    '''
    return layout(title, body, None, page_class="auth-page-shell", description="Log in or create a free account.")
def account_shell(user, active, title, subtitle, content):
    initials = "".join(part[0] for part in user["name"].split()[:2]).upper()
    links = [
        ("Overview", "/profile", "overview", "layers"),
        ("Saved jobs", "/saved", "saved", "heart"),
        ("Applications", "/tracker", "tracker", "check"),
        ("Job alerts", "/alerts", "alerts", "bell"),
        ("Profile settings", "/profile#settings", "profile", "edit"),
    ]
    if user.get("role") == "employer":
        links.append(("Employer portal", "/employers", "employer", "building"))
    if user.get("role") == "admin":
        links.append(("Admin dashboard", "/admin", "admin", "chart"))
    nav = "".join(
        f'<a class="account-nav-link{" active" if key == active else ""}" href="{e(href)}"'
        f'{" aria-current=page" if key == active else ""}>{icon(icon_name, 17)}<span>{e(label)}</span></a>'
        for label, href, key, icon_name in links
    )
    return f'''
    <section class="account-page"><div class="container">
      <div class="account-page-heading"><div><span class="account-eyebrow">YOUR WORKSPACE</span>
        <h1>{e(title)}</h1><p>{e(subtitle)}</p></div>
        <a class="btn btn-primary" href="/jobs">{icon("search", 16)} Explore jobs</a>
      </div>
      <div class="account-layout">
        <aside class="account-sidebar" aria-label="Workspace navigation">
          <div class="account-identity"><img class="account-avatar-img" src="/static/images/default_user_avatar.png" alt="Profile" width="56" height="56" decoding="async" data-fallback-kind="avatar">
            <div><strong>{e(user["name"])}</strong><small>{e(user["headline"] or user["role"].title())}</small></div>
          </div>
          <nav class="account-nav">{nav}</nav>
          <div class="account-sidebar-footer"><span>{e(user["email"])}</span>
            <form method="post" action="/logout">{csrf_input()}<button type="submit">{icon("external", 15)} Sign out</button></form>
          </div>
        </aside>
        <div class="account-content">{content}</div>
      </div>
    </div></section>'''


def dashboard_page(conn, user, saved_jobs, applications, alerts, followed, stats, title="Your Dashboard"):
    cards = [
        ("Saved Jobs", stats["saved"], "/saved", "heart", "#aa2fbe"),
        ("Applications", stats["applied"], "/tracker", "check", "#244fe7"),
        ("Following", stats["following"], "/saved#following", "users", "#009ee0"),
        ("Job Alerts", stats["alerts"], "/alerts", "bell", "#4d1096"),
    ]
    stat_cards = "".join(
        f'<a class="stat-card" style="--stat:{color}" href="{e(href)}"><span>{icon(ic, 22)}</span><strong>{n}</strong><small>{e(label)}</small></a>'
        for label, n, href, ic, color in cards
    )
    content = f'''
      <div class="account-welcome"><div><h2>Welcome back, {e(user["name"].split()[0])}</h2>
        <p>{e(user["headline"] or "Your career hub")} · {e(user["location"] or "Anywhere")}</p></div>
        <a class="btn btn-outline" href="/profile#settings">{icon("edit", 16)} Edit profile</a></div>
      <div class="stat-grid">{stat_cards}</div>
      <div class="dashboard-columns">
        <div class="content-card"><div class="card-head"><h2>Recently saved jobs</h2><a class="text-link" href="/saved">See all {icon("arrow", 15)}</a></div>
          <div class="compact-job-list">{"".join(job_card(j, compact=True) for j in saved_jobs[:4]) or empty_state("No saved jobs yet", "Save interesting roles and they will be ready when you are.", "/jobs", "Browse jobs")}</div></div>
        <div class="content-card"><div class="card-head"><h2>Application activity</h2><a class="text-link" href="/tracker">Open tracker {icon("arrow", 15)}</a></div>
          <div class="activity-list">{"".join(f'<div class="activity-item"><span class="status-dot"></span><div><strong>{e(a["title"])}</strong><small>{e(a["company_name"])} · {e(a["status"])}</small></div></div>' for a in applications[:5]) or '<p class="muted">No applications yet. Your next opportunity is one search away.</p>'}</div>
          <h3>Active alerts</h3><ul class="mini-list">{"".join(f'<li>{icon("bell", 14)} {e(a["query"])} <span>{e(a["frequency"])}</span></li>' for a in alerts[:4]) or '<li>No alerts yet.</li>'}</ul>
        </div>
      </div>
      <div class="content-card"><div class="card-head"><h2>Companies you follow</h2><a class="text-link" href="/companies">Discover companies {icon("arrow", 15)}</a></div>
        <div class="hub-company-grid">{"".join(f'<a class="hub-company" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<span>{e(c["name"])}</span></a>' for c in followed) or '<p class="muted">Follow companies to keep up with their latest roles.</p>'}</div></div>'''
    body = account_shell(user, "overview", title,
                         "Your career activity, all in one place.", content)
    return layout(title, body, user, page_class="dashboard-page", description="Your saved jobs, applications and alerts.")


def saved_page(conn, user, saved_jobs, followed):
    content = f'''
      <div class="content-card"><div class="card-head"><div><h2>Saved jobs <span class="light-count">({len(saved_jobs)})</span></h2>
        <p>Keep promising opportunities close at hand.</p></div><a class="btn btn-outline" href="/jobs">Browse jobs {icon("arrow", 15)}</a></div>
        <div class="job-list">{"".join(job_card(j) for j in saved_jobs) or empty_state("Your shortlist starts here", "Tap the heart on a role to save it for later.", "/jobs", "Explore open roles")}</div></div>
      <div class="content-card"><div class="card-head"><div><h2>Followed companies <span class="light-count">({len(followed)})</span></h2>
        <p>Stay close to teams you would love to join.</p></div><a class="text-link" href="/companies">Explore companies {icon("arrow", 15)}</a></div>
        <div class="hub-company-grid">{"".join(f'<a class="hub-company" href="/company/{e(c["slug"])}">{company_logo(c, 84)}<span>{e(c["name"])}</span></a>' for c in followed) or '<p class="muted">Follow a company to see it here.</p>'}</div></div>'''
    body = account_shell(user, "saved", "Saved jobs", "Your shortlist of roles and companies.", content)
    return layout("Saved Jobs", body, user, description="Your saved jobs and followed companies.")


def tracker_page(conn, user, applications, message=""):
    rows = "".join(
        f'''<tr><td><a href="/job/{e(a['job_slug'])}/{a['job_id']}">{e(a['title'])}</a><span>{e(a['company_name'])}</span></td>
        <td>{e(a['location'])}</td><td>{e(a['salary_display'])}</td><td><span class="status-pill">{e(a['status'])}</span></td><td>{e(a['created_at'][:10])}</td>
        <td><form method="post" action="/tracker/delete" class="application-delete-form" data-application-id="{a['id']}"><input type="hidden" name="id" value="{a['id']}">{csrf_input()}<button class="btn btn-quiet-danger" type="submit">Withdraw</button></form></td></tr>'''
        for a in applications
    ) or '<tr><td colspan="6">No applications yet. Find a role and submit your first application.</td></tr>'
    msg = f'<div class="form-success">{icon("check", 16)} {e(message)}</div>' if message else ""
    content = f'''
      <div class="content-card">{msg}<div class="card-head"><div><h2>Your applications</h2><p>{len(applications)} in your tracker</p></div>
        <a class="btn btn-primary" href="/jobs">Find more jobs {icon("arrow", 16)}</a></div>
        <div class="table-card"><table class="tracker-table"><thead><tr><th>Role</th><th>Location</th><th>Salary</th><th>Status</th><th>Applied</th><th><span class="sr-only">Actions</span></th></tr></thead><tbody>{rows}</tbody></table></div></div>'''
    body = account_shell(user, "tracker", "Application tracker",
                         "Track each opportunity from first click to final decision.", content)
    return layout("Application Tracker", body, user, description="Track your job applications.")


def alerts_page(conn, user, alerts, company_slug="", message="", error=""):
    preset = db.get_company(conn, company_slug)["name"] if company_slug and db.get_company(conn, company_slug) else "My job search"
    rows = "".join(
        f'''<div class="alert-row" data-alert-row="{a['id']}"><div class="alert-row-summary">{icon("bell", 20)}<div><strong>{e(a['query'])}</strong><span>{e(a['frequency'])} · created {e(a['created_at'][:10])}</span></div></div>
        <div class="alert-row-actions"><details class="alert-edit"><summary class="btn btn-outline">Edit</summary>
          <form method="post" action="/alerts/update" class="alert-edit-form" data-alert-id="{a['id']}">
            <input type="hidden" name="id" value="{a['id']}">{csrf_input()}<label>Alert name<input name="query" value="{e(a['query'])}" required></label>
            <label>Frequency {select("frequency", ["Daily", "Weekly", "Monthly"], a["frequency"], "", "")}</label>
            <button class="btn btn-primary" type="submit">Save changes</button></form>
        </details><form method="post" action="/alerts/delete" class="alert-delete-form" data-alert-id="{a['id']}">
          <input type="hidden" name="id" value="{a['id']}">{csrf_input()}<button class="icon-btn danger" type="submit" aria-label="Delete alert">{icon("trash", 18)}</button></form></div></div>'''
        for a in alerts
    ) or empty_state("No alerts yet", "Create a job alert and we will keep your search close.", "/jobs", "Browse jobs")
    msg = (
        f'<div class="form-success">{icon("check", 16)} {e(message)}</div>' if message else ""
    ) + (
        f'<div class="form-error">{icon("close", 16)} {e(error)}</div>' if error else ""
    )
    content = f'''
      <div class="content-card"><div class="card-head"><div><h2>Your active alerts</h2><p>Choose how often you want to hear about new matches.</p></div></div>
        {msg}<div class="account-alert-list">{rows}</div></div>
      <div class="content-card"><h2>Create a new alert</h2>
      <form method="post" action="/alerts">
        {csrf_input()}
        <div class="alert-create-form"><label>Alert name<input name="query" value="{e(preset)}" required></label>
          <label>Frequency {select("frequency", ["Daily", "Weekly", "Monthly"], "Daily", "", "")}</label>
          <button class="btn btn-primary" type="submit">{icon("bell", 16)} Create alert</button></div>
      </form></div>'''
    body = account_shell(user, "alerts", "Job alerts",
                         "A smarter way to keep up with roles that fit.", content)
    return layout("Job Alerts", body, user, description="Create and manage job alerts.")


def profile_page(conn, user, stats, message=""):
    msg = f'<div class="form-success">{icon("check", 16)} {e(message)}</div>' if message else ""
    content = f'''
      <div class="content-card" id="settings"><div class="card-head"><div><h2>Profile details</h2>
        <p>Help employers understand who you are and what you are looking for.</p></div></div>{msg}
        <form method="post" action="/profile" class="stacked-form">
          {csrf_input()}
          <label>Full name<input name="name" value="{e(user['name'])}" required></label>
          <label>Headline<input name="headline" value="{e(user['headline'] or '')}" placeholder="e.g. Senior Product Designer"></label>
          <label>Location<input name="location" value="{e(user['location'] or '')}" placeholder="City, State"></label>
          <label>Email<input value="{e(user['email'])}" disabled></label>
          <button class="btn btn-primary" type="submit">Save Changes {icon("check", 16)}</button>
        </form>
      </div>
      <div class="content-card"><div class="card-head"><div><h2>Account overview</h2><p>Your account at a glance.</p></div></div>
        <div class="profile-stat-list"><span>Account type<strong>{e(user['role'].title())}</strong></span>
          <span>Member since<strong>{e((user['created_at'] or '')[:10])}</strong></span>
          <span>Saved jobs<strong>{stats['saved']}</strong></span><span>Applications<strong>{stats['applied']}</strong></span>
          <span>Companies followed<strong>{stats['following']}</strong></span><span>Active alerts<strong>{stats['alerts']}</strong></span></div>
      </div>'''
    body = account_shell(user, "profile", "Profile settings",
                         "Keep your details current as your career evolves.", content)
    return layout("Your Profile", body, user, description="Manage your account profile.")


def employers_page(conn, user, employer_jobs=None, message="", error="", applicants=None):
    if not user:
        body = f'''
        <section class="page-hero employers-hero"><div class="container">{breadcrumb([("Home", "/"), ("For Employers", "")])}
          <span class="hero-badge light">{icon("sparkle", 15)} Employer Intelligence Platform</span>
          <h1>Be visible. Be trusted. Be chosen.</h1><p class="hero-sub">Reach candidates with company insights, employer branding and job distribution.</p>
          <div class="hero-buttons"><a class="btn btn-magenta btn-lg" href="{url('/auth/login', next='/employers')}">LOG IN TO EMPLOYER PORTAL</a><a class="btn btn-white btn-lg" href="{url('/auth/signup', role='employer', next='/employers')}">CREATE EMPLOYER ACCOUNT</a></div>
        </div></section>
        <section class="section"><div class="container"><div class="info-grid">
          <div class="info-card">{icon("building", 26)}<h3>Company profiles</h3><p>Showcase culture, benefits, teams and tech stack in one research-ready profile.</p></div>
          <div class="info-card">{icon("chart", 26)}<h3>Hiring insights</h3><p>See which roles attract attention and where your pipeline is strongest.</p></div>
          <div class="info-card">{icon("users", 26)}<h3>Candidate reach</h3><p>Post roles that appear instantly across job search, company pages and alerts.</p></div>
        </div></div></section>'''
        return layout("For Employers", body, None, description="Employer branding, job posting and hiring insights.")
    companies = [dict(r) for r in conn.execute("SELECT slug,name FROM companies ORDER BY name").fetchall()]
    company_options = [("", "Select a company")] + [(c["slug"], c["name"]) for c in companies]
    msg = f'<div class="form-success">{icon("check", 16)} {e(message)}</div>' if message else ""
    err = f'<div class="form-error">{icon("close", 16)} {e(error)}</div>' if error else ""
    job_rows = []
    for job in employer_jobs or []:
        company_field = select("company_slug", company_options, job["company_slug"], "", "")
        category_field = select("category", seed.CATEGORIES, job["category"], "", "")
        level_field = select("level", seed.LEVELS, job["level"], "", "")
        workplace_field = select("workplace", ["Fully Remote", "Hybrid", "On Site", "Remote or Hybrid"], job["workplace"], "", "")
        job_rows.append(f'''
          <article class="employer-job-row" data-employer-job="{job['id']}">
            <div class="employer-job-summary"><div class="employer-job-mark">{company_logo(job, 84)}</div><div class="employer-job-info">
              <a href="/job/{e(job['slug'])}/{job['id']}"><strong class="employer-job-title">{e(job['title'])}</strong></a>
              <span>{e(job['company_name'])} · {e(job['location'] or 'Location flexible')}</span></div>
              <span class="job-status-badge {'closed' if job['status'] != 'active' else ''}">{'Closed' if job['status'] != 'active' else 'Live'}</span>
            </div>
            <div class="employer-job-actions"><details class="employer-job-edit"><summary class="btn btn-outline">{icon("edit", 15)} Edit role</summary>
              <form method="post" action="/employers/jobs/update" class="employer-job-edit-form" data-job-id="{job['id']}">
                {csrf_input()}
                <input type="hidden" name="id" value="{job['id']}">
                <label>Job title<input name="title" value="{e(job['title'])}" required></label>
                <label>Company{company_field}</label><label>Category{category_field}</label><label>Experience{level_field}</label>
                <label>Workplace{workplace_field}</label><label>Location<input name="location" value="{e(job['location'] or '')}"></label>
                <label>Salary min (K)<input type="number" name="salary_min" min="0" value="{job['salary_min'] or 0}"></label>
                <label>Salary max (K)<input type="number" name="salary_max" min="0" value="{job['salary_max'] or 0}"></label>
                <label class="full">Skills<input name="skills" value="{e(job['skills'] or '')}"></label>
                <label class="full">Description<textarea name="description" rows="3">{e(job['description'] or '')}</textarea></label>
                <div class="full"><button class="btn btn-primary" type="submit">Save changes</button></div>
              </form>
            </details>
            <form method="post" action="/employers/jobs/archive" class="employer-job-archive-form" data-job-id="{job['id']}">
              {csrf_input()}
              <input type="hidden" name="id" value="{job['id']}">
              <button class="btn btn-quiet-danger" type="submit" {'disabled' if job['status'] != 'active' else ''}>{'Archived' if job['status'] != 'active' else 'Archive'}</button>
            </form></div>
          </article>''')
    rows = "".join(job_rows) or empty_state(
        "No roles posted yet", "Create your first listing to meet your next great hire.",
        "/employers#post", "Post a job",
    )
    _emp_counts = db.counts(conn)
    content = f'''
      <div class="stat-grid"><div class="stat-card"><span>{icon("briefcase", 22)}</span><strong>{len(employer_jobs or [])}</strong><small>Jobs you manage</small></div>
        <div class="stat-card"><span>{icon("building", 22)}</span><strong>{len(companies)}</strong><small>Company profiles</small></div>
        <div class="stat-card"><span>{icon("users", 22)}</span><strong>{_emp_counts['users']}</strong><small>Registered members</small></div>
        <div class="stat-card"><span>{icon("chart", 22)}</span><strong>{_emp_counts['jobs']}</strong><small>Active jobs</small></div></div>
      <div class="content-card" id="post"><div class="card-head"><div><h2>Post a new job</h2><p>Reach candidates across search and company pages.</p></div><span class="job-posting-tag">Publishes instantly</span></div>{msg}{err}
        <form method="post" action="/employers/post-job" class="employer-form">
          {csrf_input()}
          <label>Job title<input name="title" placeholder="e.g. Senior Frontend Engineer" required></label>
          <label>Company {select("company_slug", company_options, "", "", "")}</label>
          <label>Category {select("category", seed.CATEGORIES, "Engineering", "", "")}</label>
          <label>Experience {select("level", seed.LEVELS, "Mid level", "", "")}</label>
          <label>Workplace {select("workplace", ["Fully Remote", "Hybrid", "On Site", "Remote or Hybrid"], "Hybrid", "", "")}</label>
          <label>Location<input name="location" placeholder="e.g. New York, NY, USA"></label>
          <label>Salary min (K)<input type="number" name="salary_min" min="0" value="100"></label>
          <label>Salary max (K)<input type="number" name="salary_max" min="0" value="160"></label>
          <label class="full">Skills (comma separated)<input name="skills" placeholder="React, TypeScript, Design Systems"></label>
          <label class="full">Description<textarea name="description" rows="4" placeholder="Describe the role, team and impact…"></textarea></label>
          <div class="full"><button class="btn btn-primary btn-lg" type="submit">{icon("plus", 17)} Publish Job</button></div>
        </form>
      </div>
      <div class="content-card"><div class="card-head"><div><h2>Your job listings</h2><p>Edit details or archive a listing when hiring is complete.</p></div></div>
        <div class="employer-job-list">{rows}</div></div>'''
    app_list = applicants or []
    app_rows = "".join(
        f'''<tr>
          <td><strong>{e(a["candidate_name"])}</strong><div style="font-size:12px;color:#64748b;">{e(a["candidate_email"])}</div><div style="font-size:12px;color:#475569;">{e(a.get("candidate_headline") or "")}{" · " + e(a["candidate_location"]) if a.get("candidate_location") else ""}</div></td>
          <td><a href="/job/{e(a["job_slug"])}/{a["job_id"]}" style="font-weight:600;color:#0071e3;text-decoration:none;">{e(a["job_title"])}</a><div style="font-size:12px;color:#64748b;">{e(a["company_name"])}</div></td>
          <td style="font-size:12.5px;color:#334155;max-width:260px;">{e(a.get("note") or "No cover note attached.")}</td>
          <td style="font-size:12px;color:#64748b;white-space:nowrap;">{e((a.get("created_at") or "")[:10])}</td>
          <td>
            <form method="post" action="/employers/applications/status" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
              {csrf_input()}
              <input type="hidden" name="id" value="{a["id"]}">
              {select("status", ["Applied", "Reviewing", "Interview", "Offer", "Rejected"], a["status"], "", "")}
              <button class="btn btn-outline btn-sm" type="submit">Update</button>
            </form>
          </td>
        </tr>'''
        for a in app_list
    ) or '<tr><td colspan="5" style="text-align:center;color:#64748b;padding:20px;">No student applications yet. Once candidates apply to your posted jobs, they will appear here.</td></tr>'
    content += f'''
      <div class="content-card" id="applicants"><div class="card-head"><div><h2>Candidate Applicants &amp; CVs</h2><p>{len(app_list)} application{"s" if len(app_list) != 1 else ""} across your posted roles</p></div></div>
        <div class="table-card"><table class="tracker-table"><thead><tr><th>Candidate</th><th>Role</th><th>Cover Note / CV</th><th>Applied</th><th>Status</th></tr></thead><tbody>{app_rows}</tbody></table></div></div>'''
    body = account_shell(user, "employer", "Employer workspace",
                         "Manage your open roles and reach great candidates.", content)
    return layout("Employer Portal", body, user, description="Post and manage jobs in the Logistic Waves employer portal.")


# ---------- static / utility ----------

def simple_page(title, eyebrow, intro, sections, user=None):
    blocks = "".join(f'<div class="content-card"><h2>{e(h)}</h2><p>{e(p)}</p></div>' for h, p in sections)
    body = f'''
    <section class="page-hero"><div class="container">{breadcrumb([("Home", "/"), (title, "")])}
      <span class="hero-badge light">{e(eyebrow)}</span><h1>{e(title)}</h1><p class="hero-sub">{e(intro)}</p></div></section>
    <section class="section"><div class="container narrow"><div class="simple-stack">{blocks}</div></div></section>'''
    return layout(title, body, user, description=intro)


def not_found_page(user, path):
    body = f'''
    <section class="container narrow-page"><div class="empty-state large-empty">
      <div class="empty-icon">{icon("search", 40)}</div><h1>404 — Page not found</h1>
      <p>We couldn't find <code>{e(path)}</code>, but there's plenty more to explore.</p>
      <div class="auth-actions"><a class="btn btn-primary" href="/">Go Home</a><a class="btn btn-outline" href="/jobs">Browse Jobs</a></div>
    </div></section>'''
    return layout("Page not found", body, user, description="The requested page was not found.")


def admin_dashboard_page(conn, user, message="", error="", tab="overview", page=1, q=""):
    return admin_views.render_admin_dashboard(conn, user, message=message, error=error, tab=tab, page=page, q=q)
