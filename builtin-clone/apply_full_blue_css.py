# Script to update hero to full-width edge-to-edge with #034f9a signature blue background

with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'EXACT HERO BANNER IMPLEMENTATION FROM INDEX (2).HTML' in l or 'HERO BANNER:' in l:
        start_idx = i
    if start_idx is not None and '/* ==========================================================================' in l and i > start_idx + 20:
        end_idx = i
        break

new_css = """/* ==========================================================================
   FULL-WIDTH SIGNATURE BLUE HERO BANNER (#034f9a FULL BLEED EDGE-TO-EDGE)
   All-in-one topbar + hero + features in full-width signature blue background
   ========================================================================== */

/* Hide default outer site header on homepage */
.page-home .site-header {
  display: none !important;
}

.lw-hero-banner-section {
  padding: 0 !important;
  margin: 0 !important;
  width: 100% !important;
  background: #034f9a !important;
}

.lw-hero-banner-section .container,
.lw-hero-container {
  width: 100% !important;
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

.hero-shell {
  --navy: #034f9a;
  --navy-2: #02386e;
  --blue: #0084ff;
  --white: #fff;
  --muted: #d0e2f5;
  position: relative;
  isolation: isolate;
  width: 100%;
  max-width: 100%;
  min-height: 620px;
  margin: 0;
  overflow: hidden;
  border-radius: 0;
  background: var(--navy);
  box-shadow: 0 10px 40px rgba(3, 79, 154, .30);
  color: var(--white);
  font-family: Inter, Arial, sans-serif;
}

.hero-photo {
  position: absolute;
  z-index: -2;
  inset: 0 0 0 36%;
  background:
    linear-gradient(90deg, rgba(3,79,154,.96) 0%, rgba(3,79,154,.42) 28%, rgba(3,79,154,.06) 65%),
    linear-gradient(0deg, rgba(2,45,92,.55), transparent 45%),
    url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat;
}

.hero-shell::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(112deg, #022e5e 0%, #034f9a 49%, transparent 49.1%);
  clip-path: polygon(0 0, 68% 0, 44% 100%, 0 100%);
}

.hero-shell::after {
  content: "";
  position: absolute;
  z-index: -1;
  top: -15%;
  left: 49%;
  width: 180px;
  height: 135%;
  transform: skewX(-34deg);
  background: rgba(56, 189, 248, .18);
  border-left: 1px solid rgba(255,255,255,.14);
  border-right: 1px solid rgba(255,255,255,.10);
}

.hero-shell .topbar {
  min-height: 84px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  max-width: 1440px;
  margin: 0 auto;
  padding: 16px clamp(20px, 4vw, 56px);
  border-bottom: 1px solid rgba(255,255,255,.12);
}

.hero-shell .brand {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  text-decoration: none;
  gap: 12px;
}

.hero-shell .nav {
  display: flex;
  align-items: center;
  gap: clamp(18px, 3vw, 44px);
  color: #eaf2fb;
  font-size: 15px;
  font-weight: 600;
}

.hero-shell .nav a {
  transition: color .2s ease;
  color: #eaf2fb;
  text-decoration: none;
}

.hero-shell .nav a:hover {
  color: #7dd3fc;
}

.hero-shell .nav .active {
  position: relative;
  color: #ffffff;
}

.hero-shell .nav .active::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -19px;
  height: 3px;
  border-radius: 5px;
  background: #38bdf8;
  box-shadow: 0 0 10px #38bdf8;
}

.hero-shell .nav-actions {
  display: flex;
  align-items: center;
  gap: 22px;
}

.hero-shell .search {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-left: 1px solid rgba(255,255,255,.28);
  padding-left: 20px;
  background: transparent;
  border-top: none;
  border-right: none;
  border-bottom: none;
  color: #fff;
  cursor: pointer;
}

.hero-shell .search svg {
  width: 21px;
  height: 21px;
}

.hero-shell .quote {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  border-radius: 999px;
  background: #0284c7;
  background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%);
  color: white;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 6px 20px rgba(0, 102, 238, .35);
  border: 1px solid rgba(255, 255, 255, 0.25);
  transition: transform .2s ease, background .2s ease;
}

.hero-shell .quote:hover,
.hero-shell .primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 102, 238, .55);
  color: white;
}

.hero-shell .hero-inner-wrap {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 clamp(20px, 4vw, 56px);
}

.hero-shell .hero-content {
  width: min(720px, 58%);
  padding: clamp(44px, 5.5vw, 84px) 0 32px 0;
}

.hero-shell .eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .14);
  border: 1px solid rgba(255, 255, 255, .25);
  color: #f0f7ff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
  backdrop-filter: blur(8px);
}

.hero-shell .eyebrow::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #38bdf8;
  box-shadow: 0 0 12px #38bdf8;
}

.hero-shell h1 {
  max-width: 720px;
  margin: 24px 0 20px;
  font-size: clamp(42px, 5vw, 72px);
  line-height: 1.05;
  letter-spacing: -.04em;
  font-weight: 800;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.hero-shell h1 span {
  color: #38bdf8;
  text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
}

.hero-shell .intro {
  max-width: 540px;
  margin: 0;
  color: var(--muted);
  font-size: clamp(15px, 1.3vw, 19px);
  line-height: 1.65;
  text-shadow: 0 1px 4px rgba(0,0,0,0.25);
}

.hero-shell .hero-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 32px;
}

.hero-shell .primary,
.hero-shell .secondary {
  min-height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 26px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: .2s ease;
}

.hero-shell .primary {
  background: #0284c7;
  background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 24px rgba(0, 102, 238, .45);
}

.hero-shell .secondary {
  border: 1px solid rgba(255, 255, 255, .4);
  background: rgba(2, 45, 92, .45);
  color: white;
  backdrop-filter: blur(8px);
  cursor: pointer;
}

.hero-shell .secondary:hover {
  background: rgba(255, 255, 255, .18);
  border-color: rgba(255, 255, 255, .7);
  color: white;
}

.hero-shell .play {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border: 1.5px solid white;
  border-radius: 50%;
  font-size: 10px;
}

.hero-shell .features {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
  max-width: 1440px;
  margin: 48px auto 0;
  padding: 20px clamp(20px, 4vw, 56px) 24px;
  border-top: 1px solid rgba(255,255,255,.14);
}

.hero-shell .feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 clamp(16px, 2.5vw, 40px);
  color: #eaf2fb;
  font-size: 14px;
  font-weight: 600;
  border-right: 1px solid rgba(255,255,255,.24);
}

.hero-shell .feature:first-child {
  padding-left: 0;
}

.hero-shell .feature:last-child {
  border-right: 0;
}

.hero-shell .feature svg {
  width: 24px;
  height: 24px;
  color: #38bdf8;
  filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5));
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .hero-shell { min-height: 720px; }
  .hero-shell .topbar { padding: 16px 20px; }
  .hero-shell .nav { display: none; }
  .hero-photo { inset: 38% 0 0 0; background-position: center; }
  .hero-shell::before {
    background: linear-gradient(180deg, #022e5e 0%, #034f9a 48%, rgba(3,79,154,.25) 100%);
    clip-path: none;
  }
  .hero-shell::after { display: none; }
  .hero-shell .hero-content { width: 100%; padding: 48px 0 0; }
  .hero-shell h1 { font-size: clamp(38px, 8vw, 56px); }
  .hero-shell .features { margin: 200px auto 0; gap: 16px 0; padding: 18px 20px; }
  .hero-shell .feature { width: 50%; padding: 8px 10px; border-right: 0; }
  .hero-shell .feature:nth-child(odd) { padding-left: 0; }
}

@media (max-width: 520px) {
  .hero-shell { min-height: 780px; }
  .hero-shell .topbar { min-height: 70px; padding: 14px 16px; }
  .hero-shell .search { display: none; }
  .hero-shell .quote { padding: 10px 16px; font-size: 12px; }
  .hero-shell .hero-content { padding: 36px 0 0; }
  .hero-shell .eyebrow { font-size: 10.5px; }
  .hero-shell h1 { margin-top: 18px; font-size: 38px; }
  .hero-shell .intro { font-size: 14.5px; }
  .hero-shell .hero-buttons { gap: 10px; margin-top: 24px; }
  .hero-shell .primary, .hero-shell .secondary { min-height: 46px; padding: 0 16px; font-size: 13px; }
  .hero-shell .hero-photo { inset: 42% 0 0 0; }
  .hero-shell .features { margin: 190px auto 0; padding: 16px; }
  .hero-shell .feature { width: 100%; font-size: 12px; gap: 8px; }
  .hero-shell .feature svg { width: 20px; height: 20px; }
}
"""

new_file_lines = lines[:start_idx] + [new_css] + lines[end_idx:]

with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
    f.writelines(new_file_lines)

print("styles.css updated with full-width blue hero!")
