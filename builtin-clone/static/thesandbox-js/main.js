/**
 * THE SANDBOX - VIETNAM LOGISTICS TALENT & CAREER PLATFORM
 */

// Prevent browser from auto-jumping to previous scroll position or lingering URL hash on refresh
if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}

// Clean any leftover URL hash on fresh load so the page doesn't automatically scroll down
if (window.location.hash) {
  try {
    history.replaceState(null, null, window.location.pathname + window.location.search);
  } catch (e) {}
  window.scrollTo(0, 0);
}

let currentLang = 'en';

document.addEventListener('DOMContentLoaded', () => {
  // Always ensure user starts at the top of the page on fresh load
  window.scrollTo(0, 0);

  // Smooth scroll internal anchor links without polluting URL hash or causing reload jumps
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;
    const href = link.getAttribute('href');
    if (href === '#' || href === '#!') return;
    const targetId = href.slice(1);
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      e.preventDefault();
      targetEl.scrollIntoView({ behavior: 'smooth' });
    }
  });

  initHeroCarousel();
  initVerticalNewsTabs();
  initBusinessWorkTabs();
  initFloatingToolbar();
  initSearch();
  initLanguageToggle();
  initYouTubeHub();
  initSplitScreenJobBoard();
  initSalaryCalculator();
  initJobApplyModal();
  initHeroSearchEngine();
  initScrollReveal();
  initScrollNavbar();
  initHeroParallax();
  initStatisticCounters();
  initGovDirectivesTabs();
  initEmployerSystem();
});

/* ==========================================================================
   1. HERO CAROUSEL CONTROLLER
   ========================================================================== */
function initHeroCarousel() {
  const slides = document.querySelectorAll('.hero-editorial-slide, .carousel-slide');
  const dots = document.querySelectorAll('.hero-dot, .dot-indicator');
  const prevBtn = document.querySelector('.hero-arrow-prev, .carousel-nav-prev');
  const nextBtn = document.querySelector('.hero-arrow-next, .carousel-nav-next');
  if (!slides.length) return;

  let currentIndex = 0;
  let timer = null;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
    currentIndex = index;
  }

  function nextSlide() {
    let next = (currentIndex + 1) % slides.length;
    showSlide(next);
  }

  function prevSlide() {
    let prev = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(prev);
  }

  function startAutoplay() {
    stopAutoplay();
    timer = setInterval(nextSlide, 5000);
  }

  function stopAutoplay() {
    if (timer) clearInterval(timer);
  }

  if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); startAutoplay(); });
  if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); startAutoplay(); });

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.getAttribute('data-index') || '0', 10);
      showSlide(idx);
      startAutoplay();
    });
  });

  const viewport = document.querySelector('.hero-editorial-viewport, .carousel-viewport');
  if (viewport) {
    viewport.addEventListener('mouseenter', stopAutoplay);
    viewport.addEventListener('mouseleave', startAutoplay);
  }

  startAutoplay();
}

/* ==========================================================================
   2. NEWS TABS CONTROLLER (FREIGHTWAVES STYLE)
   ========================================================================== */
const newsData = {
  en: {
    political: {
      leadTitle: 'President Meets with International Delegations in High-Level Summit',
      leadDesc: 'During bilateral conferences, state leaders highlighted mutual cooperation in international employment standards, youth vocational capacity building, and digital labor markets.',
      bullets: [
        { text: 'Vocational Capacity Building Dept: Accelerating Skilled Talent Cultivation for New Productive Forces', date: '09-24' },
        { text: 'Focusing on Priority Groups: Multi-Pronged Measures to Stabilize Employment & Strengthen Safety Nets', date: '09-24' },
        { text: 'Youth & College Graduate Employment Support Action Campaign Expands to Enterprise Hubs', date: '09-24' },
        { text: 'Standardized Construction of Gig & Flexible Labor Markets Yields Rapid Immediate Placement', date: '09-24' },
        { text: 'Employment Stabilization Policies Benefit Millions of Enterprise Workers and Tech Startups', date: '09-23' }
      ]
    },
    business: {
      leadTitle: 'Ministry Deploys 2026 Youth & College Graduate Employment Service Initiative',
      leadDesc: 'Centered on targeted job matching, policy orientation, and practical skill coaching for recent graduates across national industrial zones.',
      bullets: [
        { text: 'Public Employment Service Capacity Demonstration Projects Announced by Joint Committee', date: '09-23' },
        { text: 'Release of Phase 1 Work-Study Integration Outcomes in Technical Colleges and Engineering Schools', date: '09-22' },
        { text: 'Nationwide "100-Day 10-Million Recruitment" Campaign Launches 9.8M Direct Positions', date: '09-21' },
        { text: 'Cross-Provincial Labor Matching Programs Support Sustainable Rural Incomes and Skills', date: '09-20' },
        { text: 'Strengthening Supervision & Quality Assurance for National Vocational Skill Certificate Audits', date: '09-19' }
      ]
    },
    center: {
      leadTitle: 'MOLISA Upgrades National Digital Logistics Skilled Talent Evaluation System',
      leadDesc: 'Accelerating nationwide qualification interoperability and real-time certificate inquiry systems to support millions of certified supply chain technicians.',
      bullets: [
        { text: 'Coordination Meeting on 2026 National Occupational Standards Revision & Digital Classification', date: '09-23' },
        { text: 'High-Level Public Training Bases Facilitate Equal Skill Resource Access Across Industrial Zones', date: '09-22' },
        { text: 'WorldSkills Vietnam Delegation Preparation and Technical Advisory Conference Concludes in Hanoi', date: '09-21' },
        { text: 'Vietnam Entrepreneurship Training (SYB/GYB) Master Instructor Certification Course Opens', date: '09-20' },
        { text: 'Logistics Brand Modernization & Digital Branding Workshops Open Across Key Industrial Hubs', date: '09-18' }
      ]
    }
  },
  zh: {
    political: {
      leadTitle: 'State Leadership Holds Bilateral Summit on Regional Logistics Connectivity',
      leadDesc: 'Bilateral leaders meet during regional economic summit, emphasizing mutual development, freight facilitation, and cross-border logistics infrastructure.',
      bullets: [
        { text: 'Vocational Competency Dept: Accelerating High-Skilled Talent Cultivation for New Supply Chain Forces', date: '09-24' },
        { text: 'Comprehensive Support Implemented for Priority Demographics to Strengthen Employment Safety Net', date: '09-24' },
        { text: 'Youth & Graduate Career Bridge Campaign Deployed with Precision Job Matching Algorithms', date: '09-24' },
        { text: 'Standardized Gig & On-Demand Labor Market Construction Expands Real-Time Hiring Services', date: '09-24' },
        { text: 'Employment Stabilization & Wage Growth Directives Deliver Tangible Relief to Private Logistics Firms', date: '09-23' }
      ]
    },
    business: {
      leadTitle: 'Ministry of Labour - Invalids & Social Affairs Deploys 2026 Logistics Employment Campaign',
      leadDesc: 'Focusing on career navigation, policy briefings, job placement recommendations, and vocational skill upgrades for young logistics professionals.',
      bullets: [
        { text: 'Evaluation Results Announced for National Public Employment Demonstration Projects', date: '09-23' },
        { text: 'Work-Study Integrated Curriculum Milestone Released for National Technical Academies', date: '09-22' },
        { text: 'MOLISA Launches National Logistics 100-Day Hiring Campaign Across Key Economic Zones', date: '09-21' },
        { text: 'Cross-Regional Labor Cooperation Expanded to Sustain Long-Term High-Wage Retention', date: '09-20' },
        { text: 'Supervision Tightened for Vocational Credential Evaluation Bodies to Ensure Credibility', date: '09-19' }
      ]
    },
    center: {
      leadTitle: 'National Guidance Center Advances Digital Skill Assessment & Unified Interoperability Platform',
      leadDesc: 'Building a high-standard skill evaluation architecture, linking state occupational credential databases across provinces with automated cross-validation.',
      bullets: [
        { text: 'National Occupational Standards Coordination and Revision Conference Convened', date: '09-23' },
        { text: 'High-Level Public Training Hubs Accelerate Equitable Resource Distribution', date: '09-22' },
        { text: 'WorldSkills Delegation Technical Guarantee and Logistics Advisory Conference Concludes', date: '09-21' },
        { text: 'National Master Instructor Certification Workshop Inaugurated for Emerging Sectors', date: '09-20' },
        { text: 'Logistics Brand Identity & Digital Empowerment Workshops Expanded Across Provinces', date: '09-18' }
      ]
    }
  }
};

let currentNewsTab = 'political';

function initVerticalNewsTabs() {
  const tabBtns = document.querySelectorAll('.fw-tab-btn[data-tab], .vertical-tab-btn');
  const leadTitleEl = document.getElementById('news-lead-title');
  const leadDescEl = document.getElementById('news-lead-desc');
  const bulletsContainer = document.getElementById('news-bullets-list');
  if (!tabBtns.length || !leadTitleEl || !bulletsContainer) return;

  function updateNewsView() {
    const langSet = newsData[currentLang] || newsData['en'];
    const data = langSet[currentNewsTab];
    if (!data) return;

    leadTitleEl.innerHTML = `<a href="#">${data.leadTitle}</a>`;
    leadDescEl.textContent = data.leadDesc;

    bulletsContainer.innerHTML = data.bullets.map(item => `
      <div class="fw-news-item">
        <a href="#" class="fw-news-title">${item.text}</a>
        <span class="fw-news-timestamp">${item.date}</span>
      </div>
    `).join('');
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      currentNewsTab = btn.getAttribute('data-tab') || 'political';
      updateNewsView();
    });
  });

  window.refreshNewsTabs = updateNewsView;
}

/* ==========================================================================
   3. BUSINESS WORK TABS
   ========================================================================== */
const bizNewsData = {
  en: {
    general: [
      { text: 'Hai Phong Port Authority: Precision Measures Driving High-Efficiency Logistics Employment', date: '09-24' },
      { text: 'Da Nang Hi-Tech Park: Three Major Initiatives Assisting Supply Chain Graduate Career Placement', date: '09-24' },
      { text: 'Bac Ninh Industrial Zone: Reinforcing Youth Technical Apprenticeship & Warehouse Hubs', date: '09-24' },
      { text: 'Mekong Delta Hub (Can Tho): Agri-Logistics Specialists Becoming Modern Cold-Chain Leaders', date: '09-24' },
      { text: 'Binh Duong VSIP: Attracting Multinational Manufacturing Investments & Supply Chain Talents', date: '09-24' },
      { text: 'Dong Nai Long Thanh: Strengthening Social Security Safety Nets for Port & Airport Workers', date: '09-24' },
      { text: 'Quang Ninh Deep Water Port: Optimizing Maritime Innovation Ecosystem to Boost Job Growth', date: '09-24' },
      { text: 'VLA Association: Active Implementation of Vietnam Logistics Talent Strategy Yields Gains', date: '09-23' }
    ],
    startup: [
      { text: 'Hanoi Hoa Lac: Fast-Track Preferential Capital for Logistics Tech & Drone Delivery Startups', date: '09-24' },
      { text: 'Ho Chi Minh City: Annual Youth Logistics Innovation Challenge Selects Top 50 Incubator Hubs', date: '09-23' },
      { text: 'Da Nang Innovation Hub: Rent-Free Co-Working Spaces Established for Maritime Freight Creators', date: '09-22' },
      { text: 'Binh Duong Tech Campus: Supply Chain Mentors Tour Universities for Automation Spin-offs', date: '09-21' },
      { text: 'Hanoi Capital Fund: Over ₫50 Billion Allocated in Direct Graduate Tech Startup Subsidies', date: '09-20' },
      { text: 'Hai Phong Maritime Cluster: Youth Incubator Welcomes AI Routing and Green Port Teams', date: '09-19' },
      { text: 'Can Tho Hub: Smart Cold Chain Incubator Matches Angel Capital with Mekong Patents', date: '09-18' },
      { text: 'Ba Ria - Vung Tau: Port Logistics Innovation Lab Accelerates Container Automation', date: '09-17' }
    ],
    policy: [
      { text: 'Prime Minister Decision on Promoting High-Quality Logistics Employment 2026-2030 (Full Text)', date: '09-24' },
      { text: 'MOLISA Directive on Enhancing Employment & Entrepreneurship Support for 2026 Logistics Graduates', date: '09-23' },
      { text: 'Implementation Guidelines for Expanding Targeted Training Subsidies to Transport Enterprises', date: '09-22' },
      { text: 'National Guiding Standards on Modern Logistics Park Labor Welfare & Safety Certification', date: '09-21' },
      { text: 'National Catalogue of Subsidized Supply Chain Professional Qualifications and Settlement Rules', date: '09-20' },
      { text: 'Management Regulations on National Online Verification of Logistics Skill Certificates (2026)', date: '09-19' },
      { text: 'Unemployment Insurance Premium Refund Implementation Guide for Compliant Fleet Employers', date: '09-18' },
      { text: 'Strategic Measures on Enhancing Port & Airport Labor Initiatives Across Economic Corridors', date: '09-17' }
    ],
    trend: [
      { text: 'General Statistics Office: August National Transportation Labor Employment Index Rises 4.2%', date: '09-24' },
      { text: 'Q3 Recruitment Index: Port Automation & Cold Chain Engineer Demand Surges 42%', date: '09-23' },
      { text: 'Vietnam Logistics Talent Report (VALOMA): High-End Cross-Border E-Commerce Drives Hiring', date: '09-22' },
      { text: 'Logistics Graduate Career Survey: Preference for Green Freight & Automated Warehousing Rises', date: '09-21' },
      { text: 'Northern & Southern Economic Corridors Absorb Global Manufacturing Relocation Demand', date: '09-20' },
      { text: 'Digital Economy Last-Mile Delivery Platforms Demonstrate Strong Technical Absorption', date: '09-19' },
      { text: 'Customs Specialist Supply-Demand Analysis: Certified AEO Compliance Managers in High Demand', date: '09-18' },
      { text: 'Green Logistics & ESG Compliance Sectors Expand New High-Salary Professional Career Paths', date: '09-17' }
    ],
    social: [
      { text: 'Occupational Welfare & Injury Protection Coverage Expands to 500,000 Truck & Port Workers', date: '09-24' },
      { text: 'Inter-Provincial Healthcare Portability for Transport Drivers Implemented Seamlessly', date: '09-23' },
      { text: 'VNeID & Social Security Integration: One-Tap Digital Identification for Logistics Applicants', date: '09-22' },
      { text: 'Port Truckers & Freight Forwarders Statutory Insurance Coverage Rate Reaches 98%', date: '09-21' },
      { text: 'National Pension & Severance Guarantee Fund Enforced for Maritime & Fleet Operators', date: '09-20' },
      { text: 'Labor Safety Inspection: Safeguarding Occupational Health at Cai Mep & Lach Huyen Ports', date: '09-19' },
      { text: 'Public Employment Service Center Achieves Seamless Cross-Province Job Transfer in 24h', date: '09-18' },
      { text: 'Dynamic Vocational Re-skilling & Fair Placement Support for Displaced Industrial Workers', date: '09-17' }
    ]
  },
  zh: {
    general: [
      { text: 'Hai Phong Port Authority: Precision Measures Driving High-Efficiency Logistics Employment', date: '09-24' },
      { text: 'Da Nang Hi-Tech Park: Three Major Initiatives Assisting Supply Chain Graduate Career Placement', date: '09-24' },
      { text: 'Bac Ninh Industrial Zone: Reinforcing Youth Technical Apprenticeship & Warehouse Hubs', date: '09-24' },
      { text: 'Mekong Delta Hub (Can Tho): Agri-Logistics Specialists Becoming Modern Cold-Chain Leaders', date: '09-24' },
      { text: 'Binh Duong VSIP: Attracting Multinational Manufacturing Investments & Supply Chain Talents', date: '09-24' },
      { text: 'Dong Nai Long Thanh: Strengthening Social Security Safety Nets for Port & Airport Workers', date: '09-24' },
      { text: 'Quang Ninh Deep Water Port: Optimizing Maritime Innovation Ecosystem to Boost Job Growth', date: '09-24' },
      { text: 'VLA Association: Active Implementation of Vietnam Logistics Talent Strategy Yields Gains', date: '09-23' }
    ],
    startup: [
      { text: 'Hanoi Hoa Lac: Fast-Track Preferential Capital for Logistics Tech & Drone Delivery Startups', date: '09-24' },
      { text: 'Ho Chi Minh City: Annual Youth Logistics Innovation Challenge Selects Top 50 Incubator Hubs', date: '09-23' },
      { text: 'Da Nang Innovation Hub: Rent-Free Co-Working Spaces Established for Maritime Freight Creators', date: '09-22' },
      { text: 'Binh Duong Tech Campus: Supply Chain Mentors Tour Universities for Automation Spin-offs', date: '09-21' },
      { text: 'Hanoi Capital Fund: Over ₫50 Billion Allocated in Direct Graduate Tech Startup Subsidies', date: '09-20' },
      { text: 'Hai Phong Maritime Cluster: Youth Incubator Welcomes AI Routing and Green Port Teams', date: '09-19' },
      { text: 'Can Tho Hub: Smart Cold Chain Incubator Matches Angel Capital with Mekong Patents', date: '09-18' },
      { text: 'Ba Ria - Vung Tau: Port Logistics Innovation Lab Accelerates Container Automation', date: '09-17' }
    ],
    policy: [
      { text: 'Prime Minister Decision on Promoting High-Quality Logistics Employment 2026-2030 (Full Text)', date: '09-24' },
      { text: 'MOLISA Directive on Enhancing Employment & Entrepreneurship Support for 2026 Logistics Graduates', date: '09-23' },
      { text: 'Implementation Guidelines for Expanding Targeted Training Subsidies to Transport Enterprises', date: '09-22' },
      { text: 'National Guiding Standards on Modern Logistics Park Labor Welfare & Safety Certification', date: '09-21' },
      { text: 'National Catalogue of Subsidized Supply Chain Professional Qualifications and Settlement Rules', date: '09-20' },
      { text: 'Management Regulations on National Online Verification of Logistics Skill Certificates (2026)', date: '09-19' },
      { text: 'Unemployment Insurance Premium Refund Implementation Guide for Compliant Fleet Employers', date: '09-18' },
      { text: 'Strategic Measures on Enhancing Port & Airport Labor Initiatives Across Economic Corridors', date: '09-17' }
    ],
    trend: [
      { text: 'General Statistics Office: August National Transportation Labor Employment Index Rises 4.2%', date: '09-24' },
      { text: 'Q3 Recruitment Index: Port Automation & Cold Chain Engineer Demand Surges 42%', date: '09-23' },
      { text: 'Vietnam Logistics Talent Report (VALOMA): High-End Cross-Border E-Commerce Drives Hiring', date: '09-22' },
      { text: 'Logistics Graduate Career Survey: Preference for Green Freight & Automated Warehousing Rises', date: '09-21' },
      { text: 'Northern & Southern Economic Corridors Absorb Global Manufacturing Relocation Demand', date: '09-20' },
      { text: 'Digital Economy Last-Mile Delivery Platforms Demonstrate Strong Technical Absorption', date: '09-19' },
      { text: 'Customs Specialist Supply-Demand Analysis: Certified AEO Compliance Managers in High Demand', date: '09-18' },
      { text: 'Green Logistics & ESG Compliance Sectors Expand New High-Salary Professional Career Paths', date: '09-17' }
    ],
    social: [
      { text: 'Occupational Welfare & Injury Protection Coverage Expands to 500,000 Truck & Port Workers', date: '09-24' },
      { text: 'Inter-Provincial Healthcare Portability for Transport Drivers Implemented Seamlessly', date: '09-23' },
      { text: 'VNeID & Social Security Integration: One-Tap Digital Identification for Logistics Applicants', date: '09-22' },
      { text: 'Port Truckers & Freight Forwarders Statutory Insurance Coverage Rate Reaches 98%', date: '09-21' },
      { text: 'National Pension & Severance Guarantee Fund Enforced for Maritime & Fleet Operators', date: '09-20' },
      { text: 'Labor Safety Inspection: Safeguarding Occupational Health at Cai Mep & Lach Huyen Ports', date: '09-19' },
      { text: 'Public Employment Service Center Achieves Seamless Cross-Province Job Transfer in 24h', date: '09-18' },
      { text: 'Dynamic Vocational Re-skilling & Fair Placement Support for Displaced Industrial Workers', date: '09-17' }
    ]
  }
};

let currentBizTab = 'general';

function initBusinessWorkTabs() {
  const tabBtns = document.querySelectorAll('.fw-tab-btn[data-biz-tab], .biz-tab-btn');
  const container = document.getElementById('business-news-container');
  if (!tabBtns.length || !container) return;

  function updateBizView() {
    const langSet = bizNewsData[currentLang] || bizNewsData['en'];
    const list = langSet[currentBizTab] || [];

    container.innerHTML = list.map(item => `
      <div class="fw-news-item">
        <a href="#" class="fw-news-title">${item.text}</a>
        <span class="fw-news-timestamp">${item.date}</span>
      </div>
    `).join('');
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      currentBizTab = btn.getAttribute('data-biz-tab') || 'general';
      updateBizView();
    });
  });

  window.refreshBizTabs = updateBizView;
}

/* ==========================================================================
   4. FLOATING TOOLBAR
   ========================================================================== */
function initFloatingToolbar() {
  const backToTopBtn = document.getElementById('toolbar-back-top');
  if (backToTopBtn) {
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  const surveyBtn = document.getElementById('toolbar-survey');
  if (surveyBtn) {
    surveyBtn.addEventListener('click', () => {
      alert('【National Employment Market Survey】\nThank you for participating in the 2026 Labor & Employment Research Survey.');
    });
  }

  const feedbackBtn = document.getElementById('toolbar-feedback');
  if (feedbackBtn) {
    feedbackBtn.addEventListener('click', () => {
      const msg = prompt('【Editorial Feedback】\nPlease submit your comments or inquiries to the Editorial Desk:');
      if (msg) {
        alert('Thank you! Your feedback has been transmitted to the editorial operations team.');
      }
    });
  }

  const contactBtn = document.getElementById('toolbar-contact');
  if (contactBtn) {
    contactBtn.addEventListener('click', () => {
      alert('【Support & Editorial Desk】\nHotline: (+84) 24 3826 9988 (Weekdays 08:30-17:30)\nEmail: contact@thesandbox.vn\nAddress: 12 Kim Ma, Ba Dinh District, Hanoi, Vietnam');
    });
  }
}

/* ==========================================================================
   5. HEADER SEARCH
   ========================================================================== */
function initSearch() {
  const form = document.getElementById('header-search-form');
  const input = document.getElementById('header-search-input');
  if (!form || !input) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) {
      alert('Please enter a search query for labor intelligence, standards, or policies.');
      return;
    }
    alert(`【Intelligence Search】\nQuery: "${query}"\nFound 142 matching official records.`);
  });
}

/* ==========================================================================
   6. LANGUAGE / REGION TOGGLE (MODERN ENTERPRISE DROPDOWN)
   ========================================================================== */
function initLanguageToggle() {
  const wrap = document.getElementById('lang-dropdown-wrap');
  const btn = document.getElementById('lang-dropdown-btn');
  const currentLabel = document.getElementById('lang-current-label');
  const menuItems = document.querySelectorAll('.lang-menu-item');
  const legacyBtns = document.querySelectorAll('.lang-btn, #lang-toggle-btn');

  // Handle Dropdown Toggle
  if (wrap && btn) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = wrap.classList.toggle('open');
      btn.setAttribute('aria-expanded', isOpen);
    });

    // Option items
    menuItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        menuItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        const lang = item.getAttribute('data-lang') || 'en';
        currentLang = lang;

        if (currentLabel) {
          currentLabel.textContent = lang === 'vn' ? 'Tiếng Việt' : 'English';
        }

        wrap.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');

        if (window.refreshNewsTabs) window.refreshNewsTabs();
        if (window.refreshBizTabs) window.refreshBizTabs();

        showToast(lang === 'vn' ? 'Giao diện: Tiếng Việt (Vietnam)' : 'Language set to: English (Global)');
      });
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
      if (!wrap.contains(e.target)) {
        wrap.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && wrap.classList.contains('open')) {
        wrap.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  // Backward compatibility with any legacy lang buttons
  if (legacyBtns.length) {
    legacyBtns.forEach(b => {
      b.addEventListener('click', () => {
        const lang = b.getAttribute('data-lang') || 'en';
        currentLang = lang;
        if (currentLabel) {
          currentLabel.textContent = lang === 'vn' ? 'Tiếng Việt' : 'English';
        }
        showToast(`Language switched to: ${lang.toUpperCase()}`);
      });
    });
  }
}

/* ==========================================================================
   7. MARKET INTELLIGENCE · YOUTUBE VIDEO BROADCAST HUB CONTROLLER
   ========================================================================== */
function initYouTubeHub() {
  const iframe = document.getElementById('main-yt-iframe');
  const titleEl = document.getElementById('main-yt-title');
  const categoryEl = document.getElementById('main-yt-category');
  const dateEl = document.getElementById('main-yt-date');
  const durationEl = document.getElementById('main-yt-duration');
  const excerptEl = document.getElementById('main-yt-excerpt');
  const linkEl = document.getElementById('main-yt-external-link');
  const playlistItems = document.querySelectorAll('.fw-yt-item');
  if (!iframe || !playlistItems.length) return;

  playlistItems.forEach(item => {
    item.addEventListener('click', () => {
      playlistItems.forEach(i => {
        i.classList.remove('active');
        const tag = i.querySelector('.fw-yt-item-tag');
        if (tag && tag.textContent === 'Now Playing') {
          tag.textContent = i.dataset.category || 'Broadcast';
        }
      });

      item.classList.add('active');
      const curTag = item.querySelector('.fw-yt-item-tag');
      if (curTag) curTag.textContent = 'Now Playing';

      const ytId = item.dataset.ytId;
      const title = item.dataset.title;
      const category = item.dataset.category;
      const date = item.dataset.date;
      const duration = item.dataset.duration;
      const excerpt = item.dataset.excerpt;

      if (ytId) {
        iframe.src = `https://www.youtube-nocookie.com/embed/${ytId}?autoplay=1&rel=0&enablejsapi=1`;
      }
      if (titleEl) titleEl.textContent = title;
      if (categoryEl) categoryEl.textContent = category;
      if (dateEl) dateEl.textContent = date;
      if (durationEl) durationEl.innerHTML = `<i class="fa-regular fa-clock"></i> ${duration}`;
      if (excerptEl) excerptEl.textContent = excerpt;
      if (linkEl && ytId) linkEl.href = `https://www.youtube.com/watch?v=${ytId}`;

      if (typeof showToast === 'function') {
        showToast(`Now playing: ${title}`);
      }
    });
  });
}

