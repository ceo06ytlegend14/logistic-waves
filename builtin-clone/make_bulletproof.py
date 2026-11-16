# Script to make hero completely bulletproof with inline style and strict SVG dimensions

with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

start_marker = '<section class="lw-hero-banner-section">'
end_marker = '</section>'

idx1 = views_content.find(start_marker)
idx2 = views_content.find(end_marker, idx1) + len(end_marker)

bulletproof_hero_html = '''<section class="lw-hero-banner-section">
        <style>
          /* Bulletproof inline styles for hero banner */
          .page-home .site-header { display: none !important; }
          .lw-hero-banner-section {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
            background: #034f9a !important;
            overflow: hidden !important;
          }
          .hero-shell {
            position: relative !important;
            isolation: isolate !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: 600px !important;
            margin: 0 !important;
            overflow: hidden !important;
            background: linear-gradient(135deg, #034f9a 0%, #065eb8 100%) !important;
            color: #ffffff !important;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            box-shadow: 0 10px 40px rgba(3, 79, 154, 0.35) !important;
          }
          .hero-photo {
            position: absolute !important;
            z-index: -2 !important;
            inset: 0 0 0 36% !important;
            background:
              linear-gradient(90deg, #034f9a 0%, rgba(3,79,154,.88) 16%, rgba(3,79,154,.38) 32%, rgba(3,79,154,.02) 65%),
              linear-gradient(0deg, rgba(3,79,154,.65), transparent 45%),
              url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat !important;
          }
          .hero-shell::before {
            content: "" !important;
            position: absolute !important;
            z-index: -1 !important;
            inset: 0 !important;
            pointer-events: none !important;
            background: linear-gradient(112deg, #023d77 0%, #034f9a 49%, transparent 49.1%) !important;
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
            background: rgba(56, 189, 248, .20) !important;
            border-left: 1px solid rgba(255,255,255,.16) !important;
            border-right: 1px solid rgba(255,255,255,.10) !important;
            pointer-events: none !important;
          }
          .hero-shell .topbar {
            min-height: 84px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 28px !important;
            max-width: 1440px !important;
            margin: 0 auto !important;
            padding: 16px clamp(20px, 4vw, 56px) !important;
            border-bottom: 1px solid rgba(255,255,255,.14) !important;
          }
          .hero-shell .brand {
            display: flex !important;
            align-items: center !important;
            flex: 0 0 auto !important;
            text-decoration: none !important;
            gap: 12px !important;
          }
          .hero-shell .nav {
            display: flex !important;
            align-items: center !important;
            gap: clamp(18px, 3vw, 44px) !important;
            color: #eaf2fb !important;
            font-size: 15px !important;
            font-weight: 600 !important;
          }
          .hero-shell .nav a {
            transition: color .2s ease !important;
            color: #eaf2fb !important;
            text-decoration: none !important;
          }
          .hero-shell .nav a:hover {
            color: #7dd3fc !important;
          }
          .hero-shell .nav .active {
            position: relative !important;
            color: #ffffff !important;
          }
          .hero-shell .nav .active::after {
            content: "" !important;
            position: absolute !important;
            left: 0 !important;
            right: 0 !important;
            bottom: -19px !important;
            height: 3px !important;
            border-radius: 5px !important;
            background: #38bdf8 !important;
            box-shadow: 0 0 10px #38bdf8 !important;
          }
          .hero-shell .nav-actions {
            display: flex !important;
            align-items: center !important;
            gap: 22px !important;
          }
          .hero-shell .search {
            width: 40px !important;
            height: 40px !important;
            display: grid !important;
            place-items: center !important;
            border-left: 1px solid rgba(255,255,255,.28) !important;
            padding-left: 20px !important;
            background: transparent !important;
            border-top: none !important;
            border-right: none !important;
            border-bottom: none !important;
            color: #fff !important;
            cursor: pointer !important;
          }
          .hero-shell .search svg {
            width: 21px !important;
            height: 21px !important;
            max-width: 21px !important;
            max-height: 21px !important;
            display: block !important;
          }
          .hero-shell .quote {
            display: inline-flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 12px 24px !important;
            border-radius: 999px !important;
            background: #0284c7 !important;
            background: linear-gradient(135deg, #0284c7 0%, #0066ee 100%) !important;
            color: white !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            text-decoration: none !important;
            box-shadow: 0 6px 20px rgba(0, 102, 238, .35) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            transition: transform .2s ease, background .2s ease !important;
          }
          .hero-shell .quote:hover,
          .hero-shell .primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(0, 102, 238, .55) !important;
            color: white !important;
          }
          .hero-shell .hero-inner-wrap {
            max-width: 1440px !important;
            margin: 0 auto !important;
            padding: 0 clamp(20px, 4vw, 56px) !important;
          }
          .hero-shell .hero-content {
            width: min(720px, 58%) !important;
            padding: clamp(40px, 5vw, 76px) 0 32px 0 !important;
          }
          .hero-shell .eyebrow {
            display: inline-flex !important;
            align-items: center !important;
            gap: 10px !important;
            padding: 8px 16px !important;
            border-radius: 999px !important;
            background: rgba(255, 255, 255, .15) !important;
            border: 1px solid rgba(255, 255, 255, .25) !important;
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
            max-width: 720px !important;
            margin: 22px 0 18px !important;
            font-size: clamp(40px, 4.8vw, 68px) !important;
            line-height: 1.06 !important;
            letter-spacing: -.04em !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
          }
          .hero-shell h1 span {
            color: #38bdf8 !important;
            text-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
          }
          .hero-shell .intro {
            max-width: 540px !important;
            margin: 0 !important;
            color: #d0e2f5 !important;
            font-size: clamp(15px, 1.3vw, 18.5px) !important;
            line-height: 1.65 !important;
            text-shadow: 0 1px 4px rgba(0,0,0,0.25) !important;
          }
          .hero-shell .hero-buttons {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 16px !important;
            margin-top: 30px !important;
          }
          .hero-shell .primary,
          .hero-shell .secondary {
            min-height: 50px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 12px !important;
            padding: 0 26px !important;
            border-radius: 999px !important;
            font-size: 15px !important;
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
            width: 22px !important;
            height: 22px !important;
            display: grid !important;
            place-items: center !important;
            border: 1.5px solid white !important;
            border-radius: 50% !important;
            font-size: 10px !important;
          }
          .hero-shell .features {
            display: flex !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 0 !important;
            max-width: 1440px !important;
            margin: 44px auto 0 !important;
            padding: 18px clamp(20px, 4vw, 56px) 22px !important;
            border-top: 1px solid rgba(255,255,255,.16) !important;
          }
          .hero-shell .feature {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 0 clamp(16px, 2.5vw, 40px) !important;
            color: #eaf2fb !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            border-right: 1px solid rgba(255,255,255,.24) !important;
          }
          .hero-shell .feature:first-child {
            padding-left: 0 !important;
          }
          .hero-shell .feature:last-child {
            border-right: 0 !important;
          }
          .hero-shell .feature svg {
            width: 24px !important;
            height: 24px !important;
            min-width: 24px !important;
            min-height: 24px !important;
            max-width: 24px !important;
            max-height: 24px !important;
            color: #38bdf8 !important;
            filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5)) !important;
            flex: 0 0 auto !important;
            display: block !important;
          }
          @media (max-width: 900px) {
            .hero-shell { min-height: 720px !important; }
            .hero-shell .topbar { padding: 16px 20px !important; }
            .hero-shell .nav { display: none !important; }
            .hero-photo { inset: 38% 0 0 0 !important; background-position: center !important; }
            .hero-shell::before {
              background: linear-gradient(180deg, #022e5e 0%, #034f9a 48%, rgba(3,79,154,.25) 100%) !important;
              clip-path: none !important;
            }
            .hero-shell::after { display: none !important; }
            .hero-shell .hero-content { width: 100% !important; padding: 44px 0 0 !important; }
            .hero-shell h1 { font-size: clamp(36px, 8vw, 54px) !important; }
            .hero-shell .features { margin: 180px auto 0 !important; gap: 16px 0 !important; padding: 18px 20px !important; }
            .hero-shell .feature { width: 50% !important; padding: 8px 10px !important; border-right: 0 !important; }
            .hero-shell .feature:nth-child(odd) { padding-left: 0 !important; }
          }
        </style>
        
        <main class="hero-shell">
          <div class="hero-photo" aria-hidden="true"></div>
          
          <header class="topbar">
            <a class="brand brand-logistic-waves" href="/" aria-label="Logistics Waves home">
              <span class="brand-diamond-wrap">
                <img class="brand-diamond-logo" src="/static/images/logo_emblem.png" alt="Logistics Waves" />
              </span>
              <span class="brand-text-lw">
                <span class="brand-lw-main">LOGISTICS</span>
                <span class="brand-lw-sub">WAVES</span>
              </span>
            </a>
            <nav class="nav" aria-label="Main navigation">
              <a class="active" href="/">Home</a>
              <a href="/companies">Companies</a>
              <a href="/jobs">Jobs</a>
              <a href="/article-blogs">Articles</a>
              <a href="/courses">Courses</a>
            </nav>
            <div class="nav-actions">
              <button class="search search-trigger" type="button" aria-label="Search">
                <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" style="width:21px; height:21px; max-width:21px; max-height:21px; display:inline-block;"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg>
              </button>
              <a class="quote" href="/employers">Get a Quote <span aria-hidden="true">→</span></a>
            </div>
          </header>

          <div class="hero-inner-wrap">
            <section class="hero-content">
              <div class="eyebrow">Global Logistics Solution</div>
              <h1>Insights for<br><span>Smarter</span> Logistics</h1>
              <p class="intro">Real-time data, greater visibility, and smarter decisions for a more connected supply chain.</p>
              <div class="hero-buttons">
                <a class="primary" href="/article-blogs">Explore Insights <span aria-hidden="true">→</span></a>
                <a class="secondary" href="#overview" onclick="openFwtModal(0); return false;"><span class="play" aria-hidden="true">▶</span> Watch Overview</a>
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
        </main>
      </section>'''

views_content = views_content[:idx1] + bulletproof_hero_html + views_content[idx2:]
views_content = views_content.replace('?v=20261112_11', '?v=20261112_12')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print("views.py updated with bulletproof inline styles and strict SVG dimensions!")
