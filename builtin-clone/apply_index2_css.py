with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'HERO BANNER:' in l:
        start_idx = i
    if start_idx is not None and '/* ==========================================================================' in l and i > start_idx + 20:
        end_idx = i
        break

new_css = """/* ==========================================================================
   EXACT HERO BANNER IMPLEMENTATION FROM INDEX (2).HTML
   Unified All-in-One Rectangle (Header + Banner + Features inside 1 Shell)
   ========================================================================== */

/* Hide default outer site header on homepage */
.page-home .site-header {
  display: none !important;
}

.lw-hero-banner-section {
  padding: 24px 0 24px 0 !important;
  background: transparent !important;
}

.lw-hero-banner-section .container,
.lw-hero-container {
  width: min(1500px, 96%) !important;
  max-width: 1500px !important;
  padding: 0 16px !important;
  margin: 0 auto !important;
}

.hero-shell {
  --navy: #061b35;
  --navy-2: #092b50;
  --blue: #168cf4;
  --white: #fff;
  --muted: #c4d1df;
  position: relative;
  isolation: isolate;
  max-width: 1600px;
  min-height: 650px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 24px;
  background: var(--navy);
  box-shadow: 0 18px 50px rgba(6, 27, 53, .20);
  color: var(--white);
  font-family: Inter, Arial, sans-serif;
}

.hero-photo {
  position: absolute;
  z-index: -2;
  inset: 0 0 0 38%;
  background:
    linear-gradient(90deg, rgba(6,27,53,.92) 0%, rgba(6,27,53,.34) 29%, rgba(6,27,53,.03) 65%),
    linear-gradient(0deg, rgba(3,18,36,.42), transparent 45%),
    url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat;
}

.hero-shell::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(112deg, #061a32 0%, #08294b 49%, transparent 49.1%);
  clip-path: polygon(0 0, 69% 0, 43% 100%, 0 100%);
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
  background: rgba(20, 132, 230, .16);
  border-left: 1px solid rgba(255,255,255,.10);
  border-right: 1px solid rgba(255,255,255,.08);
}

.hero-shell .topbar {
  min-height: 92px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  padding: 20px clamp(24px, 5vw, 72px);
  border-bottom: 1px solid rgba(255,255,255,.09);
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
  font-size: 14px;
  font-weight: 600;
}

.hero-shell .nav a {
  transition: color .2s ease;
  color: #eaf2fb;
  text-decoration: none;
}

.hero-shell .nav a:hover {
  color: #59b3ff;
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
  background: var(--blue);
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
  padding: 14px 22px;
  border-radius: 999px;
  background: var(--blue);
  color: white;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(22,140,244,.25);
  transition: transform .2s ease, background .2s ease;
}

.hero-shell .quote:hover,
.hero-shell .primary:hover {
  transform: translateY(-2px);
  background: #0878dc;
  color: white;
}

.hero-shell .hero-content {
  width: min(760px, 57%);
  padding: clamp(48px, 6vw, 92px) 0 34px clamp(24px, 5vw, 72px);
}

.hero-shell .eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 15px;
  border-radius: 999px;
  background: rgba(107,169,220,.14);
  border: 1px solid rgba(142,196,239,.22);
  color: #d8e9f8;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
}

.hero-shell .eyebrow::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2da5ff;
  box-shadow: 0 0 12px #2da5ff;
}

.hero-shell h1 {
  max-width: 760px;
  margin: 26px 0 22px;
  font-size: clamp(44px, 5.2vw, 78px);
  line-height: .99;
  letter-spacing: -.065em;
  font-weight: 800;
  color: #ffffff;
}

.hero-shell h1 span {
  color: #168cf4;
}

.hero-shell .intro {
  max-width: 570px;
  margin: 0;
  color: var(--muted);
  font-size: clamp(15px, 1.35vw, 20px);
  line-height: 1.65;
}

.hero-shell .hero-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 34px;
}

.hero-shell .primary,
.hero-shell .secondary {
  min-height: 54px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 13px;
  padding: 0 25px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: .2s ease;
}

.hero-shell .primary {
  background: var(--blue);
  color: white;
  box-shadow: 0 10px 28px rgba(22,140,244,.26);
}

.hero-shell .secondary {
  border: 1px solid rgba(235,244,255,.65);
  background: rgba(5,24,45,.34);
  color: white;
  cursor: pointer;
}

.hero-shell .secondary:hover {
  background: rgba(255,255,255,.12);
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
  margin: 54px clamp(24px, 5vw, 72px) 0;
  padding: 22px 0 28px;
  border-top: 1px solid rgba(255,255,255,.13);
}

.hero-shell .feature {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 0 clamp(16px, 2.5vw, 40px);
  color: #e1eaf4;
  font-size: 14px;
  font-weight: 500;
  border-right: 1px solid rgba(255,255,255,.48);
}

.hero-shell .feature:first-child {
  padding-left: 0;
}

.hero-shell .feature:last-child {
  border-right: 0;
}

.hero-shell .feature svg {
  width: 25px;
  height: 25px;
  color: #168cf4;
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .hero-shell { min-height: 760px; }
  .hero-shell .topbar { padding: 18px 24px; }
  .hero-shell .nav { display: none; }
  .hero-photo { inset: 38% 0 0 0; background-position: center; }
  .hero-shell::before {
    background: linear-gradient(180deg, #061a32 0%, #08294b 48%, rgba(8,41,75,.18) 100%);
    clip-path: none;
  }
  .hero-shell::after { display: none; }
  .hero-shell .hero-content { width: 100%; padding: 62px 28px 0; }
  .hero-shell h1 { max-width: 650px; font-size: clamp(44px, 8vw, 68px); }
  .hero-shell .features { margin: 230px 28px 0; gap: 18px 0; }
  .hero-shell .feature { width: 50%; padding: 8px 12px; border-right: 0; }
  .hero-shell .feature:nth-child(odd) { padding-left: 0; }
}

@media (max-width: 520px) {
  .hero-shell { min-height: 820px; border-radius: 16px; }
  .hero-shell .topbar { min-height: 76px; padding: 16px 20px; }
  .hero-shell .search { display: none; }
  .hero-shell .quote { padding: 11px 14px; font-size: 12px; }
  .hero-shell .hero-content { padding: 48px 22px 0; }
  .hero-shell .eyebrow { font-size: 10px; }
  .hero-shell h1 { margin-top: 22px; font-size: 44px; }
  .hero-shell .intro { font-size: 15px; }
  .hero-shell .hero-buttons { gap: 10px; margin-top: 26px; }
  .hero-shell .primary, .hero-shell .secondary { min-height: 49px; padding: 0 16px; font-size: 13px; }
  .hero-shell .hero-photo { inset: 43% 0 0 0; }
  .hero-shell .features { margin: 225px 22px 0; padding-top: 18px; }
  .hero-shell .feature { width: 100%; font-size: 12px; gap: 8px; }
  .hero-shell .feature svg { width: 21px; height: 21px; }
}
"""

new_file_lines = lines[:start_idx] + [new_css] + lines[end_idx:]

with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
    f.writelines(new_file_lines)

print("styles.css updated with exact index (2).html CSS rules!")