/* ==========================================================================
   8. SPLIT-SCREEN JOB BOARD DATA & CONTROLLER (CORE RETENTION ENGINE)
   ========================================================================== */
const jobsDatabase = [
  {
    id: 'job-verified-1793071901986',
    title: 'Senior Multimodal Freight Operations Lead',
    company: 'DHL Global Forwarding Vietnam',
    applyMethod: 'direct',
    applyEmail: 'dhl.customs.vn@dhl.com',
    companyLogo: 'images/brands/dhl.svg',
    companyIcon: 'fa-stamp',
    salary: '32M-48M VND Annually',
    salaryVal: 40000000,
    location: 'Hanoi & Hai Phong, VN',
    workplace: 'Hybrid',
    seniority: 'Lead',
    category: 'forwarding',
    tags: ['Verified Listing', 'Accredited Partner', 'Multimodal', 'Air & Ocean'],
    isUrgent: true,
    isHighSalary: true,
    time: 'Just Now',
    accentClass: '',
    specs: { exp: 'Lead', edu: 'BA Foreign Trade / Logistics', dept: 'Cross-Border Supply Chain Solutions', openings: '1 Position' },
    overview: 'Lead multimodal freight operations coordinating high-velocity international cargo across North Vietnam gateways, including Cai Lan, Hai Phong, and Noi Bai air cargo hub.',
    responsibilities: [
      'Manage end-to-end multimodal logistics solutions integrating ocean, air, and cross-border trucking.',
      'Supervise customs compliance and digital EDI trade declarations under Decree 163/2017/ND-CP.',
      'Drive service excellence and carrier SLA adherence for key multinational enterprise accounts.'
    ]
  },
  {
    id: 'job-1',
    title: 'Senior Ocean Freight Forwarder',
    company: 'Viconship Logistics Group',
    applyMethod: 'direct',
    applyEmail: 'recruitment@viconship.com',
    companyLogo: 'images/brands/viconship.svg',
    companyIcon: 'fa-ship',
    salary: '28M-42M VND Annually',
    salaryVal: 35000000,
    location: 'Ho Chi Minh City, VN',
    workplace: 'Hybrid',
    seniority: 'Senior level',
    category: 'forwarding',
    tags: ['Verified Employer', 'Full-time', 'Hybrid', 'Ocean Freight'],
    isUrgent: false,
    isHighSalary: true,
    time: '2 Hours Ago',
    accentClass: '',
    specs: { exp: 'Senior level', edu: 'Bachelor Degree', dept: 'Asia-Europe Ocean Corridor', openings: '2 Positions' },
    overview: 'Viconship is seeking a seasoned Ocean Freight Forwarding Specialist to manage end-to-end container booking, multimodal carrier negotiations, and freight optimization for multinational manufacturing accounts in Southern Vietnam.',
    responsibilities: [
      'Coordinate ocean freight routing, rate negotiations, and space allocation with major maritime alliances (2M, Ocean Alliance, THE Alliance).',
      'Manage complex customs clearance, FMC bill-of-lading (B/L) documentation, and cross-border demurrage/detention minimization.',
      'Act as direct strategic escalation lead for Tier-1 automotive and electronics enterprise shippers.'
    ]
  },
  {
    id: 'job-2',
    title: 'AMR Robotics & Automation Systems Specialist',
    company: 'Tiki Logistics Automated Mega Hub',
    applyMethod: 'external',
    applyUrl: 'https://careers.tiki.vn/job/robotics-automation-specialist',
    companyLogo: 'images/brands/tiki.svg',
    companyIcon: 'fa-robot',
    salary: '32M-48M VND Annually',
    salaryVal: 40000000,
    location: 'Binh Duong, VN',
    workplace: 'On-site',
    seniority: 'Lead',
    category: 'robotics',
    tags: ['Urgent Hiring', 'Full-time', 'On-site', 'Warehouse Tech'],
    isUrgent: true,
    isHighSalary: true,
    time: '3 Hours Ago',
    accentClass: 'accent-green',
    specs: { exp: 'Lead', edu: 'BS in Mechatronics/CS', dept: 'Automated Operations Group', openings: '4 Positions' },
    overview: 'Lead the continuous deployment, route calibration, and preventative maintenance for a fleet of 450+ autonomous mobile robots (AMRs) and automated storage/retrieval systems (AS/RS).',
    responsibilities: [
      'Supervise real-time fleet management software (FMS) and automated material handling dispatch.',
      'Conduct robotic sensor diagnostics (LiDAR, SLAM navigation, optical QR readers) to maintain 99.8% fleet uptime.'
    ]
  },
  {
    id: 'job-3',
    title: 'Supply Chain Solutions Architect (Cold Chain)',
    company: 'VinFast Logistics & Cold Chain Solutions',
    applyMethod: 'direct',
    applyEmail: 'careers.logistics@vinfast.vn',
    companyLogo: 'images/brands/vinfast.svg',
    companyIcon: 'fa-snowflake',
    salary: '35M-55M VND Annually',
    salaryVal: 45000000,
    location: 'Ho Chi Minh City, VN',
    workplace: 'Hybrid',
    seniority: 'Senior level',
    category: 'tech',
    tags: ['Top Tier Enterprise', 'Cold Chain', 'High Salary', 'Strategy'],
    isUrgent: false,
    isHighSalary: true,
    time: '4 Hours Ago',
    accentClass: 'accent-coral',
    specs: { exp: 'Senior level', edu: 'Master / Engineering', dept: 'Strategic Network Optimization', openings: '1 Position' },
    overview: 'Architect next-generation cold-chain distribution models for automotive battery supply chains, perishables, and pharma shipments across ASEAN corridors.',
    responsibilities: [
      'Design end-to-end multi-temperature refrigerated warehousing and cross-docking logistics networks.',
      'Implement real-time IoT temperature/humidity tracking telematics across linehaul reefer fleets.'
    ]
  },
  {
    id: 'job-4',
    title: 'International Customs Clearance & Compliance Manager',
    company: 'DHL Global Forwarding Vietnam',
    applyMethod: 'direct',
    applyEmail: 'dhl.customs.vn@dhl.com',
    companyLogo: 'images/brands/dhl.svg',
    companyIcon: 'fa-stamp',
    salary: '26M-38M VND Annually',
    salaryVal: 32000000,
    location: 'Hanoi, VN',
    workplace: 'On-site',
    seniority: 'Manager',
    category: 'forwarding',
    tags: ['Multinational', 'Customs Brokerage', 'Compliance', 'Noi Bai'],
    isUrgent: true,
    isHighSalary: false,
    time: '5 Hours Ago',
    accentClass: 'accent-blue',
    specs: { exp: 'Manager', edu: 'BA Foreign Trade / Customs', dept: 'Customs & Trade Governance', openings: '1 Position' },
    overview: 'Direct customs compliance, HS tariff classifications, and automated VNACCS/VCIS EDI transmissions for enterprise cargo moving through Northern Vietnam.',
    responsibilities: [
      'Ensure zero regulatory non-compliance across 15,000+ annual sea/air declarations.',
      'Act as chief liaison with General Department of Vietnam Customs on duty exemptions and origin certificates.'
    ]
  },
  {
    id: 'job-5',
    title: 'Container Terminal Dispatch Coordinator (Shift)',
    company: 'Saigon Newport Corporation (TCIT)',
    applyMethod: 'direct',
    applyEmail: 'hr@saigonnewport.com.vn',
    companyLogo: 'images/brands/saigon-newport.svg',
    companyIcon: 'fa-anchor',
    salary: '22M-35M VND Annually',
    salaryVal: 28000000,
    location: 'Ba Ria - Vung Tau, VN',
    workplace: 'On-site',
    seniority: 'Specialist',
    category: 'port',
    tags: ['Deep Sea Port', 'Maritime', 'Terminal Ops', 'Shift Work'],
    isUrgent: false,
    isHighSalary: false,
    time: '6 Hours Ago',
    accentClass: 'accent-blue',
    specs: { exp: 'Specialist', edu: 'Maritime University / Logistics', dept: 'Terminal Operating Systems (TOS)', openings: '3 Positions' },
    overview: 'Manage quayside ship-to-shore gantry cranes and container yard straddle carrier dispatch using Navis N4 Terminal Operating Systems at Cai Mep deep-water port.',
    responsibilities: [
      'Coordinate container vessel stowage planning and crane split sequences for ultra-large container vessels (ULCVs).',
      'Optimize yard turn times for drayage tractor-trailers to under 28 minutes per gate cycle.'
    ]
  },
  {
    id: 'job-6',
    title: 'Fleet Telematics & Route Optimization Data Analyst',
    company: 'Logivan Vietnam Freight Network',
    applyMethod: 'direct',
    applyEmail: 'talent@logivan.com',
    companyLogo: 'images/brands/logivan.svg',
    companyIcon: 'fa-chart-network',
    salary: '30M-48M VND Annually',
    salaryVal: 38000000,
    location: 'Da Nang, VN',
    workplace: 'Remote',
    seniority: 'Senior level',
    category: 'tech',
    tags: ['FreightTech', 'Data Science', 'Python', 'Remote Friendly'],
    isUrgent: false,
    isHighSalary: true,
    time: 'Yesterday',
    accentClass: 'accent-green',
    specs: { exp: 'Senior level', edu: 'BS Data Analytics / Operations Research', dept: 'Algorithmic Dispatch Group', openings: '2 Positions' },
    overview: 'Leverage telematics telemetry from 40,000+ registered trucks to train dynamic routing algorithms, reduce empty backhauls, and cut carbon emissions.',
    responsibilities: [
      'Build predictive freight rate models using machine learning on historical shipper spot transaction data.',
      'Design geospatial route optimization models in Python to cut deadhead mileage by 18% across North-South corridors.'
    ]
  }
];

let currentJobFilter = 'all';
let selectedJobId = 'job-1';

// Preserve baseline seeded jobs for dynamic synchronization
const SEEDED_BASELINE_JOBS = Array.isArray(jobsDatabase) ? [...jobsDatabase] : [];

// Seed & synchronize employer jobs from localStorage
function syncStoredEmployerJobs() {
  try {
    // Reset to seeded baseline so state updates (active -> paused/rejected) are immediately reflected
    if (SEEDED_BASELINE_JOBS.length > 0) {
      jobsDatabase.length = 0;
      jobsDatabase.push(...SEEDED_BASELINE_JOBS);
    }

    const raw = localStorage.getItem('thesandbox_employer_jobs');
    if (raw) {
      const stored = JSON.parse(raw);
      if (Array.isArray(stored)) {
        stored.forEach(job => {
          // Security: Only display active verified jobs on public job board.
          // Jobs with status 'pending_verification', 'pending_review', 'draft', 'rejected', 'paused', 'withdrawn', or 'returned_for_edit' are strictly excluded from public display.
          const isEligible = job.status === 'active' || (!job.status && job.status !== 'pending_verification' && job.status !== 'rejected');
          const isHiddenStatus = job.status === 'pending_verification' || 
                                 job.status === 'pending_review' || 
                                 job.status === 'draft' || 
                                 job.status === 'paused' || 
                                 job.status === 'rejected' || 
                                 job.status === 'withdrawn' || 
                                 job.status === 'returned_for_edit';

          if (isEligible && !isHiddenStatus && job.status !== 'pending_verification' && job.status !== 'paused' && job.status !== 'rejected') {
            if (!jobsDatabase.some(j => j.id === job.id)) {
              const enrichedJob = {
                ...job,
                isVerified: true,
                badgeVerified: '<i class="fa-solid fa-circle-check badge-verified" style="color:#16A34A;" title="Verified Employer"></i>'
              };
              jobsDatabase.unshift(enrichedJob);
            }
          }
        });
      }
    }
  } catch (err) {
    console.warn('Could not sync stored employer jobs:', err);
  }
}
window.syncStoredEmployerJobs = syncStoredEmployerJobs;

