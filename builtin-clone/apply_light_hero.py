import re

with open('views.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_hero = """<!-- 1. Enterprise Hero: Insights for Smarter Logistics (Light White Master Composition) -->
    <section class="lw-hero-banner-section">
      <div class="hero-shell-white">
        <div class="hero-content-col">
          <div class="hero-eyebrow-light">
            <span class="eyebrow-dot-blue"></span>
            GLOBAL LOGISTICS SOLUTION
          </div>
          
          <h1 class="hero-headline-light">
            Insights for<br>
            <span class="hero-hl-blue">Smarter</span> Logistics
          </h1>
          
          <p class="hero-subtitle-light">
            Real-time data, greater visibility, and smarter decisions for a more connected supply chain.
          </p>
          
          <div class="hero-actions-light">
            <a class="hero-btn-primary-light" href="/article-blogs">
              Explore Insights
            </a>
            <a class="hero-btn-secondary-light" href="#overview" onclick="openFwtModal(0); return false;" aria-label="Watch Overview Video">
              <span class="hero-yt-badge">
                <i class="fa-brands fa-youtube"></i>
              </span>
              <span>Watch Overview</span>
            </a>
          </div>

          <div class="hero-features-light">
            <div class="hero-feat-item"><i class="fa-solid fa-earth-americas"></i> Worldwide Coverage</div>
            <div class="hero-feat-item"><i class="fa-solid fa-bolt"></i> Real-Time Tracking</div>
            <div class="hero-feat-item"><i class="fa-solid fa-shield-halved"></i> Trusted &amp; Secure</div>
            <div class="hero-feat-item"><i class="fa-solid fa-headset"></i> 24/7 Support</div>
          </div>
        </div>

        <div class="hero-visual-col">
          <div class="hero-visual-card">
            <img src="/static/images/hero_transport_flawless.jpg" alt="Multimodal Global Logistics: Air, Sea, Overland" loading="eager">
          </div>
        </div>
      </div>
    </section>

    <!-- 2. Editorial Showcase"""

updated = re.sub(r'<!-- 1\. Enterprise Hero.*?<!-- 2\. Editorial Showcase', new_hero, text, flags=re.DOTALL)
updated = re.sub(r'/static/styles\.css\?v=[^"]+', '/static/styles.css?v=20261114_05', updated)

with open('views.py', 'w', encoding='utf-8') as f:
    f.write(updated)
print('views.py updated successfully!')
