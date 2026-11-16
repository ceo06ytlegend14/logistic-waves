import re

# 1. Update views.py
with open('views.py', 'r', encoding='utf-8') as f:
    views_text = f.read()

# Replace hero section
new_hero = """<!-- 1. Enterprise Hero: Insights for Smarter Logistics (HD Photographic Smoke-White Master Composition) -->
    <section class="lw-hero-banner-section smoke-white-hero">
      <div class="hero-shell">
        <div class="hero-photo-hd" aria-hidden="true"></div>
        <div class="hero-smoke-overlay" aria-hidden="true"></div>

        <div class="hero-inner-wrap">
          <div class="hero-content">
            <div class="hero-eyebrow-smoke">
              <span class="eyebrow-dot-blue"></span>
              GLOBAL LOGISTICS INTELLIGENCE
            </div>
            
            <h1 class="hero-headline-smoke">
              Insights for<br>
              <span class="hero-hl-blue">Smarter</span> Logistics
            </h1>
            
            <p class="hero-subtitle-smoke">
              Real-time intelligence, container visibility, and vetted industry careers connecting over 45,000+ logistics professionals worldwide.
            </p>
            
            <div class="hero-actions">
              <a class="hero-btn-primary" href="/article-blogs">
                Explore Insights
              </a>
              <a class="hero-btn-secondary" href="#overview" onclick="openFwtModal(0); return false;" aria-label="Watch Overview Video">
                <span class="hero-yt-badge">
                  <i class="fa-brands fa-youtube"></i>
                </span>
                <span>Watch Overview</span>
              </a>
            </div>

            <div class="hero-features-smoke">
              <div class="feat-item-smoke"><i class="fa-solid fa-earth-americas"></i> Worldwide Coverage</div>
              <div class="feat-item-smoke"><i class="fa-solid fa-bolt"></i> Real-Time Tracking</div>
              <div class="feat-item-smoke"><i class="fa-solid fa-shield-halved"></i> Trusted &amp; Secure</div>
              <div class="feat-item-smoke"><i class="fa-solid fa-headset"></i> 24/7 Support</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. Editorial Showcase"""

views_updated = re.sub(r'<!-- 1\. Enterprise Hero.*?<!-- 2\. Editorial Showcase', new_hero, views_text, flags=re.DOTALL)
views_updated = re.sub(r'/static/styles\.css\?v=[^"]+', '/static/styles.css?v=20261114_08', views_updated)

with open('views.py', 'w', encoding='utf-8') as f:
    f.write(views_updated)
print('views.py updated with HD smoke-white hero!')

