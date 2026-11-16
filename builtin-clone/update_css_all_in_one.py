with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'HERO BANNER: INSIGHTS FOR SMARTER LOGISTICS' in l:
        start_idx = i
    if start_idx is not None and '/* ==========================================================================' in l and i > start_idx + 20:
        end_idx = i
        break

new_css = """/* ==========================================================================
   HERO BANNER: ALL-IN-ONE (HEADER + BANNER UNIFIED IN 1 RECTANGULAR CARD)
   Matching Logiexpress design reference: Floating card with integrated navbar,
   high-tech multimodal visuals, diagonal light slice, and bottom feature ribbon
   ========================================================================== */

/* Hide the duplicate outer header on the homepage so the in-card header is the only one */
.page-home .site-header {
  display: none !important;
}

.lw-hero-banner-section {
  padding: 24px 0 24px 0 !important;
  background: transparent !important;
}

.lw-hero-banner-section .container,
.lw-hero-container {
  width: min(1380px, 96%) !important;
  max-width: 1380px !important;
  padding: 0 16px !important;
  margin: 0 auto !important;
}

/* The All-in-One Floating Rounded Rectangle */
.lw-hero-banner-card {
  position: relative !important;
  border-radius: 24px !important;
  overflow: hidden !important;
  background-color: #030e22 !important;
  background-image: 
    linear-gradient(108deg, #030d22 0%, #030d22 38%, rgba(3, 13, 34, 0.94) 47%, rgba(3, 13, 34, 0.45) 58%, transparent 72%),
    url('/static/images/hero_multimodal_bg_2x.jpg') !important;
  background-position: center right !important;
  background-size: cover !important;
  background-repeat: no-repeat !important;
  border: 1px solid rgba(56, 189, 248, 0.24) !important;
  box-shadow: 0 24px 60px -12px rgba(2, 14, 38, 0.75), 0 0 35px rgba(0, 132, 255, 0.12) !important;
  min-height: 520px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
}

/* Diagonal glowing accent beam matching reference */
.lw-hero-banner-card::before {
  content: "" !important;
  position: absolute !important;
  top: -60px !important;
  bottom: -60px !important;
  left: 47% !important;
  width: 3px !important;
  background: linear-gradient(180deg, rgba(56, 189, 248, 0.7) 0%, rgba(14, 165, 233, 0.3) 60%, transparent 100%) !important;
  transform: rotate(-22deg) !important;
  transform-origin: center center !important;
  pointer-events: none !important;
  filter: blur(1.5px) drop-shadow(0 0 14px #00c2ff) !important;
  opacity: 0.85 !important;
  z-index: 1 !important;
}

/* Soft ambient glow on left text area */
.lw-hero-banner-card::after {
  content: "" !important;
  position: absolute !important;
  inset: 0 !important;
  background: radial-gradient(circle at 18% 30%, rgba(14, 165, 233, 0.12) 0%, transparent 60%) !important;
  pointer-events: none !important;
  z-index: 1 !important;
}

/* 1. Integrated Header Inside Card */
.lw-card-header {
  position: relative !important;
  z-index: 10 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 22px 46px 14px 46px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.lw-card-brand .brand {
  text-decoration: none !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
}

.lw-card-nav {
  display: flex !important;
  align-items: center !important;
  gap: 32px !important;
}

.lw-card-nav-link {
  color: #cbd5e1 !important;
  font-size: 14.5px !important;
  font-weight: 500 !important;
  text-decoration: none !important;
  padding: 6px 0 !important;
  position: relative !important;
  transition: color 0.2s ease !important;
}

.lw-card-nav-link:hover {
  color: #ffffff !important;
}

.lw-card-nav-link.active {
  color: #ffffff !important;
  font-weight: 600 !important;
}

.lw-card-nav-link.active::after {
  content: "" !important;
  position: absolute !important;
  bottom: -4px !important;
  left: 0 !important;
  right: 0 !important;
  height: 2.5px !important;
  background: #00c2ff !important;
  border-radius: 2px !important;
  box-shadow: 0 0 10px #00c2ff !important;
}

.lw-card-actions {
  display: flex !important;
  align-items: center !important;
  gap: 18px !important;
}

.lw-card-search-btn {
  color: #e2e8f0 !important;
  font-size: 16px !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  padding: 6px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: color 0.2s ease !important;
}

.lw-card-search-btn:hover {
  color: #00c2ff !important;
}

.lw-card-auth-link {
  color: #cbd5e1 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  text-decoration: none !important;
  transition: color 0.2s ease !important;
}

.lw-card-auth-link:hover {
  color: #38bdf8 !important;
}

.lw-card-quote-btn {
  background: #0084ff !important;
  background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%) !important;
  color: #ffffff !important;
  padding: 10px 22px !important;
  border-radius: 9999px !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  box-shadow: 0 4px 18px rgba(0, 119, 255, 0.45) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  transition: all 0.22s ease !important;
  cursor: pointer !important;
}

.lw-card-quote-btn:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 24px rgba(0, 119, 255, 0.65) !important;
  border-color: #38bdf8 !important;
  color: #ffffff !important;
}

/* 2. Hero Content */
.lw-hero-main-row {
  position: relative !important;
  z-index: 2 !important;
  padding: 38px 46px 32px 46px !important;
  max-width: 650px !important;
}

.lw-hero-content-col {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
}

.lw-hero-tag-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 9px !important;
  background: rgba(14, 165, 233, 0.12) !important;
  color: #7dd3fc !important;
  border: 1px solid rgba(56, 189, 248, 0.3) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  padding: 6px 16px !important;
  border-radius: 9999px !important;
  margin-bottom: 18px !important;
  backdrop-filter: blur(8px) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}

.lw-badge-dot {
  width: 8px !important;
  height: 8px !important;
  border-radius: 50% !important;
  background: #00c2ff !important;
  box-shadow: 0 0 10px #00c2ff, 0 0 18px #00c2ff !important;
  display: inline-block !important;
  animation: lw-pulse-dot 2.5s infinite ease-in-out !important;
}

@keyframes lw-pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.55; transform: scale(0.85); }
}

.lw-hero-title {
  font-family: "Plus Jakarta Sans", "Montserrat", system-ui, -apple-system, sans-serif !important;
  font-size: clamp(38px, 4vw, 52px) !important;
  font-weight: 800 !important;
  color: #FFFFFF !important;
  line-height: 1.14 !important;
  letter-spacing: -0.03em !important;
  margin: 0 0 16px 0 !important;
  text-shadow: 0 2px 14px rgba(0, 0, 0, 0.45) !important;
}

.lw-hero-highlight {
  color: #0088ff !important;
  background: linear-gradient(135deg, #00c2ff 0%, #2563eb 100%) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  display: inline-block !important;
  filter: drop-shadow(0 2px 14px rgba(0, 194, 255, 0.4)) !important;
}

.lw-hero-subtitle {
  font-size: 16px !important;
  line-height: 1.6 !important;
  color: #cbd5e1 !important;
  margin: 0 0 28px 0 !important;
  max-width: 500px !important;
  font-weight: 400 !important;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4) !important;
}

.lw-hero-cta-group {
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
  flex-wrap: wrap !important;
}

.lw-hero-btn-primary {
  background: #0084ff !important;
  background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  padding: 12px 28px !important;
  border-radius: 9999px !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 9px !important;
  box-shadow: 0 8px 24px rgba(0, 119, 255, 0.45), 0 2px 8px rgba(0, 0, 0, 0.25) !important;
  transition: all 0.22s ease !important;
  cursor: pointer !important;
}

.lw-hero-btn-primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 30px rgba(0, 119, 255, 0.65) !important;
  border-color: #38bdf8 !important;
  color: #ffffff !important;
}

.lw-hero-btn-secondary {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  padding: 12px 24px !important;
  border-radius: 9999px !important;
  font-size: 14.5px !important;
  font-weight: 600 !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 9px !important;
  transition: all 0.22s ease !important;
  backdrop-filter: blur(10px) !important;
  cursor: pointer !important;
}

.lw-hero-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.16) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  transform: translateY(-2px) !important;
  color: #ffffff !important;
}

.lw-hero-btn-secondary i {
  font-size: 16px !important;
  color: #38bdf8 !important;
}

/* 3. Bottom Feature Ribbon */
.lw-hero-bottom-ribbon {
  position: relative !important;
  z-index: 2 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 14px 44px !important;
  background: rgba(2, 10, 26, 0.78) !important;
  backdrop-filter: blur(14px) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.lw-ribbon-item {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  color: #cbd5e1 !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em !important;
}

.lw-ribbon-icon {
  color: #00c2ff !important;
  font-size: 16px !important;
  filter: drop-shadow(0 0 6px rgba(0, 194, 255, 0.5)) !important;
}

.lw-ribbon-divider {
  width: 1px !important;
  height: 18px !important;
  background: rgba(255, 255, 255, 0.15) !important;
}

@media (max-width: 960px) {
  .lw-card-nav {
    display: none !important;
  }
  .lw-card-header {
    padding: 18px 20px 12px 20px !important;
  }
  .lw-hero-banner-card {
    background-image: 
      linear-gradient(180deg, rgba(3, 13, 34, 0.94) 0%, rgba(3, 13, 34, 0.8) 60%, rgba(3, 13, 34, 0.98) 100%),
      url('/static/images/hero_multimodal_bg_2x.jpg') !important;
    min-height: auto !important;
  }
  .lw-hero-banner-card::before {
    display: none !important;
  }
  .lw-hero-main-row {
    padding: 30px 20px 24px 20px !important;
    max-width: 100% !important;
  }
  .lw-hero-title {
    font-size: 32px !important;
  }
  .lw-hero-bottom-ribbon {
    flex-wrap: wrap !important;
    gap: 12px 20px !important;
    padding: 14px 18px !important;
    justify-content: flex-start !important;
  }
  .lw-ribbon-divider {
    display: none !important;
  }
  .lw-ribbon-item {
    width: 45% !important;
    font-size: 12.5px !important;
  }
}

"""

new_file_lines = lines[:start_idx] + [new_css] + lines[end_idx:]

with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
    f.writelines(new_file_lines)

print("styles.css updated with all-in-one styles!")
