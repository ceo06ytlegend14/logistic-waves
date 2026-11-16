# Script to restore authentic top header (Image 1) and make hero banner a clean rounded card (fit in rectable)

# 1. Update views.py
with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

start_marker = '<section class="lw-hero-banner-section">'
end_marker = '</section>'

idx1 = views_content.find(start_marker)
idx2 = views_content.find(end_marker, idx1) + len(end_marker)

clean_hero_html = '''<section class="lw-hero-banner-section">
        <div class="container lw-hero-container">
          <div class="hero-shell">
            <div class="hero-photo" aria-hidden="true"></div>

            <div class="hero-inner-wrap">
              <section class="hero-content">
                <div class="eyebrow">Global Logistics Solution</div>
                <h1>Insights for<br><span>Smarter</span> Logistics</h1>
                <p class="intro">Real-time data, greater visibility, and smarter decisions for a more connected supply chain.</p>
                <div class="hero-buttons">
                  <a class="primary" href="/article-blogs">Explore Insights <span aria-hidden="true">&rarr;</span></a>
                  <a class="secondary" href="#overview" onclick="openFwtModal(0); return false;"><span class="play" aria-hidden="true">&#9654;</span> Watch Overview</a>
                </div>
              </section>
            </div>

            <section class="features" aria-label="Our advantages">
              <div class="feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width:24px; height:24px; min-width:24px; min-height:24px; max-width:24px; max-height:24px; flex-shrink:0;"><circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.4 2.5 3.5 5.6 3.5 9.2s-1.1 6.7-3.5 9.2c-2.4-2.5-3.5-5.6-3.5-9.2S9.6 5.3 12 2.8Z"/></svg>
                <span>Worldwide Coverage</span>
              </div>
              <div class="feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="width:24px; height:24px; min-width:24px; min-height:24px; max-width:24px; max-height:24px; flex-shrink:0;"><path d="M13.4 1.5 4.8 13h5.7l-.8 9.5L19.2 10h-6.1l.3-8.5Z"/></svg>
                <span>Real-Time Tracking</span>
              </div>
              <div class="feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width:24px; height:24px; min-width:24px; min-height:24px; max-width:24px; max-height:24px; flex-shrink:0;"><path d="m12 2 8 3v6c0 5.2-3.4 8.7-8 11-4.6-2.3-8-5.8-8-11V5l8-3Z"/><path d="m8 12 2.5 2.5L16 9"/></svg>
                <span>Trusted &amp; Secure</span>
              </div>
              <div class="feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="width:24px; height:24px; min-width:24px; min-height:24px; max-width:24px; max-height:24px; flex-shrink:0;"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><rect x="2.5" y="12" width="4" height="7" rx="1.5"/><rect x="17.5" y="12" width="4" height="7" rx="1.5"/><path d="M18 19c-1 2-3 2.5-6 2.5"/></svg>
                <span>24/7 Support</span>
              </div>
            </section>
          </div>
        </div>
      </section>'''

views_content = views_content[:idx1] + clean_hero_html + views_content[idx2:]
views_content = views_content.replace('?v=20261112_12', '?v=20261112_13')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)
print("views.py updated!")

# 2. Update styles.css
with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'FULL-WIDTH SIGNATURE BLUE HERO BANNER' in l or 'EXACT HERO BANNER IMPLEMENTATION' in l or 'HERO BANNER:' in l:
        start_idx = i
    if start_idx is not None and '/* ==========================================================================' in l and i > start_idx + 20:
        end_idx = i
        break