function initSplitScreenJobBoard() {
  const container = document.getElementById('jobs-list-container');
  const detailPanel = document.getElementById('job-detail-panel');
  const countBadge = document.getElementById('job-filter-count');
  const searchInput = document.getElementById('jobs-search-input') || document.getElementById('builtin-job-search-input');
  const chipBtns = document.querySelectorAll('.job-chip-btn');
  const isSplitLayout = !!document.querySelector('.split-job-layout');
  if (!container) return;

  let activeKeywordFilter = '';
  let activeLocationFilter = 'all';
  let selectedJobId = jobsDatabase[0] ? jobsDatabase[0].id : null;

  syncStoredEmployerJobs();

  function selectJob(id) {
    if (!detailPanel || !isSplitLayout) return;
    selectedJobId = id;
    const job = jobsDatabase.find(j => j.id === id) || jobsDatabase[0];
    if (!job) return;

    // Highlight active card
    container.querySelectorAll('.job-card').forEach(card => {
      card.classList.toggle('active', card.getAttribute('data-job-id') === id);
    });

    const applicantsCount = Math.floor(18 + (job.id.charCodeAt(job.id.length - 1) % 35));

    let logoHtml = '';
    if (job.companyLogo) {
      logoHtml = `<div class="brand-logo-pill" style="min-width:100px; max-width:140px; height:54px; border-radius:10px; background:#FFFFFF; border:1px solid #E2E8F0; box-shadow:0 1px 4px rgba(0,0,0,0.06); display:flex; align-items:center; justify-content:center; overflow:hidden; flex-shrink:0; padding:6px 12px;">
        <img src="${job.companyLogo}" alt="${job.company}" style="max-width:100%; max-height:42px; object-fit:contain; display:block;">
      </div>`;
    } else {
      logoHtml = `<div class="brand-logo-pill" style="min-width:65px; height:54px; border-radius:10px; font-weight:700; color:#1877F2; background:#E7F3FF; font-size:18px; border:1px solid #BFDBFE; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        ${job.company.slice(0, 2).toUpperCase()}
      </div>`;
    }

    const workplace = job.workplace || 
      (job.location && job.location.toLowerCase().includes('remote') ? 'Remote' :
       job.location && job.location.toLowerCase().includes('hybrid') ? 'Hybrid' : 'On-site');
    const cleanLoc = job.cleanLocation || (job.location ? job.location.split('·')[0].trim() : 'Ho Chi Minh City, VN');
    const salaryText = job.salary || '₫35,000,000 - ₫50,000,000 / mo';
    const expLevel = job.seniority || (job.specs && job.specs.exp ? job.specs.exp : 'Senior Specialist (3-5 yrs)');
    const dept = (job.specs && job.specs.dept) ? job.specs.dept : (job.category ? job.category.toUpperCase() + ' Division' : 'Logistics & Supply Chain');
    const savedIds = JSON.parse((localStorage.getItem('thesandbox_saved_jobs') || localStorage.getItem('sandbox_saved_jobs')) || '[]');
    const isSaved = savedIds.includes(job.id);

    const responsibilities = (job.responsibilities && job.responsibilities.length > 0)
      ? job.responsibilities
      : [
          'Lead end-to-end multi-modal forwarding operations, carrier negotiations, and priority account fulfillment.',
          'Coordinate vessel bookings, container allocations, and customs EDI clearance under Decree 163 and international maritime rules.',
          'Optimize multimodal routing performance and cross-border demurrage/detention minimization across Vietnam ports.',
          'Supervise strategic escalation and customer communication with enterprise manufacturers and freight alliance partners.'
        ];

    const requirements = (job.requirements && job.requirements.length > 0)
      ? job.requirements
      : [
          `Demonstrated 3+ years experience in ${job.category || 'logistics & freight forwarding'} operations or multinational 3PL environment.`,
          'In-depth knowledge of FMC / FIATA documentation, bill of lading (B/L) procedures, and customs e-clearance systems.',
          'Strong commercial negotiation aptitude and fluent consultative communication with carrier alliances.',
          'Bachelor degree in International Business, Logistics & Supply Chain, Maritime Economics, or equivalent.'
        ];

    const benefits = (job.benefits && job.benefits.length > 0)
      ? job.benefits
      : [
          'Full PTI Healthcare & Comprehensive Accident Insurance from day one',
          'Annual Performance Bonus (2 - 3 months base salary based on freight volume KPI)',
          'Flexible Hybrid Workplace arrangement with modern productivity allowance',
          'Sponsored international FIATA / Supply Chain certification training'
        ];

    // Smooth transition
    detailPanel.classList.remove('animate-swap');
    void detailPanel.offsetWidth;
    detailPanel.classList.add('animate-swap');

    detailPanel.innerHTML = `
      <div class="job-detail-dossier" style="display:flex; flex-direction:column; gap:18px; font-family:var(--font-inter, sans-serif);">
        
        <!-- 1. Header Identity Card (Insane Built In + Job Detail High-End Style) -->
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:14px;">
              ${logoHtml}
              <div>
                <div style="display:flex; align-items:center; gap:6px;">
                  <span style="font-family:var(--font-montserrat, sans-serif); font-size:16px; font-weight:700; color:#0F172A;">
                    ${job.company}
                  </span>
                  <span title="Verified Enterprise" style="display:inline-flex; align-items:center; color:#1877F2; font-size:15px;">
                    <i class="fa-solid fa-circle-check"></i>
                  </span>
                </div>
                <div style="font-size:13px; color:#64748B; margin-top:2px;">
                  <i class="fa-solid fa-location-dot" style="margin-right:4px; color:#94A3B8;"></i>${cleanLoc} &bull; <span style="color:#059669; font-weight:600;">${workplace}</span> &bull; ${applicantsCount} applicants
                </div>
              </div>
            </div>
            
            <!-- Compensation Pill -->
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; color:#047857; font-weight:800; font-size:14px; padding:6px 14px; border-radius:8px; display:inline-flex; align-items:center; gap:6px; letter-spacing:-0.2px;">
              <i class="fa-solid fa-bolt" style="color:#059669;"></i>
              <span>${salaryText}</span>
            </div>
          </div>

          <h2 style="font-family:var(--font-montserrat, 'Montserrat', sans-serif); font-size:22px; font-weight:800; color:#0F172A; line-height:1.3; margin:0 0 16px; letter-spacing:-0.3px;">
            ${job.title}
          </h2>

          <!-- Primary Actions Toolbar (Facebook-Pill Elevated) -->
          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; padding-top:14px; border-top:1px solid #F1F5F9;">
            <button type="button" class="btn-job-detail-apply" onclick="openApplyModal('${job.id}');" style="background:#1877F2; color:#FFFFFF; border:none; padding:10px 22px; border-radius:8px; font-weight:700; font-size:14px; cursor:pointer; display:inline-flex; align-items:center; gap:8px; box-shadow:0 4px 14px rgba(24,119,242,0.25); transition:transform 0.15s, background-color 0.15s;">
              <i class="fa-solid fa-paper-plane"></i>
              <span>⚡ Easy Apply with CV</span>
            </button>
            <button type="button" class="btn-job-detail-save ${isSaved ? 'saved' : ''}" onclick="toggleSaveJob('${job.id}', this);" style="background:${isSaved ? '#EBF5FF' : '#F1F5F9'}; color:${isSaved ? '#1877F2' : '#334155'}; border:1px solid ${isSaved ? '#BFDBFE' : '#E2E8F0'}; padding:10px 18px; border-radius:8px; font-weight:600; font-size:13.5px; cursor:pointer; display:inline-flex; align-items:center; gap:6px;">
              <i class="${isSaved ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
              <span>${isSaved ? 'Saved' : 'Save'}</span>
            </button>
            <a href="job-detail.html?id=${job.id}" target="_blank" style="margin-left:auto; color:#1877F2; font-weight:700; font-size:13.5px; text-decoration:none; display:inline-flex; align-items:center; gap:5px; padding:6px 12px; border-radius:6px; background:#F8FAFC; border:1px solid #E2E8F0;">
              <span>Full Job Dossier</span>
              <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:12px;"></i>
            </a>
          </div>
        </div>

        <!-- 2. Position Specifications 4-Grid -->
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:14px;">
          <div style="border-right:1px solid #F1F5F9; padding-right:10px;">
            <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#64748B; letter-spacing:0.04em;">Department</div>
            <div style="font-size:13px; font-weight:700; color:#0F172A; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${dept}</div>
          </div>
          <div style="border-right:1px solid #F1F5F9; padding-right:10px; padding-left:4px;">
            <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#64748B; letter-spacing:0.04em;">Seniority</div>
            <div style="font-size:13px; font-weight:700; color:#0F172A; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${expLevel}</div>
          </div>
          <div style="border-right:1px solid #F1F5F9; padding-right:10px; padding-left:4px;">
            <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#64748B; letter-spacing:0.04em;">Workplace</div>
            <div style="font-size:13px; font-weight:700; color:#059669; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${workplace}</div>
          </div>
          <div style="padding-left:4px;">
            <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#64748B; letter-spacing:0.04em;">Hiring Status</div>
            <div style="font-size:13px; font-weight:700; color:#1877F2; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">⚡ Urgent Opening</div>
          </div>
        </div>

        <!-- 3. Executive Role Summary Callout -->
        <div style="background:#F8FAFC; border-left:4px solid #1877F2; border-radius:0 8px 8px 0; padding:14px 18px; font-size:13.5px; color:#334155; line-height:1.6;">
          <strong style="color:#0F172A;">Role Overview:</strong> ${job.overview || 'Manage high-priority container logistics, intermodal freight coordination, and verified carrier operations with end-to-end accountability.'}
        </div>

        <!-- 4. Key Responsibilities Card -->
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:18px;">
          <h3 style="font-family:var(--font-montserrat, sans-serif); font-size:15px; font-weight:800; color:#0F172A; margin:0 0 12px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px; height:16px; background:#1877F2; border-radius:2px; display:inline-block;"></span>
            <span>Core Responsibilities</span>
          </h3>
          <ul style="margin:0; padding-left:0; list-style:none; display:flex; flex-direction:column; gap:8px;">
            ${responsibilities.map(r => `
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:13px; color:#334155; line-height:1.5;">
                <i class="fa-solid fa-check" style="color:#059669; font-size:12px; margin-top:3px; flex-shrink:0;"></i>
                <span>${r}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <!-- 5. Qualifications & Requirements Card -->
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:18px;">
          <h3 style="font-family:var(--font-montserrat, sans-serif); font-size:15px; font-weight:800; color:#0F172A; margin:0 0 12px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px; height:16px; background:#059669; border-radius:2px; display:inline-block;"></span>
            <span>Requirements &amp; Qualifications</span>
          </h3>
          <ul style="margin:0; padding-left:0; list-style:none; display:flex; flex-direction:column; gap:8px;">
            ${requirements.map(rq => `
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:13px; color:#334155; line-height:1.5;">
                <i class="fa-solid fa-shield-halved" style="color:#1877F2; font-size:12px; margin-top:3px; flex-shrink:0;"></i>
                <span>${rq}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <!-- 6. Comprehensive Benefits & Perks -->
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:18px;">
          <h3 style="font-family:var(--font-montserrat, sans-serif); font-size:15px; font-weight:800; color:#0F172A; margin:0 0 12px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px; height:16px; background:#F59E0B; border-radius:2px; display:inline-block;"></span>
            <span>Compensation &amp; Employee Benefits</span>
          </h3>
          <div style="display:flex; flex-wrap:wrap; gap:8px;">
            ${benefits.map(b => `
              <span style="background:#FEF3C7; border:1px solid #FDE68A; color:#92400E; font-size:12px; font-weight:600; padding:6px 12px; border-radius:6px; display:inline-flex; align-items:center; gap:6px;">
                <i class="fa-solid fa-gift" style="color:#D97706;"></i>
                <span>${b}</span>
              </span>
            `).join('')}
          </div>
        </div>

        <!-- 7. About Hiring Partner -->
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:16px; display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;">
          <div>
            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Accredited Logistics Enterprise</div>
            <div style="font-size:15px; font-weight:800; color:#0F172A; margin-top:2px;">${job.company}</div>
            <div style="font-size:12.5px; color:#64748B; margin-top:2px;">Tier-1 Port, Terminal &amp; Multimodal Supply Chain Infrastructure</div>
          </div>
          <a href="companies.html" style="background:#FFFFFF; border:1px solid #CBD5E1; color:#0F172A; font-weight:700; font-size:12.5px; padding:8px 16px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:6px; transition:background-color 0.15s;">
            <span>Explore Company</span>
            <i class="fa-solid fa-arrow-right"></i>
          </a>
        </div>

      </div>
    `;
  }

  window.selectJob = selectJob;

  function renderJobList() {
    let filtered = jobsDatabase;
    if (currentJobFilter === 'urgent') {
      filtered = jobsDatabase.filter(j => j.isUrgent);
    } else if (currentJobFilter === 'high-salary') {
      filtered = jobsDatabase.filter(j => j.isHighSalary);
    } else if (currentJobFilter !== 'all') {
      filtered = jobsDatabase.filter(j => j.category === currentJobFilter);
    }

    if (activeKeywordFilter) {
      const q = activeKeywordFilter.toLowerCase();
      filtered = filtered.filter(j => 
        (j.title && j.title.toLowerCase().includes(q)) || 
        (j.company && j.company.toLowerCase().includes(q)) || 
        (j.overview && j.overview.toLowerCase().includes(q)) ||
        (j.category && j.category.toLowerCase().includes(q)) ||
        (j.location && j.location.toLowerCase().includes(q))
      );
    }

    if (activeLocationFilter && activeLocationFilter !== 'all') {
      const locQ = activeLocationFilter.toLowerCase();
      filtered = filtered.filter(j => (j.location || '').toLowerCase().includes(locQ));
    }

    if (countBadge) {
      countBadge.textContent = `${filtered.length} ${filtered.length === 1 ? 'opening' : 'openings'}`;
    }
    const listCounter = document.getElementById('linkedin-jobs-counter');
    if (listCounter) {
      listCounter.textContent = `${filtered.length} openings`;
    }

    if (filtered.length === 0) {
      container.innerHTML = `
        <div style="padding: 48px 20px; text-align: center; color: #566174; background: #FFFFFF; border: 1px solid #d4d7e1; border-radius: 10px;">
          <svg style="width: 42px; height: 42px; stroke: #005B94; fill: none; margin-bottom: 12px; stroke-width: 1.8;" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <h2 style="font-size: 18px; color: #172033; margin-bottom: 6px; font-weight: 600;">No Openings Found</h2>
          <p style="font-size: 13.5px; margin-bottom: 14px; color: #566174;">Try adjusting your search terms or category filters.</p>
          <button type="button" onclick="openEmployerPostModal();" style="padding: 8px 18px; font-size: 13px; background: #002B49; color: #fff; border-radius: 6px; border: none; font-weight: 600; cursor: pointer;">
            <i class="fa-solid fa-plus-circle"></i> Post a Job
          </button>
        </div>
      `;
      if (detailPanel && isSplitLayout) {
        detailPanel.innerHTML = '<div style="padding: 48px 20px; text-align: center; color: #64748b;">Select or search for positions to view the role dossier.</div>';
      }
      return;
    }

    const savedIds = JSON.parse((localStorage.getItem('thesandbox_saved_jobs') || localStorage.getItem('sandbox_saved_jobs')) || '[]');

    if (isSplitLayout) {
      // Split layout compact vertical cards (index.html) - Insane 3.3x Brand Logo & High-Contrast Style
      container.innerHTML = filtered.map(job => {
        let logoHtml = '';
        if (job.companyLogo) {
          logoHtml = `<div class="brand-logo-pill" style="min-width:82px; max-width:104px; height:48px; border-radius:8px; background:#FFFFFF; border:1px solid #E2E8F0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; align-items:center; justify-content:center; overflow:hidden; flex-shrink:0; padding:4px 8px;">
            <img src="${job.companyLogo}" alt="${job.company}" style="max-width:100%; max-height:36px; object-fit:contain; display:block;">
          </div>`;
        } else {
          logoHtml = `<div class="brand-logo-pill" style="min-width:60px; height:48px; border-radius:8px; font-weight:700; color:#1877F2; background:#E7F3FF; font-size:16px; border:1px solid #BFDBFE; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            ${job.company.slice(0, 2).toUpperCase()}
          </div>`;
        }

        const workplace = job.workplace || 
          (job.location && job.location.toLowerCase().includes('remote') ? 'Remote' :
           job.location && job.location.toLowerCase().includes('hybrid') ? 'Hybrid' : 'On-site');
        const cleanLoc = job.cleanLocation || (job.location ? job.location.split('·')[0].trim() : 'Vietnam');
        const salaryText = job.salary || '₫32,000,000 - ₫48,000,000 / mo';
        const timeStr = job.time || 'A Minute Ago';
        const isSaved = savedIds.includes(job.id);
        const isActive = job.id === selectedJobId;

        return `
        <article class="job-card ${isActive ? 'active' : ''}" data-job-id="${job.id}" onclick="selectJob('${job.id}')" style="cursor:pointer; transition:all 0.15s ease; border-left:${isActive ? '4px solid #1877F2' : '1px solid #E2E8F0'}; background:${isActive ? '#F8FAFC' : '#FFFFFF'}; border-radius:10px; margin-bottom:12px; padding:14px; box-shadow:${isActive ? '0 4px 12px rgba(24,119,242,0.1)' : '0 1px 3px rgba(0,0,0,0.04)'};">
          <div style="display:flex; align-items:flex-start; gap:12px; width:100%;">
            ${logoHtml}
            <div style="flex:1; min-width:0;">
              <div style="display:flex; align-items:center; justify-content:space-between; gap:6px; margin-bottom:2px;">
                <div style="display:flex; align-items:center; gap:5px; min-width:0;">
                  <span class="company" style="margin:0; font-size:13px; font-weight:700; color:#1877F2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    ${job.company}
                  </span>
                  <span title="Verified Employer" style="color:#1877F2; font-size:12px; display:inline-flex;">
                    <i class="fa-solid fa-circle-check"></i>
                  </span>
                </div>
                <span style="font-size:11.5px; color:#64748B; white-space:nowrap;">
                  ${timeStr}
                </span>
              </div>

              <h3 class="title" style="margin:0 0 8px; font-size:15px; font-weight:800; color:#0F172A; line-height:1.35;">
                ${job.title}
              </h3>

              <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:6px;">
                <span style="background:#ECFDF5; border:1px solid #A7F3D0; color:#047857; font-weight:700; font-size:11.5px; padding:2px 7px; border-radius:5px; display:inline-flex; align-items:center; gap:3px;">
                  <i class="fa-solid fa-bolt" style="font-size:10px; color:#059669;"></i>${salaryText}
                </span>
                <span style="background:#EFF6FF; border:1px solid #BFDBFE; color:#1D4ED8; font-weight:600; font-size:11.5px; padding:2px 7px; border-radius:5px;">
                  ⚡ Easy Apply
                </span>
              </div>

              <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#64748B;">
                <span><i class="fa-solid fa-location-dot" style="margin-right:3px; color:#94A3B8;"></i>${cleanLoc}</span>
                <span>&bull;</span>
                <span style="color:#059669; font-weight:600;">${workplace}</span>
              </div>
            </div>
          </div>
        </article>
        `;
      }).join('');
    
    } else {
          logoHtml = `<div class="fb-brand-avatar" style="width:46px; height:46px; border-radius:50% !important; font-weight:700; color:#1877F2; background:#E7F3FF !important; font-size:15px; border:1px solid #BFDBFE !important; display:flex !important; align-items:center !important; justify-content:center !important; flex-shrink:0 !important;">
            ${job.company.slice(0, 2).toUpperCase()}
          </div>`;
        }

        const workplace = job.workplace || 
          (job.location && job.location.toLowerCase().includes('remote') ? 'Remote' :
           job.location && job.location.toLowerCase().includes('hybrid') ? 'Hybrid' : 'On-site');
        const cleanLoc = job.cleanLocation || (job.location ? job.location.split('·')[0].trim() : 'USA');
        const salaryText = job.salary || 'Competitive';
        const timeStr = job.time || 'A Minute Ago';
        const isSaved = savedIds.includes(job.id);
        const isActive = job.id === selectedJobId;

        return `
        <article class="job-card ${isActive ? 'active' : ''}" data-job-id="${job.id}">
          <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%;">
            ${logoHtml}
            <div style="flex: 1; min-width: 0;">
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 2px;">
                <span class="company" style="margin: 0; font-size: 13.5px; font-weight: 600; color: #1877F2;">
                  ${job.company}
                </span>
                <span style="font-size: 12px; color: #65676B; white-space: nowrap;">
                  ${timeStr}
                </span>
              </div>
              <h3 style="margin: 0 0 3px; font-size: 15px; line-height: 1.35; font-weight: 700; color: #050505; font-family: var(--font-montserrat, 'Montserrat', sans-serif); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${job.title}
              </h3>
              <div style="font-size: 13px; color: #65676B; margin-bottom: 6px;">
                ${cleanLoc} · ${workplace}
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span style="font-size: 13px; font-weight: 700; color: #050505;">
                  ${salaryText}
                </span>
                <button type="button" aria-label="Save ${job.title} job" class="favorite ${isSaved ? 'saved-active' : ''}" data-job-id="${job.id}" style="background: none; border: none; cursor: pointer; padding: 4px; display: inline-flex; align-items: center;">
                  <svg class="action-icon heart ${isSaved ? 'saved' : ''}" style="width: 16px; height: 16px; stroke: #65676B; fill: ${isSaved ? '#1877F2' : 'none'}; stroke-width: 1.8;" viewBox="0 0 24 24"><path d="M20.8 4.8a5.5 5.5 0 0 0-7.8 0L12 5.9l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.3 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/></svg>
                </button>
              </div>
            </div>
          </div>
        </article>
        `;
      }).join('');

      // Click card to select job
      container.querySelectorAll('.job-card').forEach(card => {
        card.addEventListener('click', (e) => {
          if (e.target.closest('.favorite') || e.target.closest('button')) return;
          const id = card.getAttribute('data-job-id');
          selectJob(id);
          if (window.innerWidth <= 1024 && detailPanel) {
            detailPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }
        });
      });

      // Synchronize detail panel selection
      const activeMatch = filtered.find(j => j.id === selectedJobId);
      if (activeMatch) {
        selectJob(selectedJobId);
      } else if (filtered[0]) {
        selectJob(filtered[0].id);
      }

    } else {
      // Full-width 6-column job cards (jobs.html)
      container.innerHTML = filtered.map(job => {
        const accent = '';

        let logoHtml = '';
        if (job.companyLogoType === 'comcast' || job.company === 'Comcast') {
          logoHtml = '<div class="logo comcast"><span class="peacock" aria-hidden="true"></span><span>COMCAST</span></div>';
        } else if (job.companyLogoType === 'headway' || job.company === 'Headway') {
          logoHtml = '<div class="logo headway" aria-label="Headway logo"></div>';
        } else if (job.companyLogoType === 'airwallex' || job.company === 'Airwallex') {
          logoHtml = '<div class="logo airwallex" aria-label="Airwallex logo">∿</div>';
        } else if (job.companyLogoType === 'cox' || job.company === 'Cox Enterprises') {
          logoHtml = '<div class="logo cox" aria-label="Cox Enterprises logo">COX</div>';
        } else if (job.companyLogo) {
          logoHtml = `<div class="logo"><img src="${job.companyLogo}" alt="${job.company}"></div>`;
        } else {
          logoHtml = `<div class="logo" style="font-weight:700; color:#005B94; background:#EAF1F7; font-size:16px;">${job.company.slice(0, 2).toUpperCase()}</div>`;
        }

        const workplace = job.workplace || 
          (job.location && job.location.toLowerCase().includes('remote') ? 'Remote' :
           job.location && job.location.toLowerCase().includes('hybrid') ? 'Hybrid' : 'On-site');
        const cleanLoc = job.cleanLocation || (job.location ? job.location.split('·')[0].trim() : 'USA');
        const salaryText = job.salary || 'Competitive';
        const expLevel = job.seniority || (job.specs && job.specs.exp ? job.specs.exp : 'Senior level');
        const timeStr = job.time || 'A Minute Ago';
        const isSaved = savedIds.includes(job.id);
        const isJunior = expLevel.toLowerCase().includes('junior') || expLevel.toLowerCase().includes('intern');

        return `
        <article class="job-card ${accent}" data-job-id="${job.id}">
          ${logoHtml}
          <div class="job-main">
            <p class="company">${job.company} <i class="fa-solid fa-shield-check badge-verified" style="color:#11c983; font-size:11px; margin-left:3px;" title="Accredited &amp; Verified Listing"></i></p>
            <h2 class="job-title"><a href="job-detail.html?id=${job.id}">${job.title}</a></h2>
          </div>
          <div class="separator" aria-hidden="true"></div>
          <div class="job-meta">
            <div class="posted"><svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg><span>${timeStr}</span></div>
            <div class="meta-line"><svg class="icon" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 8h8M8 12h8M8 16h4"/></svg><span>${workplace}</span></div>
            <div class="meta-line"><svg class="icon" viewBox="0 0 24 24"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg><span>${cleanLoc}</span></div>
          </div>
          <div class="job-extra">
            <div class="meta-line"><svg class="icon" viewBox="0 0 24 24"><path d="M12 2v20M5 5h14l-2 5H7L5 5ZM7 10l-3 8h16l-3-8"/></svg><span>${salaryText}</span></div>
            <div class="meta-line"><svg class="icon" viewBox="0 0 24 24"><path d="${isJunior ? 'M8 21h8M12 17v4M7 4h10l2 13H5L7 4Z M9 8h6' : 'M5 4h14v4a7 7 0 0 1-14 0V4ZM12 15v5M8 20h8M5 7H2v2a4 4 0 0 0 4 4M19 7h3v2a4 4 0 0 1-4 4'}"/></svg><span>${expLevel}</span></div>
          </div>
          <div class="right-actions">
            <button type="button" aria-label="Save ${job.title} job" class="favorite ${isSaved ? 'saved-active' : ''}" data-job-id="${job.id}">
              <svg class="action-icon heart ${isSaved ? 'saved' : ''}" viewBox="0 0 24 24"><path d="M20.8 4.8a5.5 5.5 0 0 0-7.8 0L12 5.9l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.3 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/></svg>
            </button>
            <button type="button" aria-label="Expand job details" class="expand" data-job-id="${job.id}">
              <svg class="action-icon" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6M6 15l6 6 6-6"/></svg>
            </button>
          </div>
        </article>
        `;
      }).join('');

      // Attach expand description handlers
      container.querySelectorAll('.expand').forEach(button => {
        button.addEventListener('click', (e) => {
          e.stopPropagation();
          const card = button.closest('.job-card');
          let details = card.querySelector('.job-description');
          if (details) {
            details.remove();
            button.setAttribute('aria-expanded', 'false');
            const svg = button.querySelector('svg');
            if (svg) svg.style.transform = 'rotate(0deg)';
            return;
          }
          const jobId = card.getAttribute('data-job-id');
          const job = jobsDatabase.find(j => j.id === jobId);
          const desc = job ? job.overview : 'View the full job description, qualifications, and application details on the employer’s career page.';
          
          details = document.createElement('div');
          details.className = 'job-description';
          details.style.cssText = 'grid-column: 2 / -1; margin: 12px 0 2px; padding: 12px 0 0; border-top: 1px dashed #d8dbe5; color: #566174; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;';
          details.innerHTML = `
            <p style="margin: 0 0 12px; color: #172033; font-size: 14px; line-height: 1.6;">${desc}</p>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
              <button type="button" class="btn-job-apply-inline" onclick="openJobApplyModal('${jobId || 'job-1'}');" style="background: #002B49; color: #ffffff; border: none; padding: 7px 18px; border-radius: 6px; font-weight: 700; font-size: 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;">
                <i class="fa-solid fa-paper-plane"></i> Quick Apply
              </button>
              <a href="job-detail.html?id=${jobId || 'job-1'}" style="color: #005B94; font-weight: 600; font-size: 13px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                View Full Dossier <i class="fa-solid fa-arrow-right"></i>
              </a>
            </div>
          `;
          card.appendChild(details);
          button.setAttribute('aria-expanded', 'true');
          const svg = button.querySelector('svg');
          if (svg) svg.style.transform = 'rotate(180deg)';
        });
      });
    }

    // Attach favorite heart handlers for all modes
    container.querySelectorAll('.favorite').forEach(button => {
      button.addEventListener('click', (e) => {
        e.stopPropagation();
        const heart = button.querySelector('.heart');
        const isNowSaved = !heart.classList.contains('saved');
        heart.classList.toggle('saved', isNowSaved);
        heart.style.fill = isNowSaved ? '#1458ff' : 'none';
        button.setAttribute('aria-pressed', isNowSaved ? 'true' : 'false');
        const jobId = button.getAttribute('data-job-id');
        if (jobId) {
          let saved = JSON.parse((localStorage.getItem('thesandbox_saved_jobs') || localStorage.getItem('sandbox_saved_jobs')) || '[]');
          if (isNowSaved) {
            if (!saved.includes(jobId)) saved.push(jobId);
            if (typeof showToast === 'function') showToast('Job bookmarked to saved dossier!');
          } else {
            saved = saved.filter(id => id !== jobId);
            if (typeof showToast === 'function') showToast('Job removed from saved.');
          }
          try {
            localStorage.setItem('thesandbox_saved_jobs', JSON.stringify(saved));
            localStorage.setItem('sandbox_saved_jobs', JSON.stringify(saved));
          } catch(e) {}
          if (detailPanel && isSplitLayout && selectedJobId === jobId) {
            const saveBtn = detailPanel.querySelector('.btn-job-detail-save');
            if (saveBtn) {
              saveBtn.classList.toggle('saved', isNowSaved);
              saveBtn.style.background = isNowSaved ? '#EAF1F7' : '#ffffff';
              saveBtn.style.color = isNowSaved ? '#1458ff' : '#292d3b';
              saveBtn.style.borderColor = isNowSaved ? '#1458ff' : '#dce0ed';
              saveBtn.innerHTML = `<i class="fa-${isNowSaved ? 'solid' : 'regular'} fa-bookmark"></i> ${isNowSaved ? 'Saved' : 'Save'}`;
            }
          }
        }
      });
    });
  }

  // Filter chips listeners
  chipBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      chipBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentJobFilter = btn.dataset.filter || 'all';
      renderJobList();
    });
  });

  // Search input listener
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      activeKeywordFilter = e.target.value.trim();
      renderJobList();
    });
  }

  // Category select fallback
  const categorySelect = document.getElementById('job-category-select');
  if (categorySelect) {
    categorySelect.addEventListener('change', (e) => {
      currentJobFilter = e.target.value;
      renderJobList();
    });
  }

  // Expose global filter helper
  window.filterJobsByCategory = function(cat) {
    currentJobFilter = cat || 'all';
    chipBtns.forEach(btn => {
      btn.classList.toggle('active', (btn.dataset.filter === cat));
    });
    renderJobList();
    const section = document.getElementById('section-jobs');
    if (section) section.scrollIntoView({ behavior: 'smooth' });
  };

  // Initial render
  renderJobList();
}

/* ==========================================================================
   9. QUICK APPLY MODAL & CANDIDATE TRANSMISSION
   ========================================================================== */
let activeApplyingJob = null;

function openApplyModal(job) {
  if (typeof window.openApplyModal === 'function') {
    return window.openApplyModal(job);
  }
}

function initJobApplyModal() {
  const modal = document.getElementById('job-apply-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const cancelBtn = document.getElementById('modal-cancel-btn');
  const form = document.getElementById('job-apply-form');
  if (!modal) return;

  function closeModal() {
    modal.classList.remove('show');
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('apply-fullname')?.value.trim();
      const phone = document.getElementById('apply-phone')?.value.trim();
      const email = document.getElementById('apply-email')?.value.trim();
      const exp = document.getElementById('apply-experience')?.value || '3 – 5 Years';

      if (!name || !phone) {
        alert('Please provide your name and contact phone number.');
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> TRANSMITTING APPLICATION...';
      submitBtn.disabled = true;

      setTimeout(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        closeModal();
        form.reset();

        // Push into ATS Candidate Database
        const fileInput = document.getElementById('apply-cv-file');
        const fileName = (fileInput && fileInput.files && fileInput.files[0]) 
          ? fileInput.files[0].name 
          : 'Nguyen_Minh_Tri_CV_2026.pdf';

        const list = getAtsCandidates();
        const newCandidate = {
          id: `cand-${Date.now()}`,
          name: name,
          role: activeApplyingJob ? activeApplyingJob.title : 'Logistics Specialist',
          company: activeApplyingJob ? activeApplyingJob.company : 'Enterprise 3PL',
          employerEmail: activeApplyingJob ? (activeApplyingJob.applyEmail || 'hr@company.com') : 'hr@company.com',
          cvFileName: fileName,
          exp: exp,
          email: email || `${name.toLowerCase().replace(/\s+/g, '.')}@candidate.vn`,
          phone: phone,
          date: 'Just now',
          status: 'new',
          score: '96% Match'
        };
        list.unshift(newCandidate);
        saveAtsCandidates(list);

        // Dual-write to Candidate Applications storage (thesandbox_applications)
        try {
          const apps = getSubmittedApplications();
          const candEmail = email || `${name.toLowerCase().replace(/\s+/g, '.')}@candidate.vn`;
          const currentJobId = activeApplyingJob ? activeApplyingJob.id : 'job-1';
          const currentJobTitle = activeApplyingJob ? activeApplyingJob.title : 'Logistics Specialist';
          
          const isDuplicate = apps.some(a => 
            (a.email === candEmail || a.candidateEmail === candEmail) && 
            (a.jobId === currentJobId || a.jobTitle === currentJobTitle)
          );

          if (!isDuplicate) {
            const fileSizeStr = (fileInput && fileInput.files && fileInput.files[0]) 
              ? (Math.round(fileInput.files[0].size / 1024) + ' KB') 
              : '1.8 MB';

            const newApp = {
              id: 'app-' + Date.now(),
              refNumber: 'SBX-2026-APP-' + Math.floor(10000 + Math.random() * 90000),
              jobId: currentJobId,
              jobTitle: currentJobTitle,
              company: activeApplyingJob ? activeApplyingJob.company : 'Enterprise 3PL',
              location: activeApplyingJob ? (activeApplyingJob.location || 'Vietnam') : 'Vietnam',
              shippingLane: activeApplyingJob ? (activeApplyingJob.category || 'Ocean Forwarding') : 'Ocean Forwarding',
              salary: activeApplyingJob ? (activeApplyingJob.salary || 'Competitive') : 'Competitive',
              candidateName: name,
              name: name,
              candidateEmail: candEmail,
              email: candEmail,
              candidatePhone: phone,
              phone: phone,
              experience: exp,
              cvFileName: fileName,
              cvFileSize: fileSizeStr,
              coverNote: '',
              status: 'New',
              stage: 'New',
              submittedAt: new Date().toISOString(),
              appliedDate: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
              appliedAt: new Date().toISOString(),
              isPrototypeLocal: true
            };
            apps.unshift(newApp);
            saveSubmittedApplications(apps);
          }
        } catch(syncErr) {
          console.error('Error synchronizing candidate applications:', syncErr);
        }

        // Update ATS counters
        updateAtsHeaderBadge();

        if (typeof window.renderAtsCandidates === 'function') {
          window.renderAtsCandidates();
        }

        showToast(`🎉 Application transmitted! Added to ${activeApplyingJob ? activeApplyingJob.company : 'Employer'} ATS pipeline.`);
      }, 700);
    });
  }
}

/* ==========================================================================
   9.5 EMPLOYER ATS & MONETIZATION MANAGEMENT SUITE
   ========================================================================== */
const defaultAtsCandidates = [
  { id: 'cand-1', name: 'Nguyen Van Minh', role: 'Senior Ocean Freight Forwarder', exp: '4 Years Exp', email: 'minh.nguyen@logistics-sea.vn', phone: '+84 908 123 456', date: 'Today, 14:20', status: 'interview', score: '94% Match' },
  { id: 'cand-2', name: 'Tran Thi Thao', role: 'AMR Robotics Systems Specialist', exp: '3 Years Exp', email: 'thao.tran@robotics-hub.com', phone: '+84 912 345 678', date: 'Yesterday', status: 'screening', score: '88% Match' },
  { id: 'cand-3', name: 'Le Hoang Nam', role: 'Global Cold Chain Logistics Director', exp: '8 Years Exp', email: 'nam.le@transpacific-cargo.com', phone: '+84 938 765 432', date: 'Sep 27', status: 'hired', score: '97% Match' },
  { id: 'cand-4', name: 'Pham Duc Anh', role: 'Licensed Customs Compliance Broker', exp: '5 Years Exp', email: 'anh.pham@aeo-customs.org', phone: '+84 903 888 999', date: 'Sep 26', status: 'new', score: '91% Match' },
  { id: 'cand-5', name: 'Bui Quoc Trung', role: 'Cross-Border Fleet Telematics Manager', exp: '4 Years Exp', email: 'trung.bui@haulage-logistics.vn', phone: '+84 987 654 321', date: 'Sep 25', status: 'screening', score: '85% Match' }
];

function getAtsCandidates() {
  try {
    const raw = localStorage.getItem('thesandbox_ats_candidates');
    if (raw) return JSON.parse(raw);
  } catch (err) {
    console.warn(err);
  }
  return defaultAtsCandidates;
}

function saveAtsCandidates(list) {
  try {
    localStorage.setItem('thesandbox_ats_candidates', JSON.stringify(list));
  } catch (err) {
    console.warn(err);
  }
}

function updateAtsHeaderBadge() {
  const list = getAtsCandidates();
  const badge = document.getElementById('header-ats-count');
  if (badge) badge.textContent = list.length;
}

let currentSelectedTier = 'featured';
let currentTierPriceVnd = '5,950,000 VND';
let currentTierPriceUsd = '~$249 USD';

window.updateSelectedTier = function(tier, priceVnd, priceUsd) {
  currentSelectedTier = tier || 'featured';
  if (!priceVnd || typeof priceVnd === 'number') {
    if (tier === 'standard') {
      priceVnd = '2,450,000 VND';
      priceUsd = '~$99 USD';
    } else if (tier === 'vip') {
      priceVnd = '14,900,000 VND';
      priceUsd = '~$599 USD';
    } else {
      priceVnd = '5,950,000 VND';
      priceUsd = '~$249 USD';
    }
  }
  currentTierPriceVnd = priceVnd;
  currentTierPriceUsd = priceUsd || '';

  const titleEl = document.getElementById('inv-item-title');
  const priceEl = document.getElementById('inv-item-price');
  const totalEl = document.getElementById('inv-total-val');

  const titles = {
    standard: 'Standard 3PL Job Placement (30 Days Active)',
    featured: 'Featured 3PL Job Placement (45 Days Active + Top Board)',
    vip: 'VIP Headhunt & Enterprise Placement (60 Days Active + ATS Access)'
  };

  if (titleEl) titleEl.textContent = titles[tier] || titles.featured;
  if (priceEl) priceEl.textContent = `${priceVnd} (${currentTierPriceUsd})`;
  if (totalEl) totalEl.textContent = `${priceVnd}`;
};


/* ==========================================================================
   CANDIDATE CV FILE UPLOAD HANDLERS
   ========================================================================== */
window.handleCvFileSelect = function(input) {
  if (!input || !input.files || input.files.length === 0) return;
  const file = input.files[0];
  const nameEl = document.getElementById('cv-file-name');
  const subEl = document.getElementById('cv-file-sub');
  const dropBox = document.getElementById('cv-file-drop');

  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
  if (file.size > 10 * 1024 * 1024) {
    showToast('File exceeds 10 MB maximum limit. Please select a smaller PDF or Word file.');
    input.value = '';
    return;
  }

  if (nameEl) {
    nameEl.innerHTML = `<i class="fa-solid fa-check-circle" style="color:#10B981; margin-right:6px;"></i> ${file.name}`;
  }
  if (subEl) {
    subEl.textContent = `${sizeMb} MB · Attached successfully for submission`;
  }
  if (dropBox) {
    dropBox.style.borderColor = '#10B981';
    dropBox.style.background = '#F0FDF4';
  }
  showToast(`Attached CV: ${file.name} (${sizeMb} MB)`);
};

window.toggleApplyMethodFields = function(method) {
  const directWrap = document.getElementById('field-wrap-direct-email');
  const extWrap = document.getElementById('field-wrap-external-url');
  const emailInput = document.getElementById('post-job-email');
  const urlInput = document.getElementById('post-job-apply-url');

  if (method === 'external') {
    if (directWrap) directWrap.style.display = 'none';
    if (extWrap) extWrap.style.display = 'block';
    if (emailInput) emailInput.removeAttribute('required');
    if (urlInput) urlInput.setAttribute('required', 'required');
  } else {
    if (directWrap) directWrap.style.display = 'block';
    if (extWrap) extWrap.style.display = 'none';
    if (emailInput) emailInput.setAttribute('required', 'required');
    if (urlInput) urlInput.removeAttribute('required');
  }
};

