# Script to replace SVG icons with real FontAwesome icons in features ribbon

# 1. Update views.py
with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

start_marker = '<section class="features" aria-label="Our advantages">'
end_marker = '</section>'

idx1 = views_content.find(start_marker)
idx2 = views_content.find(end_marker, idx1) + len(end_marker)

real_icons_html = '''<section class="features" aria-label="Our advantages">
              <div class="feature">
                <i class="fa-solid fa-globe feature-real-icon"></i>
                <span>Worldwide Coverage</span>
              </div>
              <div class="feature">
                <i class="fa-solid fa-bolt feature-real-icon"></i>
                <span>Real-Time Tracking</span>
              </div>
              <div class="feature">
                <i class="fa-solid fa-shield-halved feature-real-icon"></i>
                <span>Trusted &amp; Secure</span>
              </div>
              <div class="feature">
                <i class="fa-solid fa-headset feature-real-icon"></i>
                <span>24/7 Support</span>
              </div>
            </section>'''

views_content = views_content[:idx1] + real_icons_html + views_content[idx2:]
views_content = views_content.replace('?v=20261112_13', '?v=20261112_14')

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)
print("views.py updated with real FontAwesome icons!")

# 2. Update styles.css
with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

css_replacement = """
.hero-shell .features {
  position: relative !important;
  z-index: 2 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
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
  gap: 12px !important;
  padding: 0 clamp(14px, 2.5vw, 36px) !important;
  color: #ffffff !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em !important;
  border-right: 1px solid rgba(255,255,255,.24) !important;
}

.hero-shell .feature:first-child {
  padding-left: 0 !important;
}

.hero-shell .feature:last-child {
  border-right: 0 !important;
  padding-right: 0 !important;
}

.feature-real-icon {
  font-size: 20px !important;
  color: #00c2ff !important;
  filter: drop-shadow(0 0 10px rgba(0, 194, 255, 0.8)) !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
}
"""

# Let's replace the .hero-shell .features block in styles.css
import re
css_content = re.sub(r'\.hero-shell \.features \{[^}]+\}\s*\.hero-shell \.feature \{[^}]+\}\s*\.hero-shell \.feature:first-child \{[^}]+\}\s*\.hero-shell \.feature:last-child \{[^}]+\}\s*\.hero-shell \.feature svg \{[^}]+\}',
                     css_replacement.strip(), css_content)

with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
    f.write(css_content)
print("styles.css updated with feature-real-icon styles!")