new_css = """/* ==========================================================================
   AUTHENTIC HEADER + ROUNDED HERO CARD IN SIGNATURE BLUE (#034f9a)
   Matches user reference Image 1: Clean solid header bar on top,
   and rounded rectangle hero card ("fit in rectable") below it.
   ========================================================================== */

/* Make sure the site-header is always displayed with pure solid blue #034f9a */
.site-header {
  background: #034f9a !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 100 !important;
  box-shadow: 0 2px 10px rgba(15, 60, 80, 0.15) !important;
}

.lw-hero-banner-section {
  padding: 24px 0 20px 0 !important;
  background: transparent !important;
}

.lw-hero-banner-section .container,
.lw-hero-container {
  width: min(1380px, 96%) !important;
  max-width: 1380px !important;
  padding: 0 16px !important;
  margin: 0 auto !important;
}

.hero-shell {
  --navy: #034f9a;
  --navy-2: #02386e;
  --blue: #0084ff;
  --white: #fff;
  --muted: #d0e2f5;
  position: relative !important;
  isolation: isolate !important;
  width: 100% !important;
  max-width: 1380px !important;
  min-height: 480px !important;
  margin: 0 auto !important;
  overflow: hidden !important;
  border-radius: 22px !important;
  background: linear-gradient(135deg, #02386e 0%, #034f9a 100%) !important;
  box-shadow: 0 16px 45px rgba(3, 79, 154, 0.28), 0 2px 12px rgba(0, 0, 0, 0.1) !important;
  border: 1px solid rgba(56, 189, 248, 0.22) !important;
  color: var(--white) !important;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
}

.hero-photo {
  position: absolute !important;
  z-index: -2 !important;
  inset: 0 0 0 38% !important;
  background:
    linear-gradient(90deg, #034f9a 0%, rgba(3,79,154,.85) 15%, rgba(3,79,154,.38) 32%, rgba(3,79,154,.02) 65%),
    linear-gradient(0deg, rgba(3,79,154,.65), transparent 45%),
    url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat !important;
}

.hero-shell::before {
  content: "" !important;
  position: absolute !important;
  z-index: -1 !important;
  inset: 0 !important;
  pointer-events: none !important;
  background: linear-gradient(112deg, #022e5e 0%, #034f9a 49%, transparent 49.1%) !important;
  clip-path: polygon(0 0, 68% 0, 44% 100%, 0 100%) !important;
}

.hero-shell::after {
  content: "" !important;
  position: absolute !important;
  z-index: -1 !important;
  top: -15% !important;
  left: 49% !important;
  width: 180px !important;
  height: 135% !important;
  transform: skewX(-34deg) !important;
  background: rgba(56, 189, 248, .18) !important;
  border-left: 1px solid rgba(255,255,255,.14) !important;
  border-right: 1px solid rgba(255,255,255,.08) !important;
}

.hero-shell .hero-inner-wrap {
  position: relative !important;
  z-index: 2 !important;
  padding: 44px 48px 24px 48px !important;
}

.hero-shell .hero-content {
  width: min(650px, 58%) !important;
}

.hero-shell .eyebrow {
  display: inline-flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 7px 16px !important;
  border-radius: 999px !important;
  background: rgba(255, 255, 255, .14) !important;
  border: 1px solid rgba(255, 255, 255, .24) !important;
  color: #f0f7ff !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  backdrop-filter: blur(8px) !important;
}

.hero-shell .eyebrow::before {
  content: "" !important;
  width: 8px !important;
  height: 8px !important;
  border-radius: 50% !important;
  background: #38bdf8 !important;
  box-shadow: 0 0 12px #38bdf8 !important;
}

.hero-shell h1 {
  max-width: 650px !important;
  margin: 20px 0 16px !important;
  font-size: clamp(38px, 4vw, 54px) !important;
  line-height: 1.08 !important;
  letter-spacing: -.03em !important;
  font-weight: 800 !important;
  color: #ffffff !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
}

.hero-shell h1 span {
  color: #38bdf8 !important;
  text-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
}

.hero-shell .intro {
  max-width: 500px !important;
  margin: 0 !important;
  color: var(--muted) !important;
  font-size: 15.5px !important;
  line-height: 1.6 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.25) !important;
}

.hero-shell .hero-buttons {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 14px !important;
  margin-top: 26px !important;
}

.hero-shell .primary,
.hero-shell .secondary {
  min-height: 48px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  padding: 0 24px !important;
  border-radius: 999px !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  text-decoration: none !important;
  transition: .2s ease !important;
}

.hero-shell .primary {
  background: #0284c7 !important;
  background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 8px 24px rgba(0, 102, 238, .45) !important;
}

.hero-shell .secondary {
  border: 1px solid rgba(255, 255, 255, .4) !important;
  background: rgba(2, 45, 92, .45) !important;
  color: white !important;
  backdrop-filter: blur(8px) !important;
  cursor: pointer !important;
}

.hero-shell .secondary:hover {
  background: rgba(255, 255, 255, .18) !important;
  border-color: rgba(255, 255, 255, .7) !important;
  color: white !important;
}

.hero-shell .play {
  width: 20px !important;
  height: 20px !important;
  display: grid !important;
  place-items: center !important;
  border: 1.5px solid white !important;
  border-radius: 50% !important;
  font-size: 10px !important;
}

.hero-shell .features {
  position: relative !important;
  z-index: 2 !important;
  display: flex !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 0 !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 16px 48px !important;
  border-top: 1px solid rgba(255,255,255,.14) !important;
  background: rgba(2, 38, 76, 0.55) !important;
  backdrop-filter: blur(10px) !important;
}

.hero-shell .feature {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 0 clamp(14px, 2vw, 36px) !important;
  color: #eaf2fb !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  border-right: 1px solid rgba(255,255,255,.2) !important;
}

.hero-shell .feature:first-child {
  padding-left: 0 !important;
}

.hero-shell .feature:last-child {
  border-right: 0 !important;
}

.hero-shell .feature svg {
  width: 22px !important;
  height: 22px !important;
  min-width: 22px !important;
  min-height: 22px !important;
  max-width: 22px !important;
  max-height: 22px !important;
  color: #38bdf8 !important;
  filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5)) !important;
  flex: 0 0 auto !important;
  display: block !important;
}

@media (max-width: 900px) {
  .hero-shell { min-height: 480px !important; }
  .hero-photo { inset: 38% 0 0 0 !important; background-position: center !important; }
  .hero-shell::before {
    background: linear-gradient(180deg, #022e5e 0%, #034f9a 48%, rgba(3,79,154,.25) 100%) !important;
    clip-path: none !important;
  }
  .hero-shell::after { display: none !important; }
  .hero-shell .hero-inner-wrap { padding: 32px 24px 20px 24px !important; }
  .hero-shell .hero-content { width: 100% !important; }
  .hero-shell h1 { font-size: clamp(34px, 6vw, 44px) !important; }
  .hero-shell .features { gap: 14px 0 !important; padding: 14px 20px !important; }
  .hero-shell .feature { width: 50% !important; padding: 6px 8px !important; border-right: 0 !important; font-size: 12.5px !important; }
  .hero-shell .feature:nth-child(odd) { padding-left: 0 !important; }
}

@media (max-width: 520px) {
  .hero-shell { min-height: auto !important; border-radius: 16px !important; }
  .hero-shell .hero-inner-wrap { padding: 24px 18px 18px 18px !important; }
  .hero-shell .eyebrow { font-size: 10px !important; }
  .hero-shell h1 { font-size: 30px !important; margin: 14px 0 !important; }
  .hero-shell .intro { font-size: 14px !important; }
  .hero-shell .hero-buttons { gap: 10px !important; margin-top: 20px !important; }
  .hero-shell .primary, .hero-shell .secondary { min-height: 44px !important; padding: 0 16px !important; font-size: 13px !important; }
  .hero-shell .hero-photo { inset: 45% 0 0 0 !important; }
  .hero-shell .features { padding: 14px 16px !important; }
  .hero-shell .feature { width: 100% !important; font-size: 12px !important; gap: 8px !important; }
  .hero-shell .feature svg { width: 18px !important; height: 18px !important; }
}
"""

new_file_lines = lines[:start_idx] + [new_css] + lines[end_idx:]

with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
    f.writelines(new_file_lines)

print("styles.css updated with authentic header and clean rounded hero card!")