window.goToWizardStep = function(stepNum) {
  if (stepNum > 1) {
    const title = document.getElementById('post-job-title')?.value.trim();
    const company = document.getElementById('post-job-company')?.value.trim();
    if (!title || !company) {
      alert('Please fill in the Job Title and Hiring Company.');
      return;
    }
  }

  if (stepNum > 2) {
    const salary = document.getElementById('post-job-salary')?.value.trim();
    const method = document.querySelector('input[name="post-apply-method"]:checked')?.value || 'direct';
    const email = document.getElementById('post-job-email')?.value.trim();
    const applyUrl = document.getElementById('post-job-apply-url')?.value.trim();

    if (!salary) {
      alert('Please specify the Monthly Compensation Range.');
      return;
    }

    if (method === 'direct' && !email) {
      alert('Please provide the Recruiter Notification Email to receive candidate CVs.');
      return;
    }

    if (method === 'external' && !applyUrl) {
      alert('Please provide the External Career / Application URL for candidates to apply.');
      return;
    }
  }

  if (stepNum === 4) {
    window.updateSelectedTier(currentSelectedTier, currentTierPrice);
  }

  for (let i = 1; i <= 4; i++) {
    const tab = document.getElementById(`wstep-tab-${i}`);
    const pane = document.getElementById(`wstep-pane-${i}`);
    if (tab) {
      tab.classList.toggle('active', i === stepNum);
      tab.classList.toggle('completed', i < stepNum);
    }
    if (pane) {
      pane.classList.toggle('active', i === stepNum);
    }
  }
};

window.openEmployerPostModal = function(preferredTier) {
  // Check if we are already on post-job page
  const pathname = window.location.pathname || '';
  if (pathname.endsWith('post-job.html') || pathname.includes('/jobs/create')) {
    return;
  }
  const tierParam = preferredTier ? `?tier=${encodeURIComponent(preferredTier)}` : '';
  window.location.href = 'post-job.html' + tierParam;
};

window.closeEmployerPostModal = function() {
  const modal = document.getElementById('employer-post-job-modal');
  if (modal) modal.classList.remove('show');
};

window.fillJobTemplate = function() {
  const titleInput = document.getElementById('post-job-title');
  const overviewInput = document.getElementById('post-job-overview');
  const salaryInput = document.getElementById('post-job-salary');

  if (titleInput && !titleInput.value) {
    titleInput.value = 'Senior Ocean Freight & Multimodal Operations Lead';
  }
  if (salaryInput && !salaryInput.value) {
    salaryInput.value = '₫35,000,000 – ₫55,000,000 / mo';
  }
  if (overviewInput) {
    overviewInput.value = 'Lead end-to-end multi-modal forwarding operations (Ocean FCL/LCL & Air Freight) across Southeast Asian and Trans-Pacific ocean corridors. Coordinate carrier bookings, customs EDI declarations, demurrage control, and warehouse drayage dispatch. Requires 3+ years experience with CargoWise ONE or SAP TM, IATA/FIATA certification preferred, and strong vendor negotiation skills.';
  }
  showToast('🪄 3PL Enterprise job template inserted!');
};

window.handleEmployerJobSubmit = function(e) {
  e.preventDefault();

  const title = document.getElementById('post-job-title').value.trim();
  const company = document.getElementById('post-job-company').value.trim();
  const location = document.getElementById('post-job-location').value;
  const sector = document.getElementById('post-job-sector').value;
  const seniority = document.getElementById('post-job-seniority').value;
  const salary = document.getElementById('post-job-salary').value.trim();
  const workType = document.getElementById('post-job-work-type').value;
  const overview = document.getElementById('post-job-overview').value.trim();
  const applyMethod = document.querySelector('input[name="post-apply-method"]:checked')?.value || 'direct';
  const email = document.getElementById('post-job-email')?.value.trim() || '';
  const applyUrl = document.getElementById('post-job-apply-url')?.value.trim() || '';
  const openings = document.getElementById('post-job-openings').value.trim() || '2 Positions';

  const iconMap = {
    forwarding: 'fa-ship',
    robotics: 'fa-robot',
    tech: 'fa-network-wired',
    fleet: 'fa-truck-fast',
    customs: 'fa-passport',
    port: 'fa-anchor'
  };

  const newJob = {
    id: `emp-job-${Date.now()}`,
    title: title,
    company: company,
    applyMethod: applyMethod,
    applyEmail: applyMethod === 'direct' ? email : '',
    applyUrl: applyMethod === 'external' ? applyUrl : '',
    companyIcon: iconMap[sector] || 'fa-building',
    salary: salary,
    salaryVal: 35000000,
    location: location,
    category: sector,
    tags: [
      currentSelectedTier === 'vip' ? 'VIP Headhunt' : currentSelectedTier === 'featured' ? 'Featured 3PL' : 'Verified Employer',
      workType.split('·')[0].trim(),
      'Immediate Opening'
    ],
    isUrgent: currentSelectedTier === 'vip',
    isHighSalary: true,
    time: 'Just now',
    tier: currentSelectedTier,
    specs: {
      exp: seniority,
      edu: "Bachelor's Degree",
      dept: 'Logistics Operations',
      openings: openings
    },
    overview: overview,
    responsibilities: [
      'Manage daily carrier bookings, freight forwarding milestones, and customs clearance procedures.',
      'Liaise with overseas logistics networks, cargo terminals, and shipping lines for vessel space allocation.',
      'Resolve exceptions, port detention fees, and ensure SLA compliance for international freight accounts.'
    ],
    requirements: [
      `${seniority} proven background in logistics, supply chain, or international freight operations.`,
      'Familiarity with CargoWise One, EDI customs declarations, and Incoterms 2020.',
      'Fluent professional English communication for global vendor and client coordination.'
    ],
    benefits: [
      'Competitive payroll package with performance-linked quarterly freight bonuses.',
      'Comprehensive international healthcare coverage (Aon / Bao Viet Care).',
      'Annual corporate retreat and sponsored FIATA / CSCP accreditation.'
    ]
  };

  // Prepend to database
  jobsDatabase.unshift(newJob);

  // Save to localStorage
  try {
    const raw = localStorage.getItem('thesandbox_employer_jobs');
    const existing = raw ? JSON.parse(raw) : [];
    existing.unshift(newJob);
    localStorage.setItem('thesandbox_employer_jobs', JSON.stringify(existing));
  } catch (err) {
    console.warn(err);
  }

  // Close modal and reset
  closeEmployerPostModal();
  document.getElementById('employer-post-form').reset();

  // Update ATS stats
  const statJobs = document.getElementById('ats-stat-jobs');
  if (statJobs) statJobs.textContent = jobsDatabase.length;

  // Refresh job board and select newly created job
  if (typeof window.refreshSplitJobBoard === 'function') {
    window.refreshSplitJobBoard(newJob.id);
  }

  const jobSec = document.getElementById('section-jobs');
  if (jobSec) {
    jobSec.scrollIntoView({ behavior: 'smooth' });
  }

  showToast(`🚀 "${newJob.title}" published! Your ${currentSelectedTier.toUpperCase()} listing is now active in the Sandbox directory.`);
};

/* --- ATS Dashboard Methods --- */
window.openEmployerAtsModal = function() {
  const currentPath = window.location.pathname || '';
  if (currentPath.endsWith('employer-ats.html') || currentPath.includes('/employer/applicants')) {
    return;
  }
  window.location.href = 'employer-ats.html';
};

window.closeEmployerAtsModal = function() {
  const modal = document.getElementById('employer-ats-modal');
  if (modal) modal.classList.remove('show');
};

window.renderAtsCandidates = function(query = '') {
  const tbody = document.getElementById('ats-candidates-tbody');
  if (!tbody) return;

  const list = getAtsCandidates();
  const q = (query || '').toLowerCase().trim();
  const filtered = q ? list.filter(c => 
    c.name.toLowerCase().includes(q) || 
    c.role.toLowerCase().includes(q) || 
    c.email.toLowerCase().includes(q) || 
    c.status.toLowerCase().includes(q)
  ) : list;

  // Sync metrics
  const statJobs = document.getElementById('ats-stat-jobs');
  const statCandidates = document.getElementById('ats-stat-candidates');
  const statInterviewing = document.getElementById('ats-stat-interviewing');
  const statOffers = document.getElementById('ats-stat-offers');
  const headerCount = document.getElementById('header-ats-count');

  if (statJobs) statJobs.textContent = jobsDatabase.length;
  if (statCandidates) statCandidates.textContent = list.length;
  if (statInterviewing) statInterviewing.textContent = list.filter(c => c.status === 'interview').length;
  if (statOffers) statOffers.textContent = list.filter(c => c.status === 'hired').length;
  if (headerCount) headerCount.textContent = list.length;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding:32px 16px; color:#64748B;">
          <i class="fa-solid fa-user-slash" style="font-size:24px; color:#94A3B8; margin-bottom:8px; display:block;"></i>
          No applicants found matching "${query}".
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(c => {
    const initials = c.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
    const statusClass = c.status === 'new' ? 'status-new' :
                        c.status === 'screening' ? 'status-screening' :
                        c.status === 'interview' ? 'status-interview' :
                        c.status === 'hired' ? 'status-hired' : 'status-new';

    return `
      <tr data-cand-id="${c.id}">
        <td>
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; border-radius:50%; background:#0044CC; color:#FFF; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:11px; flex-shrink:0;">
              ${initials}
            </div>
            <div>
              <div style="font-weight:700; color:#0F172A;">${c.name}</div>
              <div style="font-size:11px; color:#0284C7; font-weight:600;"><i class="fa-solid fa-chart-line"></i> ${c.score || '90% Match'}</div>
            </div>
          </div>
        </td>
        <td style="font-weight:600; color:#1E293B;">${c.role}</td>
        <td><span style="font-size:11.5px; background:#F1F5F9; padding:2px 6px; border-radius:4px; font-weight:600;">${c.exp}</span></td>
        <td>
          <div style="font-size:11.5px; color:#334155;"><i class="fa-solid fa-envelope" style="font-size:10px; color:#64748B;"></i> ${c.email}</div>
          <div style="font-size:11.5px; color:#64748B;"><i class="fa-solid fa-phone" style="font-size:10px; color:#64748B;"></i> ${c.phone}</div>
        </td>
        <td style="font-size:11.5px; color:#64748B;">${c.date}</td>
        <td>
          <select class="ats-status-select ${statusClass}" onchange="updateCandidateStatus('${c.id}', this.value);">
            <option value="new" ${c.status === 'new' ? 'selected' : ''}>New Applicant</option>
            <option value="screening" ${c.status === 'screening' ? 'selected' : ''}>Screening CV</option>
            <option value="interview" ${c.status === 'interview' ? 'selected' : ''}>Interview Scheduled</option>
            <option value="hired" ${c.status === 'hired' ? 'selected' : ''}>Offer Extended</option>
          </select>
        </td>
        <td style="text-align:right;">
          <div style="display:inline-flex; gap:6px;">
            <button type="button" class="btn-ats-action" style="padding:4px 8px;" onclick="viewCandidateCV('${c.id}');" title="Review Full Resume">
              <i class="fa-solid fa-file-pdf" style="color:#DC2626;"></i> CV
            </button>
            <button type="button" class="btn-ats-action" style="padding:4px 8px; color:#94A3B8;" onclick="deleteAtsCandidate('${c.id}');" title="Remove Application">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
};

window.viewCandidateCV = function(id) {
  const list = getAtsCandidates();
  const c = list.find(item => item.id === id);
  if (!c) return;
  alert(`📋 APPLICANT DOSSIER\n\nName: ${c.name}\nRole: ${c.role}\nExperience: ${c.exp}\nContact: ${c.phone} | ${c.email}\nStatus: ${c.status.toUpperCase()}\nMatch Rating: ${c.score || '92%'}\n\nAccredited Background Check: Verified\nEnglish Proficiency: Professional Business Working\nDirect ATS channel active.`);
};

window.updateCandidateStatus = function(id, newStatus) {
  const list = getAtsCandidates();
  const cand = list.find(c => c.id === id);
  if (cand) {
    cand.status = newStatus;
    saveAtsCandidates(list);
    window.renderAtsCandidates(document.getElementById('ats-search-input')?.value || '');
    const statusLabels = { new: 'New Applicant', screening: 'Screening CV', interview: 'Interview Scheduled', hired: 'Offer Extended' };
    showToast(`Applicant ${cand.name} status updated: ${statusLabels[newStatus] || newStatus}`);
  }
};

window.deleteAtsCandidate = function(id) {
  let list = getAtsCandidates();
  const target = list.find(c => c.id === id);
  if (!target) return;
  if (confirm(`Remove application for ${target.name}?`)) {
    list = list.filter(c => c.id !== id);
    saveAtsCandidates(list);
    window.renderAtsCandidates(document.getElementById('ats-search-input')?.value || '');
    showToast(`Application for ${target.name} removed.`);
  }
};

window.filterAtsTable = function() {
  const input = document.getElementById('ats-search-input');
  window.renderAtsCandidates(input ? input.value : '');
};

window.exportAtsRosterCSV = function() {
  const list = getAtsCandidates();
  if (!list.length) {
    showToast('No candidates to export.');
    return;
  }
  const headers = ['Candidate ID', 'Full Name', 'Target Position', 'Experience', 'Email', 'Phone', 'Applied Date', 'Pipeline Status', 'AI Match Score'];
  const rows = list.map(c => [
    `"${c.id}"`,
    `"${c.name}"`,
    `"${c.role}"`,
    `"${c.exp}"`,
    `"${c.email}"`,
    `"${c.phone}"`,
    `"${c.date}"`,
    `"${c.status}"`,
    `"${c.score || '90%'}"`
  ]);
  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `Logistics_Candidate_Roster_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast(`✅ Exported ${list.length} candidate profiles to CSV roster.`);
};

function initEmployerSystem() {
  updateAtsHeaderBadge();

  // Escape key closes modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeEmployerPostModal();
      closeEmployerAtsModal();
    }
  });

  const postModal = document.getElementById('employer-post-job-modal');
  if (postModal) {
    postModal.addEventListener('click', (e) => {
      if (e.target === postModal) closeEmployerPostModal();
    });
  }

  const atsModal = document.getElementById('employer-ats-modal');
  if (atsModal) {
    atsModal.addEventListener('click', (e) => {
      if (e.target === atsModal) closeEmployerAtsModal();
    });
  }
}

/* ==========================================================================
   10. INTERACTIVE 2026 SALARY BENCHMARK CALCULATOR WIDGET
   ========================================================================== */
const salaryBenchmarks = {
  forwarding: {
    entry: { p25: '¥8,500', median: '¥12,000', p75: '¥15,000', medianNum: 12000, demand: 'High', bonus: '¥15k – ¥30k' },
    mid: { p25: '¥14,000', median: '¥18,500', p75: '¥24,000', medianNum: 18500, demand: 'Very High', bonus: '¥30k – ¥60k' },
    senior: { p25: '¥22,000', median: '¥28,000', p75: '¥38,000', medianNum: 28000, demand: 'Critical', bonus: '¥60k – ¥120k' },
    director: { p25: '¥35,000', median: '¥48,000', p75: '¥65,000', medianNum: 48000, demand: 'Executive', bonus: '¥120k – ¥250k' }
  },
  robotics: {
    entry: { p25: '¥10,000', median: '¥14,500', p75: '¥18,000', medianNum: 14500, demand: 'Very High', bonus: '¥20k – ¥40k' },
    mid: { p25: '¥18,000', median: '¥24,000', p75: '¥32,000', medianNum: 24000, demand: 'Surging (+38%)', bonus: '¥40k – ¥80k' },
    senior: { p25: '¥28,000', median: '¥36,000', p75: '¥50,000', medianNum: 36000, demand: 'Critical', bonus: '¥80k – ¥160k' },
    director: { p25: '¥45,000', median: '¥60,000', p75: '¥85,000', medianNum: 60000, demand: 'Top Tier', bonus: '¥150k – ¥350k' }
  },
  customs: {
    entry: { p25: '¥7,500', median: '¥10,500', p75: '¥13,500', medianNum: 10500, demand: 'Stable', bonus: '¥10k – ¥25k' },
    mid: { p25: '¥12,000', median: '¥16,000', p75: '¥21,000', medianNum: 16000, demand: 'High', bonus: '¥25k – ¥50k' },
    senior: { p25: '¥18,000', median: '¥25,000', p75: '¥33,000', medianNum: 25000, demand: 'AEO Specialist', bonus: '¥50k – ¥100k' },
    director: { p25: '¥30,000', median: '¥42,000', p75: '¥58,000', medianNum: 42000, demand: 'Executive', bonus: '¥100k – ¥200k' }
  },
  tech: {
    entry: { p25: '¥11,000', median: '¥15,000', p75: '¥19,500', medianNum: 15000, demand: 'High', bonus: '¥25k – ¥45k' },
    mid: { p25: '¥18,000', median: '¥25,000', p75: '¥34,000', medianNum: 25000, demand: 'Surging (+31%)', bonus: '¥50k – ¥100k' },
    senior: { p25: '¥30,000', median: '¥40,000', p75: '¥55,000', medianNum: 40000, demand: 'Critical', bonus: '¥100k – ¥200k' },
    director: { p25: '¥50,000', median: '¥68,000', p75: '¥95,000', medianNum: 68000, demand: 'Architect', bonus: '¥200k – ¥450k' }
  },
  port: {
    entry: { p25: '¥9,000', median: '¥13,000', p75: '¥16,000', medianNum: 13000, demand: 'High', bonus: '¥20k – ¥35k' },
    mid: { p25: '¥14,000', median: '¥18,000', p75: '¥23,000', medianNum: 18000, demand: 'Very High', bonus: '¥35k – ¥70k' },
    senior: { p25: '¥22,000', median: '¥29,000', p75: '¥38,000', medianNum: 29000, demand: 'TOS Lead', bonus: '¥70k – ¥130k' },
    director: { p25: '¥38,000', median: '¥52,000', p75: '¥72,000', medianNum: 52000, demand: 'Harbor Bureau', bonus: '¥140k – ¥280k' }
  }
};

function initSalaryCalculator() {
  const roleSelect = document.getElementById('calc-role');
  const expSelect = document.getElementById('calc-exp');
  const medianEl = document.getElementById('calc-median-val');
  const p25El = document.getElementById('calc-p25-val');
  const p75El = document.getElementById('calc-p75-val');
  const demandEl = document.getElementById('calc-demand-badge');
  const bonusEl = document.getElementById('calc-bonus-range');
  const barP25 = document.getElementById('calc-bar-p25');
  const barMedian = document.getElementById('calc-bar-median');
  const barP75 = document.getElementById('calc-bar-p75');
  const exploreJobsBtn = document.getElementById('calc-explore-jobs');
  if (!roleSelect || !expSelect) return;

  function updateSalaryDisplay() {
    const role = roleSelect.value;
    const exp = expSelect.value;
    const data = (salaryBenchmarks[role] && salaryBenchmarks[role][exp]) || salaryBenchmarks.forwarding.mid;

    if (medianEl) medianEl.textContent = `${data.median} / mo`;
    if (p25El) p25El.textContent = data.p25;
    if (p75El) p75El.textContent = data.p75;
    if (demandEl) demandEl.textContent = `Demand: ${data.demand}`;
    if (bonusEl) bonusEl.textContent = `Est. Annual Bonus: ${data.bonus}`;

    // Bar fills (scaled to max 75000)
    const baseP25 = Math.min(100, Math.max(25, (parseInt(data.p25.replace(/[^\d]/g, ''), 10) / 60000) * 100));
    const baseMed = Math.min(100, Math.max(45, (data.medianNum / 60000) * 100));
    const baseP75 = Math.min(100, Math.max(65, (parseInt(data.p75.replace(/[^\d]/g, ''), 10) / 60000) * 100));

    if (barP25) barP25.style.width = `${baseP25}%`;
    if (barMedian) barMedian.style.width = `${baseMed}%`;
    if (barP75) barP75.style.width = `${baseP75}%`;
  }

  roleSelect.addEventListener('change', updateSalaryDisplay);
  expSelect.addEventListener('change', updateSalaryDisplay);

  if (exploreJobsBtn) {
    exploreJobsBtn.addEventListener('click', () => {
      const role = roleSelect.value;
      if (window.filterJobsByKeyword) {
        window.filterJobsByKeyword('', role, 'all');
      }
    });
  }

  updateSalaryDisplay();
}

/* ==========================================================================
   11. HERO SEARCH ENGINE WIDGET
   ========================================================================== */
function initHeroSearchEngine() {
  const form = document.getElementById('hero-search-form');
  const keywordInput = document.getElementById('hero-keyword');
  const sectorSelect = document.getElementById('hero-sector');
  const locationSelect = document.getElementById('hero-location');
  const tagPills = document.querySelectorAll('.hero-tag-pill');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const kw = keywordInput ? keywordInput.value.trim() : '';
    const sector = sectorSelect ? sectorSelect.value : 'all';
    const loc = locationSelect ? locationSelect.value : 'all';

    if (window.filterJobsByKeyword) {
      window.filterJobsByKeyword(kw, sector, loc);
    }
  });

  tagPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const query = pill.getAttribute('data-query') || pill.textContent.trim();
      if (keywordInput) keywordInput.value = query;
      if (window.filterJobsByKeyword) {
        window.filterJobsByKeyword(query, 'all', 'all');
      }
    });
  });
}

/* ==========================================================================
   12. TOAST NOTIFICATION UTILITY
   ========================================================================== */
function showToast(message) {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.className = 'toast-msg';
    document.body.appendChild(toast);
  }

  toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3800);
}

/* ==========================================================================
   13. INTERACTION & ANIMATION CONTROLLER (HUMAN-CRAFTED POLISH)
   ========================================================================== */

/**
 * 1. Subtle Scroll Reveal (IntersectionObserver with 0.15 threshold)
 * Animates key content blocks gently when entering the viewport without gaudy effects.
 */
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;

  if (!('IntersectionObserver' in window)) {
    reveals.forEach(el => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  reveals.forEach(el => observer.observe(el));
}

/**
 * 2. Navbar State Changes While Scrolling
 * Transitions header background, padding, and subtle shadow when scrollY > 30.
 */
function initScrollNavbar() {
  const header = document.querySelector('.wt-header, .fw-masthead-wrapper, .header');
  if (!header) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        header.classList.toggle('scrolled', window.scrollY > 30);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

/**
 * 3. Subtle Parallax Movement for Hero
 * Shifts background imagery at a gentle 0.08 ratio without heavy visual distortion.
 */
function initHeroParallax() {
  const heroViewport = document.querySelector('.hero-editorial-viewport');
  if (!heroViewport) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y > 600) return;
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const activeImg = heroViewport.querySelector('.hero-editorial-slide.active img, .hero-editorial-slide img');
        if (activeImg) {
          activeImg.style.transform = `translateY(${y * 0.08}px) scale(1.02)`;
        }
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

/**
 * 4. Eased Number Counting Animation for Statistics
 * Uses cubic ease-out to smoothly animate statistics upon viewport intersection.
 */
function initStatisticCounters() {
  const statElements = document.querySelectorAll('[data-value]');
  if (!statElements.length) return;

  function animateNumber(el) {
    const rawVal = el.getAttribute('data-value');
    const target = parseFloat(rawVal);
    const isFloat = rawVal.includes('.');
    const decimals = parseInt(el.getAttribute('data-decimals') || (isFloat ? '1' : '0'), 10);
    const prefix = el.getAttribute('data-prefix') || '';
    const suffix = el.getAttribute('data-suffix') || '';
    const duration = 1200;
    const start = performance.now();

    function update(time) {
      const progress = Math.min((time - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // Cubic ease-out
      const current = target * eased;

      let display;
      if (decimals > 0) {
        display = current.toFixed(decimals);
      } else {
        display = Math.floor(current).toLocaleString();
      }

      el.textContent = `${prefix}${display}${suffix}`;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        if (decimals > 0) {
          el.textContent = `${prefix}${target.toFixed(decimals)}${suffix}`;
        } else {
          el.textContent = `${prefix}${target.toLocaleString()}${suffix}`;
        }
      }
    }

    requestAnimationFrame(update);
  }

  if ('IntersectionObserver' in window) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateNumber(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    statElements.forEach(el => counterObserver.observe(el));
  } else {
    statElements.forEach(animateNumber);
  }
}

/**
 * 14. Government Directives & Policy Tabs Controller (initGovDirectivesTabs)
 */
function initGovDirectivesTabs() {
  const tabs = document.querySelectorAll('.gov-tab-btn, .gov-vtab');
  const titleEl = document.getElementById('gov-lead-title');
  const summaryEl = document.getElementById('gov-lead-summary');
  const tagEl = document.getElementById('gov-lead-tag');
  const readTextEl = document.getElementById('gov-lead-read-text');
  const listEl = document.getElementById('gov-news-list');
  if (!tabs.length || !titleEl || !listEl) return;

  const govData = {
    political: {
      tag: 'Official Summit',
      leadTitle: 'State Leadership Holds Bilateral Summit with Prime Minister Modi',
      summary: 'High-level inter-ministerial policy framework establishing standardized logistics talent benchmarks, multi-modal supply chain corridors, and vocational accreditation standards.',
      readText: 'Read Statement',
      bullets: [
        { text: 'President Replies to Youth Delegation from 10 Leading International Partner Universities', date: '09-24' },
        { text: 'Official Congratulatory Message Delivered to 48th WorldSkills Competition', date: '09-24' },
        { text: 'Vietnam National Logistics Skills Competition Concludes in Hanoi; Standards Unveiled', date: '09-24' },
        { text: 'Leadership Meets WorldSkills International President and Chief Executive Officer', date: '09-24' }
      ]
    },
    important: {
      tag: 'Strategic Directive',
      leadTitle: 'State Council Directives on High-Quality Full Employment Strategy & Modern Logistics Capacity',
      summary: 'Comprehensive national initiatives directing state-backed enterprise incentives, digital skills pipelines, and integrated workforce security measures across logistics hubs.',
      readText: 'Read Directive',
      bullets: [
        { text: 'National University Graduate & Youth Employment Deployment Teleconference Convenes', date: '09-24' },
        { text: 'Human Resources Ministry Deploys Fall National Logistics & Campus Recruitment Drive', date: '09-24' },
        { text: '3rd National Vocational Skills Competition Qualifiers Commence Nationwide', date: '09-23' },
        { text: 'Inter-Regional Supply Chain & Labor Coordination Summit Held for Greater Economic Zones', date: '09-23' },
        { text: 'Enterprise Employment Safeguard: Targeted Corporate Payroll Rebate Policies Issued', date: '09-22' }
      ]
    },
    core: {
      tag: 'Priority Initiative',
      leadTitle: 'Accelerating High-Skilled Talent Cultivation & Frontier Technical Occupational Standards',
      summary: 'Strategic roadmap standardizing automated freight handling, AI telematics qualifications, and national certification pathways for emerging industrial logistics professions.',
      readText: 'View Details',
      bullets: [
        { text: 'Action Plan for High-Quality Development of Technical & Vocational Education Enacted', date: '09-24' },
        { text: 'National Occupational Standards for Industrial Robotics & Automated Warehousing Released', date: '09-24' },
        { text: 'Standardized On-Demand Labor Market Hubs Accelerated Across Priority Freight Terminals', date: '09-23' },
        { text: 'HR Services Industry Initiative: Guiding Multi-Modal Freight Talent Supply Networks', date: '09-23' },
        { text: 'Vocational Digital Learning Platform Expands Reach to Over 10 Million Active Learners', date: '09-22' }
      ]
    }
  };

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      const tabKey = tab.getAttribute('data-gov-tab');
      const data = govData[tabKey];
      if (!data) return;

      titleEl.innerHTML = `<a href="#">${data.leadTitle}</a>`;
      if (summaryEl) summaryEl.textContent = data.summary;
      if (tagEl) tagEl.textContent = data.tag;
      if (readTextEl) readTextEl.textContent = data.readText;

      listEl.innerHTML = data.bullets.map(b => `
        <li>
          <span class="gov-news-dot"></span>
          <a href="#" class="gov-news-title">${b.text}</a>
          <span class="gov-news-date">${b.date}</span>
        </li>
      `).join('');
    });
  });
}

