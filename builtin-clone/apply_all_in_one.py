with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update return layout call in home_page to pass page_class="page-home"
target_layout = '''    return layout("Logistic Waves | Logistics, Supply Chain & Tech Jobs Hub", body, user, active="home",
                  description="Everything for your next move in tech: high-concurrency engineering roles, company insights, and editorial intelligence.",
                  extra_head=extra_head)'''

replacement_layout = '''    return layout("Logistic Waves | Logistics, Supply Chain & Tech Jobs Hub", body, user, active="home",
                  page_class="page-home",
                  description="Everything for your next move in tech: high-concurrency engineering roles, company insights, and editorial intelligence.",
                  extra_head=extra_head)'''

if target_layout in content:
    content = content.replace(target_layout, replacement_layout)
    print("Updated layout call with page_class='page-home'")
else:
    print("Warning: target_layout string not matched exactly, looking for alternate...")
    # search pattern
    import re
    content = re.sub(r'return layout\("Logistic Waves \| Logistics, Supply Chain & Tech Jobs Hub", body, user, active="home",\s*description=',
                     'return layout("Logistic Waves | Logistics, Supply Chain & Tech Jobs Hub", body, user, active="home", page_class="page-home", description=',
                     content)

# 2. Update hero banner section to include the in-card header
start_marker = '<section class="lw-hero-banner-section">'
end_marker = '</section>'

idx1 = content.find(start_marker)
idx2 = content.find(end_marker, idx1) + len(end_marker)

new_hero_html = '''<section class="lw-hero-banner-section">
        <div class="container lw-hero-container">
          <div class="lw-hero-banner-card">
            
            <!-- 1. Unified In-Card Header (Matching Reference Design: Header & Banner in One Rectangle) -->
            <header class="lw-card-header">
              <div class="lw-card-brand">
                <a class="brand brand-logistic-waves" href="/" aria-label="Logistics Waves">
                  <span class="brand-diamond-wrap">
                    <img class="brand-diamond-logo" src="/static/images/logo_emblem.png" alt="Logistics Waves">
                  </span>
                  <span class="brand-text-lw">
                    <span class="brand-lw-main">LOGISTICS</span>
                    <span class="brand-lw-sub">WAVES</span>
                  </span>
                </a>
              </div>
              <nav class="lw-card-nav" aria-label="Card Primary Navigation">
                <a class="lw-card-nav-link active" href="/">Home</a>
                <a class="lw-card-nav-link" href="/companies">Companies</a>
                <a class="lw-card-nav-link" href="/jobs">Jobs</a>
                <a class="lw-card-nav-link" href="/article-blogs">Articles</a>
                <a class="lw-card-nav-link" href="/courses">Courses</a>
              </nav>
              <div class="lw-card-actions">
                <button class="icon-btn search-trigger lw-card-search-btn" type="button" aria-label="Open search">
                  <i class="fa-solid fa-magnifying-glass"></i>
                </button>
                <a class="lw-card-auth-link" href="/auth/login">Join | Log in</a>
                <a class="lw-card-quote-btn" href="/employers">
                  <span>Get a Quote</span>
                  <i class="fa-solid fa-arrow-right"></i>
                </a>
              </div>
            </header>

            <!-- 2. Hero Content & Multi-Modal Visual Row -->
            <div class="lw-hero-main-row">
              <div class="lw-hero-content-col">
                <div class="lw-hero-tag-badge">
                  <span class="lw-badge-dot"></span>
                  <span>Global Logistics Solution</span>
                </div>
                <h1 class="lw-hero-title">
                  Insights for<br><span class="lw-hero-highlight">Smarter</span> Logistics
                </h1>
                <p class="lw-hero-subtitle">
                  Real-time data, greater visibility, and smarter decisions for a more connected supply chain.
                </p>
                <div class="lw-hero-cta-group">
                  <a href="/article-blogs" class="lw-hero-btn-primary">
                    <span>Explore Insights</span>
                    <i class="fa-solid fa-arrow-right"></i>
                  </a>
                  <button type="button" class="lw-hero-btn-secondary" onclick="openFwtModal(0)">
                    <i class="fa-regular fa-circle-play"></i>
                    <span>Watch Overview</span>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 3. Bottom Feature Ribbon -->
            <div class="lw-hero-bottom-ribbon">
              <div class="lw-ribbon-item">
                <i class="fa-solid fa-globe lw-ribbon-icon"></i>
                <span>Worldwide Coverage</span>
              </div>
              <div class="lw-ribbon-divider"></div>
              <div class="lw-ribbon-item">
                <i class="fa-solid fa-bolt lw-ribbon-icon"></i>
                <span>Real-Time Tracking</span>
              </div>
              <div class="lw-ribbon-divider"></div>
              <div class="lw-ribbon-item">
                <i class="fa-solid fa-shield-halved lw-ribbon-icon"></i>
                <span>Trusted &amp; Secure</span>
              </div>
              <div class="lw-ribbon-divider"></div>
              <div class="lw-ribbon-item">
                <i class="fa-solid fa-headset lw-ribbon-icon"></i>
                <span>24/7 Support</span>
              </div>
            </div>
          </div>
        </div>
      </section>'''

content = content[:idx1] + new_hero_html + content[idx2:]

# Bump cache buster
content = content.replace('?v=20261112_7', '?v=20261112_8')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("views.py updated successfully!")