# 2. Update styles.css
with open('static/styles.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

# Replace the hero block in styles.css
hero_match = re.search(r'/\* =+\s*ENTERPRISE LOGISTICS WAVES HERO', css_text)
if hero_match:
    idx = hero_match.start()
    next_match = re.search(r'/\* =+', css_text[idx+50:])
    end_idx = idx + 50 + next_match.start() if next_match else idx + 3000
    
    new_hero_css = """/* ==========================================================================
   ENTERPRISE LOGISTICS WAVES HERO - SMOKE WHITE + ULTRA HD PHOTOGRAPHY
   ========================================================================== */
.lw-hero-banner-section.smoke-white-hero {
  position: relative !important;
  width: 100% !important;
  background: #f8fafc !important;
  overflow: hidden !important;
  padding: 0 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

.smoke-white-hero .hero-shell {
  position: relative !important;
  width: 100% !important;
  min-height: 520px !important;
  background: #f8fafc !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  isolation: isolate !important;
  overflow: hidden !important;
  box-shadow: none !important;
  border: none !important;
  border-radius: 0 !important;
}

/* 1. Crystal-Clear Ultra-HD Logistics Photograph */
.smoke-white-hero .hero-photo-hd {
  position: absolute !important;
  inset: 0 !important;
  z-index: 1 !important;
  background-image: url("/static/images/login_concept_hero_bg.jpg") !important;
  background-position: center right !important;
  background-size: cover !important;
  background-repeat: no-repeat !important;
  opacity: 1 !important;
}

/* 2. Seamless Smoke-White Cinematic Gradient Mask */
.smoke-white-hero .hero-smoke-overlay {
  position: absolute !important;
  inset: 0 !important;
  z-index: 2 !important;
  background: linear-gradient(
    90deg,
    #f8fafc 0%,
    rgba(248, 250, 252, 0.98) 36%,
    rgba(248, 250, 252, 0.84) 52%,
    rgba(248, 250, 252, 0.45) 72%,
    rgba(248, 250, 252, 0.10) 90%,
    transparent 100%
  ) !important;
  pointer-events: none !important;
}

/* 3. Hero Inner Container */
.smoke-white-hero .hero-inner-wrap {
  position: relative !important;
  z-index: 3 !important;
  width: min(1360px, 94%) !important;
  max-width: 1360px !important;
  margin: 0 auto !important;
  padding: 76px 20px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}

/* 4. Left-Aligned Content */
.smoke-white-hero .hero-content {
  max-width: 660px !important;
  text-align: left !important;
}

.hero-eyebrow-smoke {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 6px 14px 6px 12px !important;
  border-radius: 9999px !important;
  background: #eff6ff !important;
  border: 1px solid #bfdbfe !important;
  color: #1d4ed8 !important;
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  margin-bottom: 20px !important;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.08) !important;
}

.eyebrow-dot-blue {
  width: 7px !important;
  height: 7px !important;
  border-radius: 50% !important;
  background: #2563eb !important;
  display: inline-block !important;
  box-shadow: 0 0 8px rgba(37, 99, 235, 0.6) !important;
}

.hero-headline-smoke {
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: clamp(38px, 4.2vw, 56px) !important;
  line-height: 1.1 !important;
  font-weight: 900 !important;
  color: #0b192c !important;
  letter-spacing: -0.03em !important;
  margin: 0 0 18px 0 !important;
}

.hero-headline-smoke .hero-hl-blue {
  color: #0284c7 !important;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}

.hero-subtitle-smoke {
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: 17px !important;
  line-height: 1.65 !important;
  color: #334155 !important;
  font-weight: 500 !important;
  margin: 0 0 32px 0 !important;
  max-width: 580px !important;
}

.smoke-white-hero .hero-actions {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 14px !important;
  align-items: center !important;
  margin-bottom: 32px !important;
}

.smoke-white-hero .hero-btn-primary {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  padding: 14px 30px !important;
  border-radius: 9999px !important;
  text-decoration: none !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4) !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}

.smoke-white-hero .hero-btn-primary:hover {
  transform: translateY(-1.5px) !important;
  box-shadow: 0 6px 22px rgba(2, 132, 199, 0.5) !important;
  color: #ffffff !important;
}

.smoke-white-hero .hero-btn-secondary {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  background: #ffffff !important;
  border: 1.5px solid #cbd5e1 !important;
  color: #0f172a !important;
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  padding: 13px 26px !important;
  border-radius: 9999px !important;
  text-decoration: none !important;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05) !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}

.smoke-white-hero .hero-btn-secondary:hover {
  background: #f8fafc !important;
  border-color: #94a3b8 !important;
  transform: translateY(-1.5px) !important;
  color: #0f172a !important;
}

.smoke-white-hero .hero-yt-badge {
  background: #ff0000 !important;
  color: #ffffff !important;
  width: 22px !important;
  height: 22px !important;
  border-radius: 50% !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 11px !important;
  flex-shrink: 0 !important;
}

.hero-features-smoke {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 24px !important;
  padding-top: 24px !important;
  border-top: 1px solid #e2e8f0 !important;
  max-width: 620px !important;
}

.feat-item-smoke {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-family: "Plus Jakarta Sans", sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  color: #334155 !important;
}

.feat-item-smoke i {
  color: #0284c7 !important;
  font-size: 15px !important;
}"""
    css_text = css_text[:idx] + new_hero_css + '\n\n' + css_text[end_idx:]

# 3. Add Smoke-White Header & Footer overrides to styles.css
smoke_header_footer_css = """
/* ==========================================================================
   SMOKE WHITE HEADER & FOOTER OVERRIDES
   ========================================================================== */
.site-header {
  background: #f8fafc !important;
  color: #0f172a !important;
  border-bottom: 1px solid #e2e8f0 !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05) !important;
}

.site-header .main-nav a {
  color: #334155 !important;
  font-weight: 700 !important;
  font-size: 14.5px !important;
  transition: color 0.18s ease !important;
}

.site-header .main-nav a:hover,
.site-header .main-nav a.active {
  color: #0284c7 !important;
}

.site-header .brand-lw-main {
  color: #0f172a !important;
  font-weight: 900 !important;
  text-shadow: none !important;
}

.site-header .brand-lw-accent {
  color: #0284c7 !important;
  font-weight: 900 !important;
  text-shadow: none !important;
}

.site-header .brand-sub-row {
  color: #64748b !important;
  font-weight: 700 !important;
}

.site-header .search-trigger,
.site-header .icon-btn {
  color: #334155 !important;
}

.site-header .search-trigger svg {
  stroke: #334155 !important;
  color: #334155 !important;
}

.site-header .search-trigger:hover,
.site-header .icon-btn:hover {
  color: #0284c7 !important;
}

.site-header .search-trigger:hover svg {
  stroke: #0284c7 !important;
}

.site-header .header-auth a,
.site-header .header-actions a {
  color: #0f172a !important;
  font-weight: 700 !important;
}

.site-header .employer-btn,
.site-header a.employer-btn {
  background: #eff6ff !important;
  color: #0284c7 !important;
  border: 1.5px solid #bfdbfe !important;
  border-radius: 9999px !important;
  padding: 8px 18px !important;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  letter-spacing: 0.06em !important;
  transition: all 0.2s ease !important;
  text-decoration: none !important;
}

.site-header .employer-btn:hover,
.site-header a.employer-btn:hover {
  background: #0284c7 !important;
  color: #ffffff !important;
  border-color: #0284c7 !important;
  text-decoration: none !important;
}

/* Promo Ticker Bar */
.promo-ticker {
  background: #f1f5f9 !important;
  border-top: 1px solid #e2e8f0 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

.promo-ticker-text {
  color: #334155 !important;
  font-weight: 600 !important;
}

.promo-ticker-dot {
  color: #94a3b8 !important;
}

/* Smoke White Footer */
.site-footer {
  background: #f8fafc !important;
  color: #1e293b !important;
  border-top: 1px solid #e2e8f0 !important;
  padding: 56px 0 24px !important;
}

.site-footer .brand-lw-main {
  color: #0f172a !important;
  text-shadow: none !important;
}

.site-footer .brand-lw-accent {
  color: #0284c7 !important;
  text-shadow: none !important;
}

.site-footer .brand-sub-row {
  color: #64748b !important;
}

.site-footer p {
  color: #475569 !important;
}

.site-footer h3,
.site-footer h4,
.site-footer .footer-col-title {
  color: #0f172a !important;
  font-weight: 800 !important;
}

.site-footer a {
  color: #64748b !important;
  transition: color 0.18s ease !important;
}

.site-footer a:hover {
  color: #0284c7 !important;
}

.site-footer .footer-social a {
  background: #ffffff !important;
  color: #334155 !important;
  border: 1px solid #e2e8f0 !important;
}

.site-footer .footer-social a:hover {
  background: #0284c7 !important;
  color: #ffffff !important;
  border-color: #0284c7 !important;
}

.site-footer .footer-bottom {
  border-top: 1px solid #e2e8f0 !important;
  color: #64748b !important;
}

.site-footer .footer-bottom a {
  color: #475569 !important;
}

.site-footer .footer-bottom a:hover {
  color: #0284c7 !important;
}
"""

css_text += "\n" + smoke_header_footer_css

with open('static/styles.css', 'w', encoding='utf-8') as f:
    f.write(css_text)
print('styles.css updated with smoke white hero, header, and footer!')