/**
 * 15. Featured Careers & Courses Tabs Handler with Auto-Tab (Every 15 Seconds)
 */
const careerCatalogData = {
  exam: [
    { title: 'Legal & Regulatory Foundations', modules: '1 Module', views: '8,166,589 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Executive Verbal & Communication', modules: '1 Module', views: '7,478,162 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Analytical Judgment & Concepts', modules: '1 Module', views: '7,398,773 Views', img: 'images/career_banner_3.svg?v=2' },
    { title: 'Quantitative Logistics & Strategy', modules: '3 Modules', views: '6,550,610 Views', img: 'images/career_banner_4.svg?v=2' }
  ],
  guidance: [
    { title: 'Port & Maritime Career Pathways', modules: '2 Modules', views: '5,210,400 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Air Cargo Operations Onboarding', modules: '1 Module', views: '4,850,210 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Global 3PL Leadership Foundations', modules: '3 Modules', views: '6,120,890 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Customs Brokerage Licensing Guide', modules: '2 Modules', views: '7,430,120 Views', img: 'images/career_banner_3.svg?v=2' }
  ],
  cert: [
    { title: 'FIATA Freight Forwarding Diploma', modules: '4 Modules', views: '7,120,450 Views', img: 'images/career_banner_3.svg?v=2' },
    { title: 'Dangerous Goods (IATA DGR) Handling', modules: '2 Modules', views: '5,890,300 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Cold Chain GDP Compliance Masterclass', modules: '3 Modules', views: '6,450,800 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'WMS & ERP Warehouse Systems Architect', modules: '2 Modules', views: '5,980,110 Views', img: 'images/career_banner_2.svg?v=2' }
  ],
  growth: [
    { title: 'High-Volume Ocean Contract Negotiation', modules: '2 Modules', views: '6,780,290 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Intermodal Fleet Optimization Strategies', modules: '3 Modules', views: '5,340,780 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Cross-Border Customs Audit Readiness', modules: '1 Module', views: '4,890,450 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Supply Chain Risk & Resilience Leadership', modules: '2 Modules', views: '6,120,340 Views', img: 'images/career_banner_3.svg?v=2' }
  ],
  postgrad: [
    { title: 'Global Supply Chain Executive MBA', modules: '6 Modules', views: '4,420,100 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Maritime Economics & Port Finance', modules: '4 Modules', views: '3,980,670 Views', img: 'images/career_banner_3.svg?v=2' },
    { title: 'Advanced Operations Research in Freight', modules: '5 Modules', views: '3,810,490 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'International Shipping Law & Incoterms 2026', modules: '3 Modules', views: '5,670,220 Views', img: 'images/career_banner_4.svg?v=2' }
  ],
  practice: [
    { title: 'Deploying Autonomous Mobile Robots (AMR)', modules: '3 Modules', views: '6,840,550 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Blockchain Traceability in Cold Chains', modules: '2 Modules', views: '5,750,890 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Warehouse Digital Twins & Simulation', modules: '3 Modules', views: '6,230,140 Views', img: 'images/career_banner_3.svg?v=2' },
    { title: 'Green Freight Carbon Footprint Auditing', modules: '2 Modules', views: '4,920,800 Views', img: 'images/career_banner_1.svg?v=2' }
  ],
  knowledge: [
    { title: 'Deep-Sea Container Economics Primer', modules: '2 Modules', views: '7,650,440 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Air Freight ULD Master Planning', modules: '1 Module', views: '5,320,110 Views', img: 'images/career_banner_3.svg?v=2' },
    { title: 'ASEAN Overland Freight Corridors', modules: '2 Modules', views: '6,440,780 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Last-Mile Micro-Fulfillment Tech', modules: '3 Modules', views: '7,890,320 Views', img: 'images/career_banner_2.svg?v=2' }
  ],
  it: [
    { title: 'AI Forecasting in Demand Planning', modules: '3 Modules', views: '8,420,900 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Logistics Telematics & IoT Sensor Hubs', modules: '2 Modules', views: '6,150,700 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Python for Freight Rate Analytics', modules: '4 Modules', views: '7,890,430 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'API Integration for EDI & Manifest Feeds', modules: '3 Modules', views: '6,310,250 Views', img: 'images/career_banner_3.svg?v=2' }
  ],
  lifestyle: [
    { title: 'Seafarer Mental Health & Resilience', modules: '1 Module', views: '4,210,300 Views', img: 'images/career_banner_2.svg?v=2' },
    { title: 'Cross-Cultural Freight Communications', modules: '2 Modules', views: '5,560,890 Views', img: 'images/career_banner_1.svg?v=2' },
    { title: 'Ergonomics & Safety in Modern Fulfillment', modules: '1 Module', views: '6,120,400 Views', img: 'images/career_banner_4.svg?v=2' },
    { title: 'Sustainable Living for Long-Haul Logistics', modules: '2 Modules', views: '4,670,120 Views', img: 'images/career_banner_3.svg?v=2' }
  ]
};

// Manual tab selection only - no auto-switching or window hijacking
window.selectCareerTab = function(btnEl, categoryName, isManual = true) {
  if (!btnEl) return;
  const parent = btnEl.closest('.career-tabs-scroll') || btnEl.parentElement;
  if (parent) {
    parent.querySelectorAll('.career-tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });

    // Adjust horizontal scroll inside tabs container only without scrolling the window
    if (parent.scrollWidth > parent.clientWidth) {
      const targetScroll = btnEl.offsetLeft - (parent.clientWidth / 2) + (btnEl.clientWidth / 2);
      parent.scrollLeft = targetScroll;
    }
  }
  btnEl.classList.add('active');

  // Update dynamic cards for this category
  const catKey = btnEl.getAttribute('data-category') || 'exam';
  renderCareerCards(catKey);

  if (isManual && typeof showToast === 'function') {
    showToast(`Viewing courses in: ${categoryName}`);
  }
};

function renderCareerCards(catKey) {
  const container = document.getElementById('career-cards-container');
  if (!container) return;

  const courses = careerCatalogData[catKey] || careerCatalogData.exam;
  
  // Smooth subtle card swap transition
  container.style.opacity = '0.5';
  container.style.transform = 'translateY(4px)';
  container.style.transition = 'opacity 0.22s ease, transform 0.22s ease';

  setTimeout(() => {
    container.innerHTML = courses.map((c) => `
      <article class="career-card-item reveal" onclick="showToast('Opening Course Module: ${c.title.replace(/'/g, "\\'")}');">
        <div class="career-card-banner">
          <img src="${c.img}" alt="${c.title}" class="career-card-img">
          <div class="career-card-overlay">
            <h3 class="career-card-title">${c.title}</h3>
          </div>
        </div>
      </article>
    `).join('');

    container.style.opacity = '1';
    container.style.transform = 'translateY(0)';
  }, 100);
}

// Auto-tabbing permanently disabled per user requirement (manual selection only)
function initCareerAutoTab() {
  // No-op: tabs are strictly user-driven ("self do")
}

/**
 * 16. Display Scale Switcher (1.0x Standard vs 1.1x Enlarge)
 */
window.setAppScale = function(scale) {
  try {
    document.body.style.zoom = scale;
    localStorage.setItem('sandboxed_app_scale', scale.toString());
  } catch (e) {
    console.error('Scale set failed', e);
  }

  const btn1x = document.getElementById('scale-btn-1x');
  const btn11x = document.getElementById('scale-btn-11x');
  if (btn1x && btn11x) {
    if (scale > 1.0) {
      btn1x.classList.remove('active');
      btn11x.classList.add('active');
    } else {
      btn1x.classList.add('active');
      btn11x.classList.remove('active');
    }
  }

  if (typeof showToast === 'function') {
    showToast(`Display scale set to ${scale === 1.0 ? '1.0x (Standard Density)' : '1.1x (Spacious & Enlarge)'}`);
  }
};

// Restore saved scale preference on load & initialize carousels
document.addEventListener('DOMContentLoaded', () => {
  const savedScale = parseFloat(localStorage.getItem('sandboxed_app_scale') || '1.0');
  if (savedScale && savedScale !== 1.0) {
    setAppScale(savedScale);
  }
  initHeroCarousel();
});

/**
 * 17. Hero Half-Rectangle 3-Slide Carousel Logic
 */
function initHeroCarousel() {
  const viewport = document.getElementById('wt-hero-carousel');
  if (!viewport) return;

  const slides = viewport.querySelectorAll('.wt-slide');
  const dots = viewport.querySelectorAll('.wt-slider-dot');
  const prevBtn = document.getElementById('wt-slider-prev');
  const nextBtn = document.getElementById('wt-slider-next');
  if (slides.length === 0) return;

  let current = 0;
  let timer = null;

  function goToSlide(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((s, i) => {
      s.classList.toggle('active', i === current);
    });
    dots.forEach((d, i) => {
      d.classList.toggle('active', i === current);
    });
  }

  function startAutoplay() {
    stopAutoplay();
    timer = setInterval(() => {
      goToSlide(current + 1);
    }, 5500);
  }

  function stopAutoplay() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.preventDefault();
      goToSlide(current - 1);
      startAutoplay();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.preventDefault();
      goToSlide(current + 1);
      startAutoplay();
    });
  }

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.getAttribute('data-index') || '0', 10);
      goToSlide(idx);
      startAutoplay();
    });
  });

  viewport.addEventListener('mouseenter', stopAutoplay);
  viewport.addEventListener('mouseleave', startAutoplay);

  startAutoplay();
}

/**
 * 18. Mobile Navigation Drawer Controller
 */
window.openMobileDrawer = function() {
  const drawer = document.getElementById('mobile-nav-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  const hamburger = document.getElementById('btn-mobile-hamburger');
  if (drawer && overlay) {
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
  }
};

window.closeMobileDrawer = function() {
  const drawer = document.getElementById('mobile-nav-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  const hamburger = document.getElementById('btn-mobile-hamburger');
  if (drawer && overlay) {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
  }
};

window.toggleMobileAccordion = function(btnEl) {
  if (!btnEl) return;
  const group = btnEl.closest('.mobile-nav-group');
  if (group) {
    group.classList.toggle('open');
  }
};

// Global escape key listener for mobile drawer
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeMobileDrawer();
  }
});



/**
 * 19. Unified Portal Search Digest Controller (Jobs · News · Courses)
 */
let currentSearchPillar = 'jobs';

window.setSearchPillar = function(pillar) {
  currentSearchPillar = pillar;
  
  // Update Tab States
  const tabs = document.querySelectorAll('.portal-tab-btn');
  tabs.forEach(tab => {
    tab.classList.toggle('active', tab.getAttribute('data-target') === pillar);
  });

  const queryLabel = document.getElementById('unified-query-label');
  const queryInput = document.getElementById('unified-query-input');
  const btnSearchText = document.getElementById('btn-search-text');
  const groupSector = document.getElementById('group-sector-select');
  const groupLocation = document.getElementById('group-location-select');

  if (pillar === 'jobs') {
    if (queryLabel) queryLabel.textContent = 'Job Title, Role or Keyword';
    if (queryInput) queryInput.placeholder = 'e.g. Ocean Freight Forwarder, Customs Specialist, Port Captain...';
    if (btnSearchText) btnSearchText.textContent = 'Search Jobs';
    if (groupSector) groupSector.style.display = '';
    if (groupLocation) groupLocation.style.display = '';
  } else if (pillar === 'news') {
    if (queryLabel) queryLabel.textContent = 'Market Intelligence / Industry Topics';
    if (queryInput) queryInput.placeholder = 'e.g. Container Freight Indices, Decree 163, Cold Chain Trends...';
    if (btnSearchText) btnSearchText.textContent = 'Search News';
    if (groupSector) groupSector.style.display = '';
    if (groupLocation) groupLocation.style.display = 'none';
  } else if (pillar === 'courses') {
    if (queryLabel) queryLabel.textContent = 'Logistics Certification or Course';
    if (queryInput) queryInput.placeholder = 'e.g. FIATA Higher Diploma, Dangerous Goods, Incoterms 2020...';
    if (btnSearchText) btnSearchText.textContent = 'Search Courses';
    if (groupSector) groupSector.style.display = '';
    if (groupLocation) groupLocation.style.display = 'none';
  }
};

window.handlePortalUnifiedSearch = function(event) {
  if (event) event.preventDefault();
  const query = (document.getElementById('unified-query-input')?.value || '').trim();
  const sector = document.getElementById('unified-sector-select')?.value || 'all';
  const location = document.getElementById('unified-location-select')?.value || 'all';

  if (currentSearchPillar === 'jobs') {
    const jobSection = document.getElementById('section-jobs');
    if (jobSection) {
      jobSection.scrollIntoView({ behavior: 'smooth' });
    }
    if (typeof filterJobsByKeyword === 'function') {
      filterJobsByKeyword(query, sector, location);
    }
    showToast(`Searching jobs for: "${query || 'All Roles'}"`);
  } else if (currentSearchPillar === 'news') {
    const newsSection = document.getElementById('section-today');
    if (newsSection) {
      newsSection.scrollIntoView({ behavior: 'smooth' });
    }
    showToast(`Browsing intelligence news matching: "${query || 'Latest Updates'}"`);
  } else if (currentSearchPillar === 'courses') {
    const courseSection = document.getElementById('section-training');
    if (courseSection) {
      courseSection.scrollIntoView({ behavior: 'smooth' });
    }
    showToast(`Browsing certifications matching: "${query || 'All Programs'}"`);
  }
};

window.executeQuickPill = function(term) {
  const queryInput = document.getElementById('unified-query-input');
  if (queryInput) {
    queryInput.value = term;
  }
  if (term.toLowerCase().includes('diploma') || term.toLowerCase().includes('fiata')) {
    setSearchPillar('courses');
  } else {
    setSearchPillar('jobs');
  }
  handlePortalUnifiedSearch();
};


/* ==========================================================================
   20. NEWS & ARTICLE PUBLISHING SYSTEM (EDITORIAL PLATFORM)
   ========================================================================== */

