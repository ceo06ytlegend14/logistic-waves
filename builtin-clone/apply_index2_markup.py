# Script to apply the exact index (2).html code into views.py and styles.css

with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

start_marker = '<section class="lw-hero-banner-section">'
end_marker = '</section>'

idx1 = views_content.find(start_marker)
idx2 = views_content.find(end_marker, idx1) + len(end_marker)

new_hero_html = '''<section class="lw-hero-banner-section">
        <div class="container lw-hero-container">
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
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg>
                </button>
                <a class="quote" href="/employers">Get a Quote <span aria-hidden="true">→</span></a>
              </div>
            </header>

            <section class="hero-content">
              <div class="eyebrow">Global Logistics Solution</div>
              <h1>Insights for<br><span>Smarter</span> Logistics</h1>
              <p class="intro">Real-time data, greater visibility, and smarter decisions for a more connected supply chain.</p>
              <div class="hero-buttons">
                <a class="primary" href="/article-blogs">Explore Insights <span aria-hidden="true">→</span></a>
                <a class="secondary" href="#overview" onclick="openFwtModal(0); return false;"><span class="play" aria-hidden="true">▶</span> Watch Overview</a>
              </div>
            </section>

            <section class="features" aria-label="Our advantages">
              <div class="feature">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.4 2.5 3.5 5.6 3.5 9.2s-1.1 6.7-3.5 9.2c-2.4-2.5-3.5-5.6-3.5-9.2S9.6 5.3 12 2.8Z"/></svg>
                Worldwide Coverage
              </div>
              <div class="feature">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.4 1.5 4.8 13h5.7l-.8 9.5L19.2 10h-6.1l.3-8.5Z"/></svg>
                Real-Time Tracking
              </div>
              <div class="feature">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m12 2 8 3v6c0 5.2-3.4 8.7-8 11-4.6-2.3-8-5.8-8-11V5l8-3Z"/><path d="m8 12 2.5 2.5L16 9"/></svg>
                Trusted &amp; Secure
              </div>
              <div class="feature">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><rect x="2.5" y="12" width="4" height="7" rx="1.5"/><rect x="17.5" y="12" width="4" height="7" rx="1.5"/><path d="M18 19c-1 2-3 2.5-6 2.5"/></svg>
                24/7 Support
              </div>
            </section>
          </main>
        </div>
      </section>'''

views_content = views_content[:idx1] + new_hero_html + views_content[idx2:]
views_content = views_content.replace('?v=20261112_8', '?v=20261112_9')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print("views.py updated successfully with exact index (2).html markup!")
