import re

with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<section class="lw-hero-banner-section">'
end_marker = '</section>'

idx1 = content.find(start_marker)
if idx1 == -1:
    print("Start marker not found!")
    exit(1)

idx2 = content.find(end_marker, idx1) + len(end_marker)

new_hero_html = '''<section class="lw-hero-banner-section">
        <div class="container lw-hero-container">
          <div class="lw-hero-banner-card">
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
            
            <!-- Bottom Feature Ribbon -->
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

updated_content = content[:idx1] + new_hero_html + content[idx2:]

# Also bump css cache buster to v=20261112_7
updated_content = updated_content.replace('?v=20261112_5', '?v=20261112_7')
updated_content = updated_content.replace('?v=20261112_6', '?v=20261112_7')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Successfully replaced hero section in views.py and bumped cache buster to v=20261112_7")