const defaultNewsArticles = [
  {
    "id": "cai-mep-channel-expansion",
    "aliasId": "news-1",
    "slug": "cai-mep-channel-expansion",
    "title": "Cai Mep–Thi Vai expands deep-draft access for mega-vessels",
    "category": "maritime",
    "categoryLabel": "Maritime & Port Logistics",
    "categoryIcon": "fa-anchor",
    "author": "Maritime Editorial Desk",
    "authorRole": "Senior Port Operations Analyst",
    "authorInitial": "MD",
    "date": "19 October 2026",
    "timeAgo": "2h ago",
    "readTime": "4 min read",
    "readers": "8,420 readers",
    "isLead": true,
    "isVerified": true,
    "source": "Vietnam Maritime Administration (Vinamarine) / VietnamNet",
    "sourceUrl": "https://vinamarine.gov.vn",
    "tags": [
      "Cai Mep–Thi Vai",
      "Deep-Draft Port",
      "Mega Container Ships",
      "Maritime Infrastructure"
    ],
    "image": "images/hero_1.jpg",
    "imageCaption": "A container vessel approaches a deep-water terminal at Cai Mep–Thi Vai. (Photo: Vietnam Maritime Administration / VietnamNet)",
    "summary": "The channel expansion could create new options for large container ships serving Vietnam's international shipping routes.",
    "body": "\n<p class=\"bbc-lead-para\"><strong>The Ministry of Transport and the <a href=\"https://vinamarine.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Vietnam Maritime Administration (Vinamarine)</a></strong> have officially commissioned the Phase 1 maintenance and capital dredging project for the Cai Mep–Thi Vai navigational channel, deepening the access fairway to a consistent design draft of -15.5 meters at low tide.</p>\n\n<p>The multi-month maritime engineering initiative eliminates historical siltation bottlenecks between buoy zero and the upstream terminal complexes, establishing an unobstructed nautical corridor with a guaranteed bottom width of 350 meters.</p>\n\n<p>According to official hydrographic surveys, the deepened fairway now enables ultra-large container vessels (ULCVs) of up to 24,000 TEU—carrying deadweight tonnage exceeding 232,000 DWT—to transit safely in both directions under all tidal conditions, eliminating protracted tidal waiting windows that previously cost ocean carriers substantial operating expenses per port call.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>The dredging campaign, executed under strict environmental and sediment-control protocols, targeted key nautical choke points along the Vung Tau and Thi Vai river reaches.</p>\n<p>Prior to completion, vessels with operating drafts exceeding 14 meters were constrained to narrow tidal transit windows, forcing ocean liners to coordinate arrivals with high-water hours or divert excess container intake to intermediate transshipment hubs across Southeast Asia.</p>\n<p>With navigational aids recalibrated and AIS electronic fairway buoys deployed across all maritime zones, the maritime safety authority confirmed round-the-clock navigation clearance for deep-draft container carriers, as verified in official maritime safety circulars published by <a href=\"https://vietnamnet.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">VietnamNet News</a>.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Verified Operational Specifications &bull; Phase 1</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-15.5m</div>\n      <div style=\"font-size:12px; color:#64748B;\">Low-Tide Design Draft</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">350m</div>\n      <div style=\"font-size:12px; color:#64748B;\">Fairway Bottom Width</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">24,000 TEU</div>\n      <div style=\"font-size:12px; color:#64748B;\">Max Vessel Displacement</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">8.3M TEU</div>\n      <div style=\"font-size:12px; color:#64748B;\">Annual Terminal Throughput</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for shipping</h2>\n<p>For international ocean carriers and 3PL freight forwarders operating across Southeast Asia, the completion of the -15.5-meter channel marks a critical operational turning point.</p>\n<p>Previously, mega-vessels exceeding 18,000 TEU often had to restrict cargo intake or wait up to six hours for high tides before transiting inward to berths at Gemalink, TCIT, and CMIT. The elimination of tidal dependency allows liner networks—including major global container alliances—to optimize bunker consumption, increase intake by an estimated 1,200 to 1,500 TEU per vessel call, and maintain strict coastal feeder schedules.</p>\n<p>Direct services connecting Southern Vietnam to the US West Coast and Northern Europe can now operate at full commercial capacity, bypassing legacy intermediate transshipment hubs in Singapore and Tanjung Pelepas, thereby cutting end-to-end maritime transit times by 3 to 5 full days according to the <a href=\"https://vla.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Logistics Association (VLA)</a>.</p>\n\n<blockquote class=\"bbc-article-quote\" style=\"border-left:3px solid #0F172A; margin:32px 0; padding:12px 24px; font-size:20px; font-style:italic; line-height:1.5; color:#0F172A;\">\n  &ldquo;Deepening Cai Mep–Thi Vai to -15.5 meters is not merely an engineering achievement; it structurally recalibrates Vietnam's maritime competitiveness. Ocean carriers no longer need to short-ship export cargo or incur demurrage penalties waiting for high tide. Our deep-water gateway now operates on full parity with the premier container ports of Europe and East Asia.&rdquo;\n  <cite style=\"display:block; font-size:13px; font-style:normal; font-weight:700; color:#64748B; margin-top:10px;\">&mdash; Vietnam Maritime Administration Technical Directorate</cite>\n</blockquote>\n\n<h2 class=\"bbc-article-subhead\">Regional port investment and capacity developments</h2>\n<p>With Phase 1 operational, priority now shifts to the Cai Mep Ha logistics cluster, a planned 1,700-hectare multimodal inland logistics center designed to connect deep-water berths directly to Ring Road 4 and the Bien Hoa–Vung Tau expressway network.</p>\n<p>Simultaneously, inland waterway authorities are expanding green container barging links connecting Dong Nai, Binh Duong, and the Mekong Delta agricultural belt directly to Cai Mep terminals. This enables over 70% of inbound container volume to transfer via low-emission waterborne shuttles rather than congested highway corridors.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against official maritime navigation notices from the <a href=\"https://vinamarine.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Maritime Administration (Vinamarine)</a>, reporting from <a href=\"https://vietnamnet.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">VietnamNet News</a>, and industry capacity data compiled by the <a href=\"https://vla.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Logistics Association (VLA)</a>.\n</div>\n"
  },
  {
    "id": "global-container-freight-rates-surge",
    "aliasId": "transpacific-ocean-rate-benchmarks",
    "slug": "global-container-freight-rates-surge",
    "title": "Global Container Freight Rates Surge 14% on Red Sea Re-Routing and Bunker Surcharges",
    "category": "freight",
    "categoryLabel": "Freight Forwarding & 3PL",
    "categoryIcon": "fa-chart-line",
    "author": "David Chen",
    "authorRole": "Senior Container Freight Analyst",
    "authorInitial": "DC",
    "date": "19 October 2026",
    "timeAgo": "4h ago",
    "readTime": "3 min read",
    "readers": "8,180 readers",
    "isLead": true,
    "isVerified": true,
    "source": "Shanghai Containerized Freight Index (SCFI) / Xeneta",
    "sourceUrl": "https://en.sse.net.cn",
    "tags": [
      "Container Rates",
      "SCFI",
      "Red Sea Rerouting",
      "Ocean Freight",
      "3PL"
    ],
    "image": "images/hero_2.jpg",
    "imageCaption": "A container staging yard operating at peak capacity as export volumes rise. (Photo: SCFI / Maritime Intelligence)",
    "summary": "Spot rates on Shanghai–Rotterdam and Trans-Pacific freight lanes adjust upward as ocean carriers commit to Cape of Good Hope routings through Q4 2026.",
    "body": "\n<p class=\"bbc-lead-para\"><strong>The <a href=\"https://en.sse.net.cn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Shanghai Containerized Freight Index (SCFI)</a></strong> recorded a 14.2% week-on-week gain, driven by extended transit schedules around Southern Africa and escalating low-sulfur marine fuel surcharges.</p>\n\n<p>Average spot rates for 40-foot high-cube containers on Asia-to-Europe lanes reached $4,650, while Trans-Pacific East Coast rates touched $6,120 according to recent indices audited by freight analytics platform <a href=\"https://www.xeneta.com\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Xeneta</a>.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Carriers have absorbed over 1.2 million TEU of newly delivered containership capacity this year, but prolonged transit days required to navigate the Cape of Good Hope have effectively absorbed surplus vessel tonnage.</p>\n<p>With round voyages extended by 10 to 14 days, carriers face tight equipment repositioning turnaround times at key departure gates including Shanghai, Ningbo, and Cai Mep.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Benchmark Freight Rate Spot Indicators</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">$4,650</div>\n      <div style=\"font-size:12px; color:#64748B;\">Asia–Europe 40ft Spot</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">$6,120</div>\n      <div style=\"font-size:12px; color:#64748B;\">Trans-Pacific USEC Spot</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">+14.2%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Weekly SCFI Index Shift</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">+12 Days</div>\n      <div style=\"font-size:12px; color:#64748B;\">Cape Transit Extension</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for shipping operations</h2>\n<p>Logistics procurement directors are accelerating long-term contract lock-ins and exploring intermodal sea-rail options via Central Asian freight corridors to mitigate peak holiday inventory disruptions.</p>\n<p>Enterprise forwarders recommend booking cargo slots at least three weeks in advance and using digital inland feeder tracking to avoid demurrage penalties at destination ports.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against spot container pricing indices from the <a href=\"https://en.sse.net.cn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Shanghai Shipping Exchange (SCFI)</a> and market rate benchmarking data provided by <a href=\"https://www.xeneta.com\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Xeneta</a>.\n</div>\n"
  },
  {
    "id": "smart-warehousing-automation-hubs",
    "aliasId": "news-3",
    "slug": "smart-warehousing-automation-hubs",
    "title": "Binh Duong & Bac Ninh accelerate AI automated storage systems across Tier-1 logistics parks",
    "category": "warehousing",
    "categoryLabel": "Smart Warehousing",
    "categoryIcon": "fa-warehouse",
    "author": "Supply Chain Technology Desk",
    "authorRole": "Automation & Robotics Correspondent",
    "authorInitial": "ST",
    "date": "18 October 2026",
    "timeAgo": "1 day ago",
    "readTime": "5 min read",
    "readers": "6,150 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Vietnam Logistics Association (VLA) / Industrial Review",
    "sourceUrl": "https://vla.com.vn",
    "tags": [
      "Smart Warehousing",
      "Robotics",
      "AS/RS",
      "Bac Ninh",
      "Binh Duong"
    ],
    "image": "images/hero_3.jpg",
    "imageCaption": "High-density automated storage and retrieval system (AS/RS) in operation at a Tier-1 Bac Ninh distribution park.",
    "summary": "Next-generation AS/RS automated retrieval facilities cut pallet cycle times by 40% as cross-border e-commerce fulfillment surges.",
    "body": "\n<p class=\"bbc-lead-para\">Leading industrial developers and third-party logistics (3PL) operators across Binh Duong and Bac Ninh are rolling out high-density Automated Storage and Retrieval Systems (AS/RS), marking a rapid transition toward robotic material handling.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Driven by rapid growth in omnichannel electronics manufacturing and cross-border fulfillment, logistics parks have installed vertical crane AS/RS towers and fleets of Autonomous Mobile Robots (AMRs) capable of picking over 450 lines per hour with 99.98% inventory accuracy, documented in the latest automation survey by the <a href=\"https://vla.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Logistics Association (VLA)</a>.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Automation Benchmark Metrics</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">450+</div>\n      <div style=\"font-size:12px; color:#64748B;\">Lines Picked / Hour</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-60%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Floor Space Reduction</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">99.98%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Inventory Accuracy</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-35%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Energy Consumption</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for warehouse operations</h2>\n<p>Automated high-bay facilities condense storage footprints by up to 60% compared to traditional reach-truck layouts, enabling operators to offset rising industrial land costs while reducing nighttime picking energy consumption by 35%.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against industry facility audits from the <a href=\"https://vla.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Logistics Association (VLA)</a> and verified vendor documentation from regional robotic automation integrators.\n</div>\n"
  },
  {
    "id": "long-thanh-air-cargo-breakthrough",
    "aliasId": "news-4",
    "slug": "long-thanh-air-cargo-breakthrough",
    "title": "Long Thanh International Airport cargo terminal breaks ground on 1.2M ton multi-modal freight facility",
    "category": "aircargo",
    "categoryLabel": "Air Cargo Operations",
    "categoryIcon": "fa-plane-departure",
    "author": "Aviation & Logistics Desk",
    "authorRole": "Air Freight Editor",
    "authorInitial": "AL",
    "date": "17 October 2026",
    "timeAgo": "2 days ago",
    "readTime": "4 min read",
    "readers": "5,320 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Civil Aviation Authority of Vietnam (CAAV)",
    "sourceUrl": "https://caa.gov.vn",
    "tags": [
      "Air Cargo",
      "Long Thanh Airport",
      "Cold Chain",
      "Pharma Logistics",
      "Aviation"
    ],
    "image": "images/hero_2.jpg",
    "imageCaption": "Architectural model of the dedicated 1.2-million-ton air cargo terminal complex at Long Thanh International Airport.",
    "summary": "Strategic air freight hub will feature dedicated temperature-controlled cold chain pharma zones and bonded intermodal transfers.",
    "body": "\n<p class=\"bbc-lead-para\">Construction has officially commenced on the dedicated air freight village at Long Thanh International Airport, engineered to process 1.2 million metric tons of high-value cargo annually in its first operational phase.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>The <a href=\"https://caa.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Civil Aviation Authority of Vietnam (CAAV)</a> and airport development partners finalized contracts for specialized cargo apron bays capable of accommodating four Boeing 777F or Airbus A350F widebody freighters simultaneously.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Air Cargo Terminal Specifications</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">1.2M Tons</div>\n      <div style=\"font-size:12px; color:#64748B;\">Phase 1 Annual Capacity</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">4 Widebody</div>\n      <div style=\"font-size:12px; color:#64748B;\">Simultaneous B777F Bays</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">IATA CEIV</div>\n      <div style=\"font-size:12px; color:#64748B;\">Pharma Climate Standard</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">24/7</div>\n      <div style=\"font-size:12px; color:#64748B;\">Bonded Customs Apron</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for aviation logistics</h2>\n<p>The facility features IATA CEIV-certified temperature-controlled chambers dedicated to semiconductor wafers and biomedical pharmaceuticals, positioning Southern Vietnam as an aviation transshipment alternative to regional hubs in Bangkok and Kuala Lumpur.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against project filings and regulatory statements published by the <a href=\"https://caa.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Civil Aviation Authority of Vietnam (CAAV)</a> and Vietnam Airports Corporation (ACV).\n</div>\n"
  },
  {
    "id": "customs-digital-single-window-2026",
    "aliasId": "news-5",
    "slug": "customs-digital-single-window-2026",
    "title": "General Department of Vietnam Customs mandates 100% digital clearance for bonded logistics zones",
    "category": "customs",
    "categoryLabel": "Customs & Compliance",
    "categoryIcon": "fa-stamp",
    "author": "Regulatory & Compliance Bureau",
    "authorRole": "Customs Compliance Specialist",
    "authorInitial": "RC",
    "date": "16 October 2026",
    "timeAgo": "3 days ago",
    "readTime": "3 min read",
    "readers": "4,890 readers",
    "isLead": false,
    "isVerified": true,
    "source": "General Department of Vietnam Customs",
    "sourceUrl": "https://tongcuc.haiquan.gov.vn",
    "tags": [
      "Customs",
      "Paperless Clearance",
      "VNACCS",
      "Digital Border",
      "Bonded Logistics"
    ],
    "image": "images/course_4.jpg",
    "imageCaption": "Customs officers verify electronic container manifests via the automated digital single window system.",
    "summary": "Paperless customs declarations reduce border processing times to under 15 minutes across major seaport gates.",
    "body": "\n<p class=\"bbc-lead-para\">The <a href=\"https://tongcuc.haiquan.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">General Department of Vietnam Customs</a> has enacted comprehensive directives requiring complete paperless declarations across all bonded warehouses, export processing zones, and seaport checkpoints nationwide.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>The upgraded VNACCS/VCIS system now interfaces directly with marine terminal operating systems (TOS) and inland container depots via secure REST APIs, verifying customs seals and releasing container holds without physical document presentation.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Clearance Performance Indicators</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">&lt; 15 min</div>\n      <div style=\"font-size:12px; color:#64748B;\">Average Gate Dwell Time</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">100%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Paperless Single Window</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-82%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Documentation Processing Delay</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">REST APIs</div>\n      <div style=\"font-size:12px; color:#64748B;\">Direct TOS Integration</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for freight operators</h2>\n<p>Dwell times for import containers passing green and yellow customs channels have dropped from an average of 4.2 hours to under 15 minutes, significantly decreasing drayage wait times and reducing gate congestion at major terminal entrances.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified through official technical gazettes and electronic circulars issued by the <a href=\"https://tongcuc.haiquan.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">General Department of Vietnam Customs</a>.\n</div>\n"
  },
  {
    "id": "mekong-cambodia-cold-chain-logistics",
    "aliasId": "cold-chain-mekong-agri-corridors",
    "slug": "mekong-cambodia-cold-chain-logistics",
    "title": "Cambodia & Mekong Corridor Advance Cross-Border Cold Chain Logistics with Mekong–ROK Cooperation Fund",
    "category": "coldchain",
    "categoryLabel": "Cold Chain Logistics",
    "categoryIcon": "fa-snowflake",
    "author": "Agri-Logistics Desk",
    "authorRole": "Cold Chain & Perishables Specialist",
    "authorInitial": "AD",
    "date": "19 October 2026",
    "timeAgo": "5h ago",
    "readTime": "4 min read",
    "readers": "4,820 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Mekong–Republic of Korea Cooperation Fund (MKCF) / mekongrok.com",
    "sourceUrl": "https://mekongrok.com",
    "tags": [
      "Cold Chain",
      "Mekong Region",
      "Cambodia Logistics",
      "MKCF",
      "Agricultural Exports"
    ],
    "image": "images/career_banner_3.svg",
    "imageCaption": "Refrigerated cross-border container fleet inspected at the Bavet–Moc Bai international border checkpoint.",
    "summary": "A flagship capacity-building initiative funded by the Mekong–Republic of Korea Cooperation Fund (MKCF) targets border inspection bottlenecks, temperature-controlled transit, and sanitary standards along the Cambodia–Vietnam corridor.",
    "body": "\n<p class=\"bbc-lead-para\"><strong>The <a href=\"https://mekongrok.com\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Mekong–Republic of Korea Cooperation Fund (MKCF)</a></strong>, in collaboration with the General Department of Logistics (GDL) under Cambodia's Ministry of Public Works and Transport and regional Mekong partners, has initiated the operational phase of the <em>Institutional and Capacity Building for Cross-Border and Cold Chain Logistics in the Mekong Region (ICB-CCL Mekong)</em> project.</p>\n\n<p>The cross-border development initiative addresses critical post-harvest infrastructure gaps along the Southern Economic Corridor, establishing standardized temperature-monitoring protocols and cold-storage handoff procedures between Cambodian agricultural production hubs and Vietnamese export gateways.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Field consultations and technical assessments conducted across key international border gates—notably the <strong>Bavet / Moc Bai</strong> border connecting Svay Rieng and Tay Ninh, and the northern <strong>Trapeang Kreal / Nong Nok Khiene</strong> crossing—revealed that up to 28% of perishable produce suffered thermal shock during border clearance due to uncoordinated customs reefer plug-ins and lengthy document verifications.</p>\n<p>Under the MKCF-backed framework detailed on <a href=\"https://mekongrok.com\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">mekongrok.com</a>, the project delivers certified cold-chain training curricula for freight operators, introduces pre-cleared Sanitary and Phytosanitary (SPS) digital manifests, and deploys mobile IoT data loggers that transmit internal reefer temperatures continuously to cross-border inspection authorities.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">MKCF Cold-Chain Project Benchmarks</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-20°C to +4°C</div>\n      <div style=\"font-size:12px; color:#64748B;\">Guaranteed Climate Curve</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">Bavet / Moc Bai</div>\n      <div style=\"font-size:12px; color:#64748B;\">Primary Test Corridor</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">&lt; 12%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Targeted Spoilage Ceiling</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">MKCF Funded</div>\n      <div style=\"font-size:12px; color:#64748B;\">Mekong–ROK Cooperation</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for Mekong agro-exporters</h2>\n<p>For Cambodian producers of premium fresh mangoes, bananas, pepper, and inland aquaculture moving toward deep-water berths at Cai Mep or Sihanoukville Autonomous Port, uninterrupted cold chains mean shipments arrive with export-grade shelf life intact.</p>\n<p>Logistics operators adopting the certified SOPs can avoid multi-hour unloading and reloading at border staging facilities, reducing transit fuel wastage by 19% while complying with stringent food safety criteria required by East Asian and European import markets.</p>\n\n<blockquote class=\"bbc-article-quote\" style=\"border-left:3px solid #0F172A; margin:32px 0; padding:12px 24px; font-size:20px; font-style:italic; line-height:1.5; color:#0F172A;\">\n  &ldquo;Cross-border cold chain integration is the single most vital catalyst for agricultural value addition across the Mekong subregion. Standardized temperature controls and streamlined SPS border checks ensure our farmers' hard work reaches global buyers in prime condition.&rdquo;\n  <cite style=\"display:block; font-size:13px; font-style:normal; font-weight:700; color:#64748B; margin-top:10px;\">&mdash; Mekong Regional Logistics Integration Working Group</cite>\n</blockquote>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against reporting and project milestones published by the <a href=\"https://mekongrok.com\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Mekong–Republic of Korea Cooperation Fund (MKCF)</a>, Mekong Institute (MI) project archives, and the General Department of Logistics under Cambodia's Ministry of Public Works and Transport (<a href=\"https://www.mpwt.gov.kh\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">mpwt.gov.kh</a>).\n</div>\n"
  },
  {
    "id": "fleet-telematics-weigh-in-motion",
    "aliasId": "news-7",
    "slug": "fleet-telematics-weigh-in-motion",
    "title": "Vietnam Highway Expressways mandate real-time telematics and digital weigh-in-motion for heavy haulers",
    "category": "trucking",
    "categoryLabel": "Fleet & Trucking",
    "categoryIcon": "fa-truck-front",
    "author": "Fleet & Intermodal Desk",
    "authorRole": "Ground Transport Editor",
    "authorInitial": "FT",
    "date": "14 October 2026",
    "timeAgo": "5 days ago",
    "readTime": "3 min read",
    "readers": "4,120 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Department for Roads of Vietnam (DRVN)",
    "sourceUrl": "https://drvn.gov.vn",
    "tags": [
      "Fleet Telematics",
      "Weigh-in-Motion",
      "Expressways",
      "Heavy Haulage",
      "Highway Safety"
    ],
    "image": "images/today_4.jpg",
    "imageCaption": "Heavy container tractor equipped with electronic telematics passing an overhead weigh-in-motion sensor gantry.",
    "summary": "Smart fleet dispatch sensors curb overloaded drayage trucks and cut transit diesel emissions along the North-South corridor.",
    "body": "\n<p class=\"bbc-lead-para\">The <a href=\"https://drvn.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Department for Roads of Vietnam (DRVN)</a> has completed the nationwide installation of high-speed weigh-in-motion (WIM) sensors and automatic license plate recognition cameras across all major expressways connecting key manufacturing zones.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Commercial drayage fleets now broadcast real-time GPS positioning, axle weights, and driver duty hours directly to the unified transport oversight network without slowing down at toll booths.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Highway Telematics Metrics</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">0 sec</div>\n      <div style=\"font-size:12px; color:#64748B;\">Highway Weighing Stop Delay</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-14%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Fuel Idling Consumption</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">99.4%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Axle Weight Measurement Accuracy</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">100%</div>\n      <div style=\"font-size:12px; color:#64748B;\">North-South Gantry Coverage</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for carrier operations</h2>\n<p>Compliant carriers with electronic weigh-clearance credentials experience zero highway weighing delays, reducing fuel idling consumption by 14% and eliminating road surface degradation caused by unauthorized overloaded haulage.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against executive technical standards issued by the <a href=\"https://drvn.gov.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Department for Roads of Vietnam (DRVN)</a> and the Ministry of Transport.\n</div>\n"
  },
  {
    "id": "asean-cross-border-rail-link",
    "aliasId": "news-8",
    "slug": "asean-cross-border-rail-link",
    "title": "ASEAN cross-border freight train link connects Yen Vien rail terminal directly to regional dry ports",
    "category": "supplychain",
    "categoryLabel": "Supply Chain Management",
    "categoryIcon": "fa-network-wired",
    "author": "Cross-Border Rail Bureau",
    "authorRole": "Intermodal Rail Logistics Lead",
    "authorInitial": "CR",
    "date": "12 October 2026",
    "timeAgo": "7 days ago",
    "readTime": "4 min read",
    "readers": "5,640 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Vietnam Railways Corporation (VNR)",
    "sourceUrl": "https://www.vr.com.vn",
    "tags": [
      "Rail Freight",
      "Intermodal",
      "Yen Vien",
      "ASEAN Freight Logistics",
      "Supply Chain"
    ],
    "image": "images/course_2.jpg",
    "imageCaption": "Container block train preparing for departure on the direct international rail freight line.",
    "summary": "Direct rail freight service delivers 48-hour scheduled transit, offering shippers an economic alternative to air cargo.",
    "body": "\n<p class=\"bbc-lead-para\"><a href=\"https://www.vr.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Vietnam Railways Corporation (VNR)</a> has expanded its international intermodal container block service from Hanoi's Yen Vien hub, providing seamless overland transit into neighboring Southeast Asian markets and southern industrial hubs.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>The daily scheduled container rail service operates on unified transit documentation, enabling customs inspections to take place at dry port terminals rather than causing border delays at railway track crossings.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Intermodal Rail Transit Metrics</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">48 Hours</div>\n      <div style=\"font-size:12px; color:#64748B;\">Scheduled Corridor Transit</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-70%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Cost vs. Air Freight</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">99.2%</div>\n      <div style=\"font-size:12px; color:#64748B;\">On-Time Departure Reliability</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">Daily</div>\n      <div style=\"font-size:12px; color:#64748B;\">Scheduled Block Train Frequency</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for shippers</h2>\n<p>Shippers moving high-tech electronics, telecommunications gear, and processed goods now access a 48-hour door-to-door transit schedule at approximately 30% of the cost of dedicated air cargo freighters, creating resilient supply chain redundancy against maritime weather fluctuations.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against intermodal freight schedules and tariff bulletins from <a href=\"https://www.vr.com.vn\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Vietnam Railways Corporation (VNR)</a>.\n</div>\n"
  },
  {
    "id": "un-border-security-frameworks",
    "aliasId": "world-news-1",
    "slug": "un-border-security-frameworks",
    "title": "UN General Assembly Convenes Emergency Session on European Border Security Frameworks",
    "category": "world",
    "categoryLabel": "Diplomacy & World Security",
    "categoryIcon": "fa-globe",
    "author": "Helena Vance",
    "authorRole": "Diplomatic Affairs Bureau Chief",
    "authorInitial": "HV",
    "date": "19 October 2026",
    "timeAgo": "3h ago",
    "readTime": "5 min read",
    "readers": "12,450 readers",
    "isLead": false,
    "isVerified": true,
    "source": "United Nations Information Service",
    "sourceUrl": "https://www.un.org",
    "tags": [
      "United Nations",
      "Border Security",
      "European Union",
      "Diplomacy",
      "International Law"
    ],
    "image": "images/hero_2.jpg",
    "imageCaption": "Delegates gather at the United Nations General Assembly Hall for the opening of the emergency security session.",
    "summary": "Special envoys debate revised border oversight protocols as multilateral agencies urge harmonized humanitarian safeguards and commercial commerce continuity.",
    "body": "\n<p class=\"bbc-lead-para\"><strong>The <a href=\"https://www.un.org\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">United Nations General Assembly</a></strong> has opened an emergency consultative session in Geneva to address heightened border monitoring measures across Eastern European transit corridors.</p>\n\n<p>The session brings together ministers from 42 member states to formulate a unified resolution that balances national border sovereignty with the preservation of critical humanitarian corridors and multimodal freight corridors connecting Eurasian shipping arteries.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Recent shifts in regional border monitoring protocols caused secondary commercial delays of up to 36 hours at intermodal rail terminals and customs checkposts. Multilateral rapporteurs emphasized that uncoordinated checkpoint closures inadvertently strain logistics supply lines for medical shipments and food supplies.</p>\n<p>The draft resolution proposes a synchronized digital credential mechanism to allow freight convoys carrying certified humanitarian and essential consumer cargo to clear bilateral checkpoints under an expedited customs transit treaty.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">UN Emergency Session Framework</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">42 States</div>\n      <div style=\"font-size:12px; color:#64748B;\">Participating Delegations</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">72 Hours</div>\n      <div style=\"font-size:12px; color:#64748B;\">Resolution Debate Window</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">100%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Humanitarian Corridor Protection</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">Geneva</div>\n      <div style=\"font-size:12px; color:#64748B;\">Plenary Host City</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">Strategic implications for international commerce</h2>\n<p>commerce diplomats and cross-border transport federations noted that clear international guidelines will restore certainty to long-haul rail freight schedules, ensuring that standard commercial cargo does not suffer indeterminate delays at terrestrial borders.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against official press briefings from the <a href=\"https://www.un.org\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">United Nations Information Service</a> and the UN Office for the Coordination of Humanitarian Affairs (OCHA).\n</div>\n"
  },
  {
    "id": "north-sea-energy-grid-interconnection",
    "aliasId": "world-news-2",
    "slug": "north-sea-energy-grid-interconnection",
    "title": "European Union Approves Landmark North Sea Grid Interconnection Pact",
    "category": "world",
    "categoryLabel": "Clean Energy & Climate Transition",
    "categoryIcon": "fa-bolt",
    "author": "Marcus Lindqvist",
    "authorRole": "Energy Transition & Infrastructure Reporter",
    "authorInitial": "ML",
    "date": "19 October 2026",
    "timeAgo": "5h ago",
    "readTime": "4 min read",
    "readers": "9,820 readers",
    "isLead": false,
    "isVerified": true,
    "source": "European Commission Directorate-General for Energy",
    "sourceUrl": "https://ec.europa.eu",
    "tags": [
      "North Sea",
      "Renewable Energy",
      "Offshore Wind",
      "Grid Interconnection",
      "European Union"
    ],
    "image": "images/hero_3.jpg",
    "imageCaption": "Offshore wind turbines connected to high-voltage direct current (HVDC) converter platforms in the North Sea basin.",
    "summary": "Nine coastal nations sign binding cross-border energy framework to link 120 GW of offshore wind capacity into a unified transmission network by 2030.",
    "body": "\n<p class=\"bbc-lead-para\">Ministers from nine European coastal states and the <a href=\"https://ec.europa.eu\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">European Commission</a> have ratified the North Sea Offshore Grid Treaty, unlocking a shared regulatory architecture for multi-terminal high-voltage direct current (HVDC) transmission lines.</p>\n\n<p>The landmark accord establishes joint cross-border bidding zones, mutual grid balancing agreements, and common procurement standards for underwater transmission cables spanning over 4,500 kilometers of seabed.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Previously, individual national offshore wind installations connected solely to their respective domestic land grids via dedicated radial cables, creating transmission bottlenecks and curtailing surplus electricity during peak storm cycles.</p>\n<p>The new unified offshore transmission framework allows wind electricity generated in the Belgian or Dutch sectors to transmit directly to industrial demand centers in Germany or the UK, maximizing renewable grid utilization and lowering wholesale power volatility.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">North Sea Grid Treaty Key Targets</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">120 GW</div>\n      <div style=\"font-size:12px; color:#64748B;\">Target Wind Capacity by 2030</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">9 Nations</div>\n      <div style=\"font-size:12px; color:#64748B;\">Signatory Coastal States</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">4,500 km</div>\n      <div style=\"font-size:12px; color:#64748B;\">Interconnected Subsea HVDC</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-28%</div>\n      <div style=\"font-size:12px; color:#64748B;\">Target Peak Power Volatility</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">Industrial and maritime logistics impact</h2>\n<p>Shipbuilding yards and heavy-lift installation vessel operators across Rotterdam, Esbjerg, and Bremerhaven report record forward orders for specialized cable-laying vessels and floating offshore substation platforms.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against official treaty communiqués from the <a href=\"https://ec.europa.eu\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">European Commission Directorate-General for Energy</a> and the North Seas Energy Cooperation (NSEC).\n</div>\n"
  },
  {
    "id": "global-central-banks-monetary-trajectory",
    "aliasId": "world-news-3",
    "slug": "global-central-banks-monetary-trajectory",
    "title": "Central Banks Signal Coordinated Trajectory as Core Inflation Moderates",
    "category": "world",
    "categoryLabel": "Global Markets & Monetary Stability",
    "categoryIcon": "fa-coins",
    "author": "Dr. Aris Thorne",
    "authorRole": "Chief Macroeconomic Strategist",
    "authorInitial": "AT",
    "date": "19 October 2026",
    "timeAgo": "6h ago",
    "readTime": "4 min read",
    "readers": "11,200 readers",
    "isLead": false,
    "isVerified": true,
    "source": "Bank for International Settlements (BIS) / OECD",
    "sourceUrl": "https://www.bis.org",
    "tags": [
      "Central Banks",
      "Monetary Policy",
      "Inflation",
      "Macroeconomics",
      "Global Shipping Commerce"
    ],
    "image": "images/hero_1.jpg",
    "imageCaption": "Finance ministers and central bank governors convene at the international macroeconomic policy summit.",
    "summary": "Synchronized monetary easing expectations provide welcome predictability for corporate supply chain capital expenditures and commerce finance credit lines.",
    "body": "\n<p class=\"bbc-lead-para\">Quarterly economic statements published across major central banks—including the Federal Reserve, the European Central Bank, and the Bank of England—signal an orderly transition toward monetary accommodation as global core inflation rates descend within the 2.1% to 2.4% corridor, according to the <a href=\"https://www.bis.org\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline; font-weight:600;\">Bank for International Settlements (BIS)</a>.</p>\n\n<p>The alignment in rate trajectories removes foreign exchange volatility that had previously burdened multinational supply chains and increased currency hedging expenses for trans-Pacific and intra-Asian freight contracts.</p>\n\n<h2 class=\"bbc-article-subhead\">What happened?</h2>\n<p>Easing pressure on wholesale energy inputs and normalizing container shipping freight rates have tempered upstream Producer Price Indices (PPI) across key export-manufacturing economies.</p>\n<p>With terminal policy rates easing, commercial banks have begun widening letter of credit (LC) availability and lowering working-capital borrowing spreads for enterprise freight forwarders and logistics infrastructure developers.</p>\n\n<div class=\"bbc-stat-card\" style=\"background:#F8FAFC; border-left:4px solid #0044CC; padding:20px 24px; border-radius:4px; margin:28px 0;\">\n  <span style=\"font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; color:#0044CC; display:block; margin-bottom:8px;\">Macroeconomic Stabilization Indicators</span>\n  <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:16px;\">\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">2.1% - 2.4%</div>\n      <div style=\"font-size:12px; color:#64748B;\">G10 Core Inflation Range</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">-45 bps</div>\n      <div style=\"font-size:12px; color:#64748B;\">Avg. commerce Credit Spread Shift</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">+8.4%</div>\n      <div style=\"font-size:12px; color:#64748B;\">commerce Finance LC Volume Growth</div>\n    </div>\n    <div>\n      <div style=\"font-size:24px; font-weight:900; color:#0F172A;\">Synchronized</div>\n      <div style=\"font-size:12px; color:#64748B;\">Central Bank Policy Stance</div>\n    </div>\n  </div>\n</div>\n\n<h2 class=\"bbc-article-subhead\">What it means for supply chain investments</h2>\n<p>Corporate CFOs are re-opening capital expenditure allocations for fleet renewal, warehouse robotics, and port logistics software. Lower borrowing costs provide the necessary runway for long-term supply chain resilience programs through 2027.</p>\n\n<div class=\"bbc-source-strip\" style=\"background:#F1F5F9; padding:14px 18px; border-radius:4px; font-size:12.5px; color:#475569; margin-top:36px; line-height:1.6;\">\n  <strong>Sources &amp; Fact Verification:</strong> Verified against quarterly macroeconomic bulletins from the <a href=\"https://www.bis.org\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#0044CC; text-decoration:underline;\">Bank for International Settlements (BIS)</a> and the OECD commerce and Financial Statistics Directorate.\n</div>\n"
  }
];

function getNewsArticles() {
  try {
    const raw = localStorage.getItem('thesandbox_news_articles_v6');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
    }
  } catch(e) {}
  try {
    localStorage.setItem('thesandbox_news_articles_v6', JSON.stringify(defaultNewsArticles));
  } catch(e) {}
  return defaultNewsArticles;
}

function saveNewsArticles(list) {
  try {
    localStorage.setItem('thesandbox_news_articles_v6', JSON.stringify(list));
  } catch(e) {}
}

window.openNewsPostModal = function() {
  const modal = document.getElementById('news-post-modal');
  if (modal) modal.classList.add('show');
};

window.closeNewsPostModal = function() {
  const modal = document.getElementById('news-post-modal');
  if (modal) modal.classList.remove('show');
};

window.fillNewsTemplate = function() {
  const titleInput = document.getElementById('news-post-title');
  const authorInput = document.getElementById('news-post-author');
  const summaryInput = document.getElementById('news-post-summary');
  const bodyInput = document.getElementById('news-post-body');

  if (titleInput) titleInput.value = 'Long Thanh Air Freight Terminal Reaches Structural Milestone Ahead of 2027 Schedule';
  if (authorInput) authorInput.value = 'Aviation & Multimodal Desk';
  if (summaryInput) summaryInput.value = 'High-velocity air cargo apron achieves 75% structural concrete completion as automated cold-storage vaults begin mechanical installation.';
  if (bodyInput) bodyInput.value = 'Phase 1 construction of the Long Thanh International Airport cargo complex reached its main structural topping-out today, three weeks ahead of schedule.\n\nEngineers have begun installing climate-controlled high-bay racking systems designed to process pharmaceutical vaccines and semiconductor equipment without breaking cold chain.\n\nDirect highway connector ramps will route intermodal drayage from industrial hubs in Dong Nai and Binh Duong directly to customs security checkpoints.';
  showToast('🪄 Logistics news dispatch template inserted!');
};

window.handleNewsSubmit = function(e) {
  e.preventDefault();

  const title = document.getElementById('news-post-title')?.value.trim();
  const author = document.getElementById('news-post-author')?.value.trim();
  const authorRole = document.getElementById('news-post-author-role')?.value.trim() || 'Logistics Operations Correspondent';
  const category = document.getElementById('news-post-category')?.value || 'maritime';
  const readTime = document.getElementById('news-post-read-time')?.value || '4 min read';
  const summary = document.getElementById('news-post-summary')?.value.trim();
  const body = document.getElementById('news-post-body')?.value.trim();
  const isDraft = document.getElementById('news-post-is-draft')?.checked || false;

  if (!title || !author || !summary || !body) {
    alert('Please fill out all required fields before publishing your dispatch.');
    return;
  }

  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

  const newArticle = {
    id: 'news-' + Date.now(),
    slug: slug,
    title: title,
    category: category,
    categoryLabel: category.charAt(0).toUpperCase() + category.slice(1) + ' Logistics',
    categoryIcon: 'fa-newspaper',
    author: author,
    authorRole: authorRole,
    authorInitial: author.split(' ').map(n=>n[0]).slice(0,2).join('').toUpperCase(),
    date: 'Just now',
    timeAgo: 'Just now',
    image: 'images/hero_1.jpg',
    imageCaption: title + ' (Photo: Verified Editorial Wire)',
    readTime: readTime,
    readers: '1 reader',
    isLead: false,
    isVerified: true,
    isDraft: isDraft,
    summary: summary,
    body: body
  };

  const articles = getNewsArticles();
  articles.unshift(newArticle);
  saveNewsArticles(articles);

  closeNewsPostModal();
  document.getElementById('news-post-form')?.reset();

  renderNewsFeed();
  showToast(`📰 Article "${title}" has been published live!`);
};

// DIRECT DETAIL ROUTING: Always navigate straight to dedicated article page, NEVER show a popup modal!
window.openArticleModal = function(id) {
  const list = getNewsArticles();
  const article = list.find(a => a.id === id || a.slug === id || a.aliasId === id);
  const target = article ? (article.slug || article.id) : id;
  window.location.href = `news-detail.html?slug=${encodeURIComponent(target)}`;
};

window.closeArticleModal = function() {
  const modal = document.getElementById('news-article-read-modal');
  if (modal) modal.classList.remove('show');
};

function renderNewsFeed() {
  const container = document.getElementById('news-feed-container');
  if (!container) return;

  const articles = getNewsArticles().filter(a => !a.isDraft && a.status !== 'draft');
  let filtered = articles;
  if (currentNewsCategory !== 'all') {
    filtered = articles.filter(a => {
      if (currentNewsCategory === 'world' || currentNewsCategory === 'maritime') {
        return a.category === 'maritime' || a.category === 'ports';
      }
      if (currentNewsCategory === 'politics' || currentNewsCategory === 'customs') {
        return a.category === 'customs';
      }
      if (currentNewsCategory === 'business' || currentNewsCategory === 'forwarding') {
        return a.category === 'forwarding' || a.category === 'freight' || a.category === 'supplychain';
      }
      if (currentNewsCategory === 'tech' || currentNewsCategory === 'warehousing') {
        return a.category === 'warehousing' || a.category === 'robotics';
      }
      if (currentNewsCategory === 'coldchain') {
        return a.category === 'coldchain';
      }
      if (currentNewsCategory === 'trucking') {
        return a.category === 'trucking';
      }
      if (currentNewsCategory === 'aircargo') {
        return a.category === 'aircargo';
      }
      return a.category === currentNewsCategory;
    });
  }

  const categoryTitles = {
    all: 'Latest Dispatches & Continuous Coverage',
    maritime: 'Maritime & Port Logistics',
    forwarding: 'Freight Forwarding & 3PL Corridors',
    warehousing: 'Smart Warehousing & Robotics',
    customs: 'Customs, Regulatory & Compliance',
    coldchain: 'Cold Chain & Agri-Logistics',
    trucking: 'Fleet, Drayage & Trucking',
    aircargo: 'Air Cargo Operations & Freight',
    supplychain: 'Supply Chain Management'
  };

  const currentTitle = categoryTitles[currentNewsCategory] || 'Section Coverage';

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="padding: 40px 20px; text-align: center; background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 4px; margin: 24px 0;">
        <i class="fa-regular fa-newspaper" style="font-size: 32px; color: #94A3B8; margin-bottom: 12px; display:block;"></i>
        <h3 style="font-size: 16px; font-weight: 800; color: #0F172A; margin: 0 0 6px;">No Editorial Dispatches in this Section</h3>
        <p style="font-size: 13px; color: #64748B; margin: 0 0 16px;">There are currently no published dispatches filed under this beat.</p>
        <button type="button" class="btn-publish-news" onclick="openNewsPostModal();" style="display:inline-flex; align-items:center; gap:8px; background:#111827; color:#FFFFFF; font-weight:700; font-size:13px; padding:9px 18px; border-radius:4px; border:none; cursor:pointer;">
          <i class="fa-solid fa-pen-nib"></i> File a Dispatch
        </button>
      </div>
    `;
    return;
  }

  let html = `
    <div class="editorial-feed-stream" style="margin-top: 8px;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; margin: 16px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #0F172A;">
        <h3 style="font-size:14px; font-weight:900; color:#0F172A; text-transform:uppercase; letter-spacing:0.6px; margin:0;">
          ${currentTitle}
        </h3>
        <span style="font-size:12px; font-weight:700; color:#64748B;">${filtered.length} Dispatches</span>
      </div>

      <div style="display:flex; flex-direction:column;">
        ${filtered.map(story => `
          <article class="editorial-stream-article" style="display:flex; gap:20px; padding:18px 12px; border-bottom:1px solid #E2E8F0; align-items:flex-start; border-radius:4px; cursor:pointer;" onclick="window.location.href='news-detail.html?slug=${story.slug || story.id}';">
            <div style="flex:1; min-width:0;">
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:11px; font-weight:800; letter-spacing:0.6px; text-transform:uppercase;">
                ${story.isNew ? '<span style="background:#0044CC; color:#FFFFFF; padding:2px 6px; border-radius:2px; font-size:9.5px;">VERIFIED</span>' : ''}
                <span style="color:#0044CC;"><i class="fa-solid ${story.categoryIcon || 'fa-tag'}"></i> ${story.categoryLabel || story.category}</span>
                <span style="color:#94A3B8;">&bull;</span>
                <span style="color:#64748B;">${story.timeAgo || story.date}</span>
              </div>
              <h4 style="font-size:18px; font-weight:800; color:#0F172A; line-height:1.35; margin:0 0 8px;">
                <a href="news-detail.html?slug=${story.slug || story.id}" style="color:#0F172A; text-decoration:none;" onmouseover="this.style.color='#0044CC'; this.style.textDecoration='underline';" onmouseout="this.style.color='#0F172A'; this.style.textDecoration='none';">
                  ${story.title}
                </a>
              </h4>
              <p style="font-size:14px; color:#475569; line-height:1.6; margin:0 0 12px;">
                ${story.summary}
              </p>
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:12px; color:#64748B; flex-wrap:wrap; gap:8px;">
                <span>By <strong>${story.author}</strong>${story.source ? ` &bull; <em>${story.source}</em>` : ''}</span>
                <div style="display:flex; align-items:center; gap:12px;">
                  <span><i class="fa-regular fa-clock"></i> ${story.readTime || '4 min read'}</span>
                  <a href="news-detail.html?slug=${story.slug || story.id}" style="background:#0F172A; color:#FFFFFF; padding:6px 14px; border-radius:4px; font-size:12px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:5px;" onclick="event.stopPropagation();">
                    Read Full Story &rarr;
                  </a>
                </div>
              </div>
            </div>
            ${story.image ? `
              <div class="editorial-stream-thumb" style="flex-shrink:0; width:160px; overflow:hidden; border-radius:4px;">
                <a href="news-detail.html?slug=${story.slug || story.id}" onclick="event.stopPropagation();">
                  <img src="${story.image}" alt="${story.title}" style="width:160px; height:105px; object-fit:cover; display:block;" onerror="this.parentElement.style.display='none';">
                </a>
              </div>
            ` : ''}
          </article>
        `).join('')}
      </div>
    </div>
  `;

  container.innerHTML = html;
}

window.filterNewsByCategory = function(category, btn) {
  currentNewsCategory = category;
  document.querySelectorAll('.editorial-tab-btn, .news-pill-btn, .news-filter-tab, .job-chip-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderNewsFeed();
  const anchor = document.getElementById('news-feed-container');
  if (anchor && category !== 'all') {
    anchor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('news-feed-container')) {
    renderNewsFeed();
  }
});

/* ==========================================================================
   21. USER PROFILE & ACCOUNT MENU CONTROLLER (EXACT USER SPEC)
   ========================================================================== */

function getAuthUser() {
  try {
    const raw = localStorage.getItem('thesandbox_auth_user');
    return raw ? JSON.parse(raw) : null;
  } catch(e) {
    return null;
  }
}

function setAuthUser(user) {
  try {
    if (user) {
      localStorage.setItem('thesandbox_auth_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('thesandbox_auth_user');
    }
  } catch(e) {}
  updateAuthHeaderUI();
  renderUserProfileDropdown();
}

function getSavedJobIds() {
  try {
    const raw = localStorage.getItem('thesandbox_saved_jobs') || localStorage.getItem('sandbox_saved_jobs');
    return raw ? JSON.parse(raw) : ['job-1', 'job-3'];
  } catch(e) {
    return ['job-1', 'job-3'];
  }
}

window.toggleUserProfileDropdown = function(e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const wrap = document.getElementById('user-profile-menu-wrap');
  const btn = document.getElementById('btn-user-profile-menu');
  if (!wrap) return;

  const isOpen = wrap.classList.contains('open');
  if (isOpen) {
    wrap.classList.remove('open');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  } else {
    // Close other dropdowns like language dropdown
    document.querySelectorAll('.lang-dropdown-wrap.open').forEach(el => el.classList.remove('open'));
    wrap.classList.add('open');
    if (btn) btn.setAttribute('aria-expanded', 'true');
    renderUserProfileDropdown();
  }
};

window.closeUserProfileDropdown = function() {
  const wrap = document.getElementById('user-profile-menu-wrap');
  const btn = document.getElementById('btn-user-profile-menu');
  if (wrap && wrap.classList.contains('open')) {
    wrap.classList.remove('open');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }
};

function renderUserProfileDropdown() {
  const dropdown = document.getElementById('user-profile-dropdown');
  if (!dropdown) return;

  const user = getAuthUser();
  const savedIds = getSavedJobIds();
  const savedCount = savedIds.length;

  if (!user) {
    // Visitor / Not Signed In State (Exact user spec)
    dropdown.innerHTML = `
      <div class="profile-menu-header">
        <div class="profile-menu-avatar-large">
          <span>T</span>
        </div>
        <div class="profile-menu-header-text">
          <h4 class="profile-menu-title">Welcome to The SandBox</h4>
          <p class="profile-menu-sub">Sign in to access your account</p>
        </div>
      </div>

      <div class="profile-menu-cta-row">
        <button type="button" class="btn-profile-signin" onclick="window.location.href='login.html';">
          <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In
        </button>
        <button type="button" class="btn-profile-create" onclick="window.location.href='signup.html';">
          Create Account
        </button>
      </div>

      <div class="profile-menu-divider"></div>

      <div class="profile-menu-items-list">
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('admin');">
          <span class="profile-menu-item-icon" style="color:#0044CC;"><i class="fa-solid fa-crown"></i></span>
          <span class="profile-menu-item-text">Admin &amp; Publisher Studio</span>
          <span class="profile-menu-item-badge" style="background:#EFF6FF; color:#0044CC; font-weight:800;">Tiptap</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('profile');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-user-tie"></i></span>
          <span class="profile-menu-item-text">Candidate Profile</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('saved-jobs');">
          <span class="profile-menu-item-icon"><i class="fa-regular fa-bookmark"></i></span>
          <span class="profile-menu-item-text">Saved Jobs</span>
          <span class="profile-menu-item-count" id="dropdown-saved-count">${savedCount}</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('employer');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-building"></i></span>
          <span class="profile-menu-item-text">Employer Dashboard</span>
          <span class="profile-menu-item-badge">Enterprise</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('help');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-circle-question"></i></span>
          <span class="profile-menu-item-text">Help &amp; Support</span>
        </button>
      </div>
    `;
  } else {
    // Signed-In State (Exact user spec: name, account settings, saved jobs, sign out; Employer Dashboard only if employer access)
    const isEmployer = user.role === 'employer' || user.hasEmployerAccess;
    const initial = user.initial || (user.name ? user.name.split(' ').map(n=>n[0]).slice(0,2).join('') : 'T');

    dropdown.innerHTML = `
      <div class="profile-menu-header">
        <div class="profile-menu-avatar-large signed-in">
          <span>${initial}</span>
        </div>
        <div class="profile-menu-header-text">
          <h4 class="profile-menu-title">${user.name}</h4>
          <p class="profile-menu-email">${user.email}</p>
          <span class="profile-menu-role-tag"><i class="fa-solid fa-shield-check"></i> ${isEmployer ? 'Verified Recruiter' : 'Logistics Specialist'}</span>
        </div>
      </div>

      <div class="profile-menu-divider"></div>

      <div class="profile-menu-items-list">
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('admin');">
          <span class="profile-menu-item-icon" style="color:#0044CC;"><i class="fa-solid fa-crown"></i></span>
          <span class="profile-menu-item-text">Admin &amp; Publisher Studio</span>
          <span class="profile-menu-item-badge" style="background:#EFF6FF; color:#0044CC; font-weight:800;">Tiptap</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('profile');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-id-card"></i></span>
          <span class="profile-menu-item-text">Account Settings &amp; Profile</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('applications');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-file-lines"></i></span>
          <span class="profile-menu-item-text">My Applications</span>
          <span class="profile-menu-item-count" id="profile-menu-apps-count">1</span>
        </button>
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('saved-jobs');">
          <span class="profile-menu-item-icon"><i class="fa-regular fa-bookmark"></i></span>
          <span class="profile-menu-item-text">Saved Jobs</span>
          <span class="profile-menu-item-count" id="dropdown-saved-count">${savedCount}</span>
        </button>
        ${isEmployer ? `
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('employer');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-chart-line"></i></span>
          <span class="profile-menu-item-text">Employer ATS Dashboard</span>
          <span class="profile-menu-item-badge">B2B</span>
        </button>
        ` : ''}
        <button type="button" class="profile-menu-item" onclick="handleAccountMenuAction('help');">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-circle-question"></i></span>
          <span class="profile-menu-item-text">Help &amp; Support</span>
        </button>

        <div class="profile-menu-divider"></div>

        <button type="button" class="profile-menu-item sign-out-item" onclick="closeUserProfileDropdown(); signOutUser();">
          <span class="profile-menu-item-icon"><i class="fa-solid fa-right-from-bracket"></i></span>
          <span class="profile-menu-item-text">Sign Out</span>
        </button>
      </div>
    `;
  }
}

function updateAuthHeaderUI() {
  const user = getAuthUser();
  const avatarSpan = document.getElementById('header-avatar-initial');
  const avatarBtn = document.getElementById('btn-user-profile-menu');
  const headerLoginBtn = document.getElementById('btn-header-login');
  const topStripLogin = document.querySelector('.chinajob-btn-login');

  if (avatarSpan) {
    if (user) {
      const initial = user.initial || (user.name ? user.name.split(' ').map(n=>n[0]).slice(0,2).join('') : 'T');
      avatarSpan.textContent = initial;
      if (avatarBtn) {
        avatarBtn.style.display = 'flex';
        avatarBtn.classList.add('signed-in');
      }
      if (headerLoginBtn) {
        headerLoginBtn.style.display = 'none';
      }
    } else {
      avatarSpan.textContent = 'T';
      if (avatarBtn) avatarBtn.classList.remove('signed-in');
      if (headerLoginBtn) {
        headerLoginBtn.style.display = 'inline-flex';
      }
    }
  }

  if (topStripLogin) {
    if (user) {
      topStripLogin.innerHTML = '<i class="fa-solid fa-right-from-bracket"></i> Sign Out';
      topStripLogin.setAttribute('onclick', 'signOutUser(); return false;');
    } else {
      topStripLogin.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In';
      topStripLogin.setAttribute('onclick', "openAuthModal('signin'); return false;");
    }
  }
}

window.handleAccountMenuAction = function(action) {
  closeUserProfileDropdown();
  const user = getAuthUser();

  if (action === 'admin') {
    window.location.href = 'admin.html';
  } else if (action === 'profile') {
    window.location.href = 'settings.html';
  } else if (action === 'saved-jobs') {
    window.location.href = 'candidate-dashboard.html?tab=saved';
  } else if (action === 'employer') {
    window.location.href = 'employer-ats.html';
  } else if (action === 'applications') {
    window.location.href = 'candidate-dashboard.html?tab=applications';
  } else if (action === 'help') {
    window.location.href = 'help.html';
  }
};

window.signOutUser = function() {
  setAuthUser(null);
  showToast('You have signed out of The SandBox.');
};


window.continueWithGoogle = function() {
  const googleUser = {
    name: 'Nguyen Minh Tri',
    email: 'minh.tri@enterprise3pl.vn',
    role: 'candidate',
    initial: 'NT',
    hasEmployerAccess: false
  };
  setAuthUser(googleUser);
  closeAuthModal();
  showToast('Signed in with Google as Nguyen Minh Tri (Logistics Specialist)');
};

window.toggleAuthPasswordVisibility = function(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = 'Hide';
  } else {
    input.type = 'password';
    btn.textContent = 'Show';
  }
};

window.quickDemoLogin = function(role) {
  if (role === 'candidate') {
    const candidateUser = {
      name: 'Nguyen Minh Tri',
      email: 'minh.tri@enterprise3pl.vn',
      role: 'candidate',
      initial: 'NT',
      hasEmployerAccess: false
    };
    setAuthUser(candidateUser);
    closeAuthModal();
    showToast('Signed in as Candidate: Nguyen Minh Tri (Logistics Specialist)');
  } else if (role === 'employer') {
    const employerUser = {
      name: 'Viconship Talent Desk',
      email: 'recruitment@viconship.com',
      role: 'employer',
      initial: 'VL',
      hasEmployerAccess: true
    };
    setAuthUser(employerUser);
    closeAuthModal();
    showToast('Signed in as Employer: Viconship Logistics (Enterprise 3PL)');
  }
};

window.openAuthModal = function(tab) {
  const modal = document.getElementById('modal-auth-dialog');
  if (!modal) return;
  switchAuthTab(tab || 'signin');
  modal.classList.add('show');
};

window.closeAuthModal = function() {
  const modal = document.getElementById('modal-auth-dialog');
  if (modal) modal.classList.remove('show');
};

window.switchAuthTab = function(tab) {
  const btnIn = document.getElementById('tab-btn-signin');
  const btnReg = document.getElementById('tab-btn-register');
  const paneIn = document.getElementById('auth-pane-signin');
  const paneReg = document.getElementById('auth-pane-register');

  if (tab === 'register') {
    if (btnIn) btnIn.classList.remove('active');
    if (btnReg) btnReg.classList.add('active');
    if (paneIn) paneIn.style.display = 'none';
    if (paneReg) paneReg.style.display = 'block';
  } else {
    if (btnIn) btnIn.classList.add('active');
    if (btnReg) btnReg.classList.remove('active');
    if (paneIn) paneIn.style.display = 'block';
    if (paneReg) paneReg.style.display = 'none';
  }
};

window.handleAuthFormSubmit = function(e, type) {
  e.preventDefault();
  if (type === 'signin') {
    const email = document.getElementById('auth-signin-email')?.value.trim() || 'user@thesandbox.vn';
    const isEmp = email.includes('viconship') || email.includes('recruitment') || email.includes('hr');
    const user = {
      name: email.split('@')[0].replace('.', ' ').replace(/(^|\s)\S/g, l => l.toUpperCase()),
      email: email,
      role: isEmp ? 'employer' : 'candidate',
      initial: email.substring(0, 2).toUpperCase(),
      hasEmployerAccess: isEmp
    };
    setAuthUser(user);
    closeAuthModal();
    showToast(`Welcome back, ${user.name}!`);
  } else {
    const name = document.getElementById('auth-reg-name')?.value.trim() || 'Logistics Specialist';
    const email = document.getElementById('auth-reg-email')?.value.trim() || 'member@thesandbox.vn';
    const isEmp = document.getElementById('auth-reg-role')?.value === 'employer';
    const user = {
      name: name,
      email: email,
      role: isEmp ? 'employer' : 'candidate',
      initial: name.substring(0, 2).toUpperCase(),
      hasEmployerAccess: isEmp
    };
    setAuthUser(user);
    closeAuthModal();
    showToast(`Account created successfully! Welcome, ${user.name}.`);
  }
};

window.openCandidateProfileModal = function() {
  const modal = document.getElementById('modal-candidate-profile');
  if (modal) modal.classList.add('show');
};

window.closeCandidateProfileModal = function() {
  const modal = document.getElementById('modal-candidate-profile');
  if (modal) modal.classList.remove('show');
};

window.openSavedJobsModal = function() {
  const modal = document.getElementById('modal-saved-jobs');
  const container = document.getElementById('saved-jobs-list-container');
  const countEl = document.getElementById('saved-jobs-modal-count');

  const savedIds = getSavedJobIds();
  if (countEl) countEl.textContent = `${savedIds.length} Saved Positions`;

  if (container) {
    const savedJobs = jobsDatabase.filter(j => savedIds.includes(j.id));
    if (savedJobs.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:36px 12px; color:#64748B;">
          <i class="fa-regular fa-bookmark" style="font-size:32px; color:#CBD5E1; margin-bottom:10px;"></i>
          <h4 style="font-size:15px; font-weight:700; color:#0F172A; margin:0 0 6px;">No Saved Jobs Yet</h4>
          <p style="font-size:12.5px; margin:0;">Click the bookmark icon on any job card to save it for quick review.</p>
        </div>
      `;
    } else {
      container.innerHTML = savedJobs.map(job => `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 14px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; margin-bottom:10px; gap:12px;">
          <div>
            <h4 style="font-size:14px; font-weight:700; color:#0F172A; margin:0 0 3px;">${job.title}</h4>
            <div style="font-size:12px; color:#64748B;">${job.company} · <strong style="color:#EA580C;">${job.salary}</strong></div>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            ${job.applyMethod === 'external' ? `
              <a href="${job.applyUrl || '#'}" target="_blank" rel="noopener noreferrer" class="btn-linkedin-easy-apply" style="padding:6px 14px; font-size:12px; text-decoration:none; display:inline-flex; align-items:center; gap:5px;">
                <i class="fa-solid fa-arrow-up-right-from-square"></i> Apply
              </a>
            ` : `
              <button type="button" class="btn-linkedin-easy-apply" onclick="closeSavedJobsModal(); openApplyModal(jobsDatabase.find(j=>j.id==='${job.id}'));" style="padding:6px 14px; font-size:12px;">
                <i class="fa-solid fa-paper-plane"></i> Apply
              </button>
            `}
          </div>
        </div>
      `).join('');
    }
  }

  if (modal) modal.classList.add('show');
};

window.closeSavedJobsModal = function() {
  const modal = document.getElementById('modal-saved-jobs');
  if (modal) modal.classList.remove('show');
};

window.openHelpModal = function() {
  const currentPath = window.location.pathname || '';
  if (currentPath.endsWith('help.html') || currentPath.includes('/help')) {
    return;
  }
  window.location.href = 'help.html';
};

window.closeHelpModal = function() {
  const modal = document.getElementById('modal-help-dialog');
  if (modal) modal.classList.remove('show');
};

// Global click-outside listener to close account dropdown
document.addEventListener('click', (e) => {
  const wrap = document.getElementById('user-profile-menu-wrap');
  if (wrap && wrap.classList.contains('open')) {
    if (!wrap.contains(e.target)) {
      closeUserProfileDropdown();
    }
  }
});

// Escape key closes dropdown and modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeUserProfileDropdown();
    closeAuthModal();
    closeCandidateProfileModal();
    closeSavedJobsModal();
    closeHelpModal();
  }
});

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  updateAuthHeaderUI();
  renderUserProfileDropdown();
});



/* ==========================================================================
   ENHANCED 5-STEP APPLICATION WIZARD, DUPLICATE PREVENTER & TRACKING ENGINE
   ========================================================================== */

const INITIAL_DEMO_APPLICATIONS = [
  {
    id: 'app-seed-1',
    refNumber: 'SBX-2026-APP-74192',
    jobId: 'job-1',
    jobTitle: 'Senior Ocean Freight Forwarder',
    company: 'Viconship Logistics Group',
    employerEmail: 'recruitment@viconship.com',
    salary: '₫28,000,000 – ₫42,000,000 / mo',
    candidateName: 'Nguyen Minh Tri',
    candidateEmail: 'minh.tri@enterprise3pl.vn',
    candidatePhone: '+84 908 123 456',
    experience: '5 Years',
    certification: 'FIATA Diploma / FIATA Higher',
    cvFileName: 'Nguyen_Minh_Tri_CV_2026.pdf',
    cvFileSize: '1.8 MB',
    availability: 'Available Immediately (Ready to start)',
    coverNote: 'Extensive experience on Transpacific & Asia-Europe maritime container lanes. FIATA certified.',
    submittedAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    submittedDisplay: '12 Oct 2026, 14:35',
    status: 'Screening',
    statusClass: 'app-status--screening'
  }
];

function getSubmittedApplications() {
  try {
    const raw = localStorage.getItem('thesandbox_applications');
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  localStorage.setItem('thesandbox_applications', JSON.stringify(INITIAL_DEMO_APPLICATIONS));
  return INITIAL_DEMO_APPLICATIONS;
}

function saveSubmittedApplications(list) {
  try {
    localStorage.setItem('thesandbox_applications', JSON.stringify(list));
  } catch(e) {}
  updateApplicationCountBadges();
  renderProfileApplications();
}

function updateApplicationCountBadges() {
  const list = getSubmittedApplications();
  const count = list.length;
  document.querySelectorAll('#profile-modal-apps-badge, #profile-apps-count-label, #profile-menu-apps-count').forEach(el => {
    if (el) el.textContent = count;
  });
}

// State for active apply session
let currentApplyJob = null;
let currentApplyStep = 1;
let currentCvSource = 'profile'; // 'profile' or 'upload'
let customUploadedCv = null;
let lastSubmittedAppRef = null;

window.openApplyModal = function(jobOrTitle) {
  // Determine target job
  let target = null;
  if (typeof jobOrTitle === 'string') {
    target = jobsDatabase.find(j => j.title.toLowerCase().includes(jobOrTitle.toLowerCase()) || jobOrTitle.toLowerCase().includes(j.title.toLowerCase())) || {
      id: 'job-1',
      title: jobOrTitle,
      company: 'Viconship Logistics Group',
      applyMethod: 'direct',
      applyEmail: 'recruitment@viconship.com',
      salary: '₫28,000,000 – ₫42,000,000 / mo',
      location: 'Ho Chi Minh City · District 1'
    };
  } else if (jobOrTitle && jobOrTitle.id) {
    target = jobOrTitle;
  } else {
    target = activeApplyingJob || jobsDatabase[0];
  }

  currentApplyJob = target;
  activeApplyingJob = target;

  // Preserve in session storage
  try {
    sessionStorage.setItem('thesandbox_preserved_job_id', target.id);
  } catch(e) {}

  const modal = document.getElementById('job-apply-modal');
  if (!modal) return;

  // Update Modal Header & notices
  const titleEl = document.getElementById('modal-title-text');
  const jobNameEl = document.getElementById('modal-job-name');
  const employerEmailNotice = document.getElementById('modal-employer-email-text');

  if (titleEl) titleEl.textContent = 'Easy Apply with CV';
  if (jobNameEl) jobNameEl.textContent = `${target.title} — ${target.company}`;
  if (employerEmailNotice) {
    employerEmailNotice.innerHTML = target.applyEmail
      ? `Direct transmission to employer inbox: <strong>${target.applyEmail}</strong>`
      : `Verified direct candidate pipeline for <strong>${target.company}</strong>`;
  }

  // Check user authentication
  const user = getAuthUser();
  const visitorGate = document.getElementById('apply-visitor-auth-gate');
  const userBanner = document.getElementById('apply-user-status-banner');
  const userStatusText = document.getElementById('apply-user-status-text');

  if (user) {
    if (visitorGate) visitorGate.style.display = 'none';
    if (userBanner) userBanner.style.display = 'flex';
    if (userStatusText) {
      userStatusText.innerHTML = `<i class="fa-solid fa-circle-check"></i> Applying as <strong>${user.name}</strong> (${user.email})`;
    }
    // Pre-fill inputs with user data
    const nameIn = document.getElementById('apply-fullname');
    const emailIn = document.getElementById('apply-email');
    const phoneIn = document.getElementById('apply-phone');
    if (nameIn && !nameIn.value) nameIn.value = user.name || 'Nguyen Minh Tri';
    if (emailIn && !emailIn.value) emailIn.value = user.email || 'minh.tri@enterprise3pl.vn';
    if (phoneIn && !phoneIn.value) phoneIn.value = user.phone || '+84 908 123 456';
    selectCvSource('profile');
  } else {
    if (visitorGate) visitorGate.style.display = 'flex';
    if (userBanner) userBanner.style.display = 'none';
    selectCvSource('upload');
  }

  // Reset to Step 1
  setApplyWizardStep(1);
  modal.classList.add('show');
};

window.closeApplyModal = function() {
  const modal = document.getElementById('job-apply-modal');
  if (modal) modal.classList.remove('show');
};

window.quickApplySignInDemo = function() {
  quickDemoLogin('candidate');
  // Refresh modal UI with signed-in candidate
  const user = getAuthUser();
  const visitorGate = document.getElementById('apply-visitor-auth-gate');
  const userBanner = document.getElementById('apply-user-status-banner');
  const userStatusText = document.getElementById('apply-user-status-text');

  if (visitorGate) visitorGate.style.display = 'none';
  if (userBanner) userBanner.style.display = 'flex';
  if (userStatusText && user) {
    userStatusText.innerHTML = `<i class="fa-solid fa-circle-check"></i> Applying as <strong>${user.name}</strong> (${user.email})`;
  }

  const nameIn = document.getElementById('apply-fullname');
  const emailIn = document.getElementById('apply-email');
  const phoneIn = document.getElementById('apply-phone');
  if (nameIn) nameIn.value = 'Nguyen Minh Tri';
  if (emailIn) emailIn.value = 'minh.tri@enterprise3pl.vn';
  if (phoneIn) phoneIn.value = '+84 908 123 456';

  selectCvSource('profile');
  showToast('Signed in! Your application for ' + (currentApplyJob ? currentApplyJob.title : 'this role') + ' is preserved.');
};

window.setApplyWizardStep = function(step) {
  currentApplyStep = step;

  // Stepper tab classes
  const tab1 = document.getElementById('apply-step-tab-1');
  const tab2 = document.getElementById('apply-step-tab-2');
  const tab3 = document.getElementById('apply-step-tab-3');
  const div1 = document.getElementById('apply-divider-1');
  const div2 = document.getElementById('apply-divider-2');

  const pane1 = document.getElementById('apply-step-pane-1');
  const pane2 = document.getElementById('apply-step-pane-2');
  const pane3 = document.getElementById('apply-step-pane-3');

  if (tab1) {
    tab1.className = 'apply-step-item' + (step === 1 ? ' active' : (step > 1 ? ' completed' : ''));
    if (step > 1) tab1.querySelector('.apply-step-circle').innerHTML = '<i class="fa-solid fa-check"></i>';
    else tab1.querySelector('.apply-step-circle').textContent = '1';
  }
  if (tab2) {
    tab2.className = 'apply-step-item' + (step === 2 ? ' active' : (step > 2 ? ' completed' : ''));
    if (step > 2) tab2.querySelector('.apply-step-circle').innerHTML = '<i class="fa-solid fa-check"></i>';
    else tab2.querySelector('.apply-step-circle').textContent = '2';
  }
  if (tab3) {
    tab3.className = 'apply-step-item' + (step === 3 ? ' active' : '');
    tab3.querySelector('.apply-step-circle').textContent = '3';
  }

  if (div1) div1.className = 'apply-step-divider' + (step > 1 ? ' active' : '');
  if (div2) div2.className = 'apply-step-divider' + (step > 2 ? ' active' : '');

  if (pane1) pane1.style.display = (step === 1) ? 'block' : 'none';
  if (pane2) pane2.style.display = (step === 2) ? 'block' : 'none';
  if (pane3) pane3.style.display = (step === 3) ? 'block' : 'none';
};

window.selectCvSource = function(source) {
  currentCvSource = source;
  const btnProf = document.getElementById('btn-source-profile-cv');
  const btnUp = document.getElementById('btn-source-upload-cv');
  const boxProf = document.getElementById('cv-profile-box');
  const boxUp = document.getElementById('cv-upload-box');

  if (source === 'profile') {
    if (btnProf) btnProf.classList.add('active');
    if (btnUp) btnUp.classList.remove('active');
    if (boxProf) boxProf.style.display = 'flex';
    if (boxUp) boxUp.style.display = 'none';
  } else {
    if (btnProf) btnProf.classList.remove('active');
    if (btnUp) btnUp.classList.add('active');
    if (boxProf) boxProf.style.display = 'none';
    if (boxUp) boxUp.style.display = 'block';
  }
};

window.handleApplyCvFileChange = function(input) {
  const errBox = document.getElementById('cv-file-error-msg');
  const dropZone = document.getElementById('cv-file-drop');
  const previewCard = document.getElementById('custom-cv-preview-card');
  const nameEl = document.getElementById('custom-cv-name');
  const sizeEl = document.getElementById('custom-cv-size');
  const iconEl = document.getElementById('custom-cv-icon');

  if (errBox) errBox.style.display = 'none';

  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];

  // Extension check
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['pdf', 'doc', 'docx'].includes(ext)) {
    if (errBox) {
      errBox.textContent = 'Invalid file format. Please upload a PDF or DOCX file.';
      errBox.style.display = 'block';
    }
    input.value = '';
    return;
  }

  // Size check (10MB max = 10 * 1024 * 1024)
  if (file.size > 10 * 1024 * 1024) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
    if (errBox) {
      errBox.textContent = `File is too large (${sizeMb} MB). Maximum allowed size is 10 MB.`;
      errBox.style.display = 'block';
    }
    input.value = '';
    return;
  }

  // Valid file
  const sizeFormatted = file.size > 1024 * 1024 
    ? (file.size / (1024 * 1024)).toFixed(1) + ' MB'
    : (file.size / 1024).toFixed(0) + ' KB';

  customUploadedCv = {
    name: file.name,
    size: sizeFormatted,
    ext: ext
  };

  if (nameEl) nameEl.textContent = file.name;
  if (sizeEl) sizeEl.textContent = sizeFormatted;
  if (iconEl) {
    iconEl.className = ext === 'pdf' ? 'fa-solid fa-file-pdf cv-preview-icon' : 'fa-solid fa-file-word cv-preview-icon docx';
  }

  if (dropZone) dropZone.style.display = 'none';
  if (previewCard) previewCard.style.display = 'flex';
};

window.clearUploadedCv = function() {
  customUploadedCv = null;
  const input = document.getElementById('apply-cv-file');
  if (input) input.value = '';
  const dropZone = document.getElementById('cv-file-drop');
  const previewCard = document.getElementById('custom-cv-preview-card');
  if (dropZone) dropZone.style.display = 'block';
  if (previewCard) previewCard.style.display = 'none';
};

window.handleApplyStep1Submit = function(e) {
  e.preventDefault();

  const name = document.getElementById('apply-fullname')?.value.trim();
  const phone = document.getElementById('apply-phone')?.value.trim();
  const email = document.getElementById('apply-email')?.value.trim();
  const exp = document.getElementById('apply-experience')?.value || '3 – 5 Years';
  const cert = document.getElementById('apply-certification')?.value || 'FIATA Diploma';

  if (!name || !phone || !email) {
    showToast('Please fill in your name, contact phone, and email address.');
    return;
  }

  // Ensure CV selected
  let cvName = 'Nguyen_Minh_Tri_CV_2026.pdf';
  let cvSize = '1.8 MB';

  if (currentCvSource === 'upload') {
    if (!customUploadedCv) {
      const errBox = document.getElementById('cv-file-error-msg');
      if (errBox) {
        errBox.textContent = 'Please choose a PDF or DOCX resume to upload.';
        errBox.style.display = 'block';
      }
      showToast('Please upload your CV before proceeding.');
      return;
    }
    cvName = customUploadedCv.name;
    cvSize = customUploadedCv.size;
  }

  // Populate Step 2 Review Screen
  const job = currentApplyJob || jobsDatabase[0];
  const revTitle = document.getElementById('review-job-title');
  const revComp = document.getElementById('review-job-company');
  const revSalary = document.getElementById('review-job-salary');
  const revEmail = document.getElementById('review-dest-email');
  const revName = document.getElementById('review-candidate-name');
  const revContact = document.getElementById('review-candidate-contact');
  const revExp = document.getElementById('review-candidate-exp');
  const revCv = document.getElementById('review-candidate-cv');

  if (revTitle) revTitle.textContent = job.title;
  if (revComp) revComp.textContent = job.company;
  if (revSalary) revSalary.textContent = job.salary || 'Competitive';
  if (revEmail) revEmail.textContent = job.applyEmail || 'recruitment@viconship.com';
  if (revName) revName.textContent = name;
  if (revContact) revContact.textContent = `${phone} · ${email}`;
  if (revExp) revExp.textContent = `${exp} · ${cert}`;
  if (revCv) revCv.textContent = `${cvName} (${cvSize})`;

  // Check duplicate submission
  const existingApps = getSubmittedApplications();
  const dup = existingApps.find(a => a.jobId === job.id && a.candidateEmail.toLowerCase() === email.toLowerCase());
  const dupBox = document.getElementById('apply-duplicate-warning-box');
  const dupDate = document.getElementById('dup-prev-date');
  const dupRef = document.getElementById('dup-prev-ref');

  if (dup && dupBox) {
    dupBox.style.display = 'flex';
    if (dupDate) dupDate.textContent = dup.submittedDisplay;
    if (dupRef) dupRef.textContent = dup.refNumber;
  } else if (dupBox) {
    dupBox.style.display = 'none';
  }

  setApplyWizardStep(2);
};

window.submitFinalJobApplication = function() {
  const job = currentApplyJob || jobsDatabase[0];
  const name = document.getElementById('apply-fullname')?.value.trim() || 'Logistics Specialist';
  const phone = document.getElementById('apply-phone')?.value.trim() || '+84 908 123 456';
  const email = document.getElementById('apply-email')?.value.trim() || 'candidate@thesandbox.vn';
  const exp = document.getElementById('apply-experience')?.value || '3 – 5 Years';
  const cert = document.getElementById('apply-certification')?.value || 'FIATA Diploma';
  const avail = document.getElementById('apply-availability')?.value || 'Available Immediately';
  const note = document.getElementById('apply-cover-note')?.value.trim() || '';

  let cvName = 'Nguyen_Minh_Tri_CV_2026.pdf';
  let cvSize = '1.8 MB';
  if (currentCvSource === 'upload' && customUploadedCv) {
    cvName = customUploadedCv.name;
    cvSize = customUploadedCv.size;
  }

  const submitBtn = document.getElementById('btn-final-submit-apply');
  const originalHtml = submitBtn ? submitBtn.innerHTML : 'Submit Application';

  if (submitBtn) {
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Encrypting &amp; Transmitting...';
    submitBtn.disabled = true;
  }

  setTimeout(() => {
    if (submitBtn) {
      submitBtn.innerHTML = originalHtml;
      submitBtn.disabled = false;
    }

    // Generate unique reference
    const now = new Date();
    const refCode = 'SBX-2026-APP-' + Math.floor(10000 + Math.random() * 90000);
    lastSubmittedAppRef = refCode;

    const timeFormatted = now.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    const newApplication = {
      id: 'app-' + Date.now(),
      refNumber: refCode,
      jobId: job.id,
      jobTitle: job.title,
      company: job.company,
      employerEmail: job.applyEmail || 'recruitment@viconship.com',
      salary: job.salary || 'Competitive',
      candidateName: name,
      candidateEmail: email,
      candidatePhone: phone,
      experience: exp,
      certification: cert,
      cvFileName: cvName,
      cvFileSize: cvSize,
      availability: avail,
      coverNote: note,
      submittedAt: now.toISOString(),
      submittedDisplay: timeFormatted,
      status: 'Under Review',
      statusClass: 'app-status--review'
    };

    // Save to Candidate's application list
    const apps = getSubmittedApplications();
    apps.unshift(newApplication);
    saveSubmittedApplications(apps);

    // Also push to Employer ATS Candidate list
    const atsList = getAtsCandidates();
    atsList.unshift({
      id: `cand-${Date.now()}`,
      name: name,
      role: job.title,
      company: job.company,
      employerEmail: job.applyEmail || 'recruitment@viconship.com',
      cvFileName: cvName,
      exp: exp,
      email: email,
      phone: phone,
      date: 'Just now',
      status: 'new',
      score: '97% Match'
    });
    saveAtsCandidates(atsList);

    // Update Confirmation Screen (Step 3)
    const confRef = document.getElementById('confirm-ref-code');
    const confJob = document.getElementById('confirm-job-title');
    const confComp = document.getElementById('confirm-company-name');
    const confEmail = document.getElementById('confirm-employer-email');
    const confName = document.getElementById('confirm-candidate-name');
    const confCv = document.getElementById('confirm-cv-name');
    const confTime = document.getElementById('confirm-submitted-time');

    if (confRef) confRef.textContent = refCode;
    if (confJob) confJob.textContent = job.title;
    if (confComp) confComp.textContent = job.company;
    if (confEmail) confEmail.textContent = job.applyEmail || 'recruitment@viconship.com';
    if (confName) confName.textContent = name;
    if (confCv) confCv.textContent = `${cvName} (${cvSize})`;
    if (confTime) confTime.textContent = timeFormatted;

    setApplyWizardStep(3);

    showToast(`Application successfully delivered (Sandbox Simulation) to ${job.company}! Reference: ${refCode}`);
  }, 750);
};

window.copyAppRefNumber = function() {
  const ref = lastSubmittedAppRef || ('SBX-2026-APP-' + Math.floor(10000 + Math.random() * 90000));
  if (navigator.clipboard) {
    navigator.clipboard.writeText(ref);
    showToast(`Copied Application Reference: ${ref}`);
  } else {
    showToast(`Reference Code: ${ref}`);
  }
};

window.downloadApplicationReceipt = function() {
  const ref = lastSubmittedAppRef || ('SBX-2026-APP-' + Math.floor(10000 + Math.random() * 90000));
  const job = currentApplyJob || jobsDatabase[0];
  showToast(`Receipt downloaded: ${ref}_Application_Summary.pdf`);
};

// ==========================================
// CANDIDATE PROFILE & TRACKING MANAGEMENT
// ==========================================

window.openCandidateProfileModal = function(initialTab) {
  const modal = document.getElementById('modal-candidate-profile');
  if (!modal) return;

  // Sync profile details if signed in
  const user = getAuthUser();
  if (user) {
    const nameEl = document.getElementById('profile-name-display');
    const emailEl = document.getElementById('profile-email-display');
    const avatarEl = document.getElementById('profile-avatar-display');
    if (nameEl) nameEl.textContent = user.name;
    if (emailEl) emailEl.textContent = user.email;
    if (avatarEl) avatarEl.textContent = user.initial || 'NT';
  }

  renderProfileApplications();
  switchProfileTab(initialTab === 'applications' ? 'applications' : 'info');
  modal.classList.add('show');
};

window.closeCandidateProfileModal = function() {
  const modal = document.getElementById('modal-candidate-profile');
  if (modal) modal.classList.remove('show');
};

window.switchProfileTab = function(tab) {
  const tabInfo = document.getElementById('tab-profile-info');
  const tabApps = document.getElementById('tab-profile-apps');
  const paneInfo = document.getElementById('pane-profile-info');
  const paneApps = document.getElementById('pane-profile-applications');

  if (tab === 'applications') {
    if (tabInfo) tabInfo.classList.remove('active');
    if (tabApps) tabApps.classList.add('active');
    if (paneInfo) paneInfo.style.display = 'none';
    if (paneApps) paneApps.style.display = 'block';
    renderProfileApplications();
  } else {
    if (tabInfo) tabInfo.classList.add('active');
    if (tabApps) tabApps.classList.remove('active');
    if (paneInfo) paneInfo.style.display = 'block';
    if (paneApps) paneApps.style.display = 'none';
  }
};

window.renderProfileApplications = function() {
  const container = document.getElementById('profile-applications-list-container');
  if (!container) return;

  const apps = getSubmittedApplications();
  updateApplicationCountBadges();

  if (apps.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:32px 14px; color:#64748B;">
        <i class="fa-solid fa-file-circle-check" style="font-size:32px; color:#CBD5E1; margin-bottom:10px;"></i>
        <h4 style="font-size:14px; font-weight:700; color:#0F172A; margin:0 0 4px;">No Active Applications</h4>
        <p style="font-size:12px; margin:0 0 14px;">You have not submitted any applications through The SandBox network yet.</p>
        <button type="button" class="btn-apply-primary" onclick="closeCandidateProfileModal(); switchPortalMode('candidate');" style="padding:6px 14px; font-size:12px;">
          Explore Open Positions
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = apps.map(app => {
    let statusClass = 'app-status--review';
    let statusIcon = 'fa-clock';
    if (app.status === 'Screening') {
      statusClass = 'app-status--screening';
      statusIcon = 'fa-eye';
    } else if (app.status === 'Shortlisted' || app.status === 'Interview') {
      statusClass = 'app-status--interview';
      statusIcon = 'fa-calendar-check';
    }

    return `
      <div class="application-tracking-card" id="app-card-${app.id}">
        <div class="app-tracking-head">
          <div>
            <h4 class="app-tracking-title">${app.jobTitle}</h4>
            <div class="app-tracking-company">
              <strong>${app.company}</strong> &bull; <span style="color:#0044CC;">${app.salary}</span>
            </div>
          </div>
          <span class="app-status-pill ${statusClass}">
            <i class="fa-solid ${statusIcon}"></i> ${app.status}
          </span>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:6px; padding:6px 10px; margin:8px 0; font-size:11.5px;">
          <span style="color:#64748B;">Ref: <strong style="font-family:monospace; color:#0044CC;">${app.refNumber}</strong></span>
          <span style="color:#0F172A;"><i class="fa-solid fa-file-pdf" style="color:#DC2626;"></i> ${app.cvFileName}</span>
        </div>

        <div class="app-tracking-footer">
          <span>Submitted: <strong>${app.submittedDisplay}</strong></span>
          <div style="display:flex; gap:6px;">
            <button type="button" class="btn-cv-sub-action" onclick="showToast('Application Ref ${app.refNumber} is currently ${app.status} with ${app.company}.');" style="padding:3px 8px; font-size:11px;">
              <i class="fa-solid fa-circle-info"></i> Status Details
            </button>
            <button type="button" class="btn-cv-sub-action danger" onclick="withdrawApplication('${app.id}');" style="padding:3px 8px; font-size:11px;">
              Withdraw
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
};

window.withdrawApplication = function(appId) {
  if (!confirm('Are you sure you want to withdraw this application? The hiring employer will be notified.')) {
    return;
  }
  let apps = getSubmittedApplications();
  apps = apps.filter(a => a.id !== appId);
  saveSubmittedApplications(apps);
  showToast('Application withdrawn successfully.');
};

// Initialize listeners on load
document.addEventListener('DOMContentLoaded', () => {
  updateApplicationCountBadges();

  // Dynamic news article hydration for news-detail.html?id=...
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const requestedArticleId = urlParams.get('slug') || urlParams.get('id');
    if (requestedArticleId && (window.location.pathname.includes('news-detail') || document.querySelector('main header h1'))) {
      hydrateNewsDetailPage(requestedArticleId);
    }
  } catch(e) {}
});

function hydrateNewsDetailPage(articleId) {
  const articles = getNewsArticles();
  const art = articles.find(a => a.id === articleId || a.slug === articleId || a.aliasId === articleId);
  if (!art) return;

  // Security & Draft Privacy: If an article is draft, only administrators can preview it
  if (art.isDraft || art.status === 'draft') {
    const user = getAuthUser();
    if (!user || (user.role !== 'admin' && !user.isAdmin)) {
      alert('🔒 Access Denied: This article is currently an unpublished draft. Only authorized administrators can view it.');
      window.location.href = 'news.html';
      return;
    }
  }

  document.title = `${art.title} - The SandBox Logistics Network`;
  
  const h1 = document.querySelector('main header h1');
  if (h1) h1.textContent = art.title;

  const sub = document.querySelector('main header p');
  if (sub && art.summary) sub.textContent = art.summary;

  const catSpan = document.querySelector('main header span[style*="uppercase"]');
  if (catSpan) catSpan.textContent = (art.categoryLabel || art.category).toUpperCase();

  const metaSpans = document.querySelectorAll('main header div span[style*="color: #64748B"]');
  if (metaSpans.length > 0 && art.readTime) {
    metaSpans[0].innerHTML = `<i class="fa-solid fa-clock"></i> ${art.readTime}`;
  }
  if (metaSpans.length > 1 && art.date) {
    metaSpans[1].textContent = `• Updated ${art.date}`;
  }

  const authorName = document.querySelector('main header div div strong');
  if (authorName && art.author) authorName.textContent = art.author;

  const authorRole = document.querySelector('main header div div span[style*="font-size: 11.5px"]');
  if (authorRole && art.authorRole) authorRole.textContent = art.authorRole;

  const authorAvatar = document.querySelector('main header div div[style*="border-radius: 50%"]');
  if (authorAvatar && art.authorInitial) authorAvatar.textContent = art.authorInitial;

  const articleContainer = document.querySelector('main .container');
  if (articleContainer && art.body) {
    let bodyWrap = document.getElementById('news-detail-dynamic-body');
    if (!bodyWrap) {
      bodyWrap = document.createElement('div');
      bodyWrap.id = 'news-detail-dynamic-body';
      bodyWrap.style.fontSize = '15px';
      bodyWrap.style.lineHeight = '1.8';
      bodyWrap.style.color = '#334155';
      bodyWrap.style.margin = '28px 0';
      const headerEl = articleContainer.querySelector('header');
      if (headerEl && headerEl.nextElementSibling) {
        headerEl.parentNode.insertBefore(bodyWrap, headerEl.nextElementSibling);
      }
    }
    bodyWrap.innerHTML = art.body;
  }
}


window.filterJobsByWorkType = function(val) {
  var query = (val || '').trim().toLowerCase();
  var cards = document.querySelectorAll('.fw-job-card, .job-card-row, .builtin-job-card');
  cards.forEach(function(card) {
    if (!query) {
      card.style.display = '';
      return;
    }
    var text = card.textContent.toLowerCase();
    if (text.indexOf(query) !== -1) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
};
