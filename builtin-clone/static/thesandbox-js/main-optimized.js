/**
 * THE SANDBOX - PERFORMANCE OPTIMIZED MAIN SCRIPT
 * Built In Design System with High-Traffic Optimizations
 * 
 * Features:
 * - Smooth scrolling with RAF throttling
 * - Request batching for DOM operations
 * - Memory leak prevention
 * - Lazy initialization
 * - Network-aware loading
 */

/* ==========================================================================
   INITIALIZATION & SETUP
   ========================================================================== */

// Prevent scroll restoration on page refresh
if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}

// Clean URL hash on load to prevent auto-scroll
if (window.location.hash) {
  try {
    history.replaceState(null, null, window.location.pathname + window.location.search);
  } catch (e) {
    console.warn('Could not clean URL hash');
  }
}

// Global state management
const AppState = {
  currentLang: 'en',
  scrollPosition: 0,
  isScrolling: false,
  isMobile: false,
  initialized: false
};

/* ==========================================================================
   PERFORMANCE-OPTIMIZED INITIALIZATION
   ========================================================================== */
document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
  // Scroll to top immediately
  window.scrollTo(0, 0);
  
  // Detect viewport size
  updateViewportState();
  
  // Initialize core features immediately
  initSmoothScroll();
  initScrollNavbar();
  initSearch();
  
  // Lazy initialize heavy features
  requestIdleCallback(() => {
    initHeroCarousel();
    initVerticalTabs();
    initFloatingToolbar();
    initLanguageToggle();
  }, { timeout: 2000 });
  
  // Initialize on interaction (very heavy features)
  initOnFirstInteraction([
    initYouTubeHub,
    initSplitScreenJobBoard,
    initJobApplyModal,
    initStatisticCounters
  ]);
  
  // Setup event listeners with performance optimization
  setupEventListeners();
  
  // Mark as initialized
  AppState.initialized = true;
  console.log('✓ App initialized successfully');
}

/* ==========================================================================
   VIEWPORT & DEVICE DETECTION
   ========================================================================== */
function updateViewportState() {
  const width = window.innerWidth;
  AppState.isMobile = width < 768;
  AppState.isTablet = width >= 768 && width < 1024;
  AppState.isDesktop = width >= 1024;
  
  // Update body classes
  document.body.classList.toggle('is-mobile', AppState.isMobile);
  document.body.classList.toggle('is-tablet', AppState.isTablet);
  document.body.classList.toggle('is-desktop', AppState.isDesktop);
}

// Use debounced resize handler
const handleResize = PerformanceUtils.debounce(() => {
  updateViewportState();
  
  // Dispatch custom event for components to react
  window.dispatchEvent(new CustomEvent('viewportchange', {
    detail: {
      width: window.innerWidth,
      height: window.innerHeight,
      isMobile: AppState.isMobile
    }
  }));
}, 250);

/* ==========================================================================
   LAZY INITIALIZATION - Only run when user interacts
   ========================================================================== */
function initOnFirstInteraction(callbacks) {
  const events = ['scroll', 'mousemove', 'touchstart', 'click'];
  let initialized = false;
  
  const handler = () => {
    if (!initialized) {
      initialized = true;
      
      // Remove listeners
      events.forEach(event => {
        window.removeEventListener(event, handler, { passive: true });
      });
      
      // Execute callbacks
      requestIdleCallback(() => {
        callbacks.forEach(callback => {
          try {
            callback();
          } catch (e) {
            console.error('Error in lazy init:', e);
          }
        });
      });
    }
  };
  
  // Add listeners
  events.forEach(event => {
    window.addEventListener(event, handler, { passive: true, once: true });
  });
}

/* ==========================================================================
   SMOOTH SCROLLING - Optimized with RAF
   ========================================================================== */
function initSmoothScroll() {
  // Use event delegation for better performance
  document.addEventListener('click', handleSmoothScrollClick, false);
}

function handleSmoothScrollClick(e) {
  const link = e.target.closest('a[href^="#"]');
  if (!link) return;
  
  const href = link.getAttribute('href');
  if (href === '#' || href === '#!') return;
  
  const targetId = href.slice(1);
  const targetEl = document.getElementById(targetId);
  
  if (targetEl) {
    e.preventDefault();
    smoothScrollTo(targetEl);
  }
}

function smoothScrollTo(element, offset = 0) {
  const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
  const startPosition = window.pageYOffset;
  const distance = targetPosition - startPosition;
  const duration = 800; // 800ms for smooth feel like Built In
  let start = null;
  
  function animation(currentTime) {
    if (start === null) start = currentTime;
    const timeElapsed = currentTime - start;
    const progress = Math.min(timeElapsed / duration, 1);
    
    // Easing function - ease-in-out cubic
    const ease = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    window.scrollTo(0, startPosition + distance * ease);
    
    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  }
  
  requestAnimationFrame(animation);
}

/* ==========================================================================
   SCROLL NAVBAR - Optimized with RAF Throttle
   ========================================================================== */
function initScrollNavbar() {
  const header = document.querySelector('.header, .fw-masthead-wrapper, header');
  if (!header) return;
  
  let lastScrollTop = 0;
  let ticking = false;
  
  const handleScroll = () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        updateNavbar();
        ticking = false;
      });
      ticking = true;
    }
  };
  
  function updateNavbar() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Add scrolled class after 50px
    if (scrollTop > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    
    // Hide on scroll down, show on scroll up (optional)
    if (scrollTop > lastScrollTop && scrollTop > 200) {
      header.classList.add('scroll-down');
      header.classList.remove('scroll-up');
    } else {
      header.classList.remove('scroll-down');
      header.classList.add('scroll-up');
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    AppState.scrollPosition = scrollTop;
  }
  
  // Use passive listener for better scroll performance
  window.addEventListener('scroll', handleScroll, { passive: true });
}

/* ==========================================================================
   HERO CAROUSEL - Performance Optimized
   ========================================================================== */
function initHeroCarousel() {
  const carousel = document.querySelector('.hero-editorial-section, .carousel-container');
  if (!carousel) return;
  
  const slides = carousel.querySelectorAll('.hero-editorial-slide, .carousel-slide');
  const dots = carousel.querySelectorAll('.hero-dot, .dot-indicator');
  const prevBtn = carousel.querySelector('.hero-arrow-prev, .carousel-nav-prev');
  const nextBtn = carousel.querySelector('.hero-arrow-next, .carousel-nav-next');
  
  if (!slides.length) return;
  
  let currentIndex = 0;
  let autoplayTimer = null;
  let isTransitioning = false;
  
  function showSlide(index, immediate = false) {
    if (isTransitioning && !immediate) return;
    
    isTransitioning = true;
    
    // Use request batcher for DOM updates
    window.requestBatcher.write(() => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
      });
      
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
      
      currentIndex = index;
      
      // Allow transitions after a delay
      setTimeout(() => {
        isTransitioning = false;
      }, 300); // Match CSS transition duration
    });
  }
  
  function nextSlide() {
    const next = (currentIndex + 1) % slides.length;
    showSlide(next);
  }
  
  function prevSlide() {
    const prev = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(prev);
  }
  
  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(nextSlide, 5000);
  }
  
  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }
  
  // Event listeners
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      nextSlide();
      startAutoplay();
    });
  }
  
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      prevSlide();
      startAutoplay();
    });
  }
  
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      showSlide(index);
      startAutoplay();
    });
  });
  
  // Pause on hover
  carousel.addEventListener('mouseenter', stopAutoplay);
  carousel.addEventListener('mouseleave', startAutoplay);
  
  // Pause when tab is hidden
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stopAutoplay();
    } else {
      startAutoplay();
    }
  });
  
  // Start autoplay
  startAutoplay();
  
  // Cleanup
  window.addEventListener('beforeunload', stopAutoplay);
}

/* ==========================================================================
   VERTICAL TABS - Optimized with Event Delegation
   ========================================================================== */
function initVerticalTabs() {
  const tabContainers = document.querySelectorAll('[data-tabs]');
  
  tabContainers.forEach(container => {
    const tabs = container.querySelectorAll('[data-tab]');
    const panels = container.querySelectorAll('[data-panel]');
    
    if (!tabs.length || !panels.length) return;
    
    // Use event delegation
    container.addEventListener('click', (e) => {
      const tab = e.target.closest('[data-tab]');
      if (!tab) return;
      
      const tabId = tab.dataset.tab;
      
      // Batch DOM updates
      window.requestBatcher.write(() => {
        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));
        
        tab.classList.add('active');
        const panel = container.querySelector(`[data-panel="${tabId}"]`);
        if (panel) {
          panel.classList.add('active');
        }
      });
    });
  });
}

/* ==========================================================================
   SEARCH FUNCTIONALITY - Debounced for Performance
   ========================================================================== */
function initSearch() {
  const searchInputs = document.querySelectorAll('.search-input, input[type="search"]');
  
  searchInputs.forEach(input => {
    // Debounced search handler
    const debouncedSearch = PerformanceUtils.debounce((value) => {
      performSearch(value);
    }, 300);
    
    input.addEventListener('input', (e) => {
      debouncedSearch(e.target.value);
    });
  });
}

function performSearch(query) {
  if (!query || query.length < 2) return;
  
  // Check cache first
  const cacheKey = `search:${query}`;
  const cached = window.cacheManager.get(cacheKey);
  
  if (cached) {
    displaySearchResults(cached);
    return;
  }
  
  // Simulate API call (replace with actual API)
  console.log('Searching for:', query);
  
  // In production, make actual API call here
  // fetch(`/api/search?q=${encodeURIComponent(query)}`)
  //   .then(res => res.json())
  //   .then(data => {
  //     window.cacheManager.set(cacheKey, data);
  //     displaySearchResults(data);
  //   });
}

function displaySearchResults(results) {
  console.log('Search results:', results);
  // Implement search results display
}

/* ==========================================================================
   LANGUAGE TOGGLE
   ========================================================================== */
function initLanguageToggle() {
  const langBtn = document.getElementById('lang-toggle-btn');
  if (!langBtn) return;
  
  langBtn.addEventListener('click', () => {
    AppState.currentLang = AppState.currentLang === 'en' ? 'vi' : 'en';
    langBtn.textContent = AppState.currentLang === 'en' ? 'EN' : 'VI';
    
    // Dispatch language change event
    window.dispatchEvent(new CustomEvent('languagechange', {
      detail: { lang: AppState.currentLang }
    }));
    
    // In production, reload content in new language
    console.log('Language changed to:', AppState.currentLang);
  });
}

/* ==========================================================================
   FLOATING TOOLBAR - Show/Hide on Scroll
   ========================================================================== */
function initFloatingToolbar() {
  const toolbar = document.querySelector('.floating-toolbar, .sticky-actions');
  if (!toolbar) return;
  
  const handleScroll = PerformanceUtils.throttle(() => {
    const scrollTop = window.pageYOffset;
    
    window.requestBatcher.write(() => {
      if (scrollTop > 500) {
        toolbar.classList.add('visible');
      } else {
        toolbar.classList.remove('visible');
      }
    });
  }, 100);
  
  window.addEventListener('scroll', handleScroll, { passive: true });
}

/* ==========================================================================
   YOUTUBE HUB - Lazy Load Videos
   ========================================================================== */
function initYouTubeHub() {
  const videoContainers = document.querySelectorAll('.fw-yt-iframe-wrap');
  
  videoContainers.forEach(container => {
    const iframe = container.querySelector('iframe');
    if (!iframe || !iframe.dataset.src) return;
    
    // Only load video when visible
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Load video
          iframe.src = iframe.dataset.src;
          observer.unobserve(container);
          
          console.log('YouTube video loaded');
        }
      });
    }, { rootMargin: '200px' });
    
    observer.observe(container);
  });
}

/* ==========================================================================
   SPLIT-SCREEN JOB BOARD - Optimized for High Traffic
   ========================================================================== */
function initSplitScreenJobBoard() {
  const jobCards = document.querySelectorAll('.job-card, [data-job-id]');
  const detailPane = document.getElementById('job-detail-pane');
  
  if (!jobCards.length || !detailPane) return;
  
  // Cache job details
  const jobCache = new Map();
  
  // Use event delegation for better performance
  document.addEventListener('click', async (e) => {
    const card = e.target.closest('.job-card, [data-job-id]');
    if (!card) return;
    
    const jobId = card.dataset.jobId;
    if (!jobId) return;
    
    // Update active state
    window.requestBatcher.write(() => {
      jobCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
    });
    
    // Load job details
    await loadJobDetails(jobId, detailPane, jobCache);
  });
  
  // Prefetch on hover
  if (!AppState.isMobile && window.prefetchManager) {
    jobCards.forEach(card => {
      card.addEventListener('mouseenter', () => {
        const jobId = card.dataset.jobId;
        if (jobId && !jobCache.has(jobId)) {
          // Prefetch job data
          window.prefetchManager.prefetch(`/api/jobs/${jobId}`);
        }
      }, { once: true, passive: true });
    });
  }
}

async function loadJobDetails(jobId, container, cache) {
  // Show loading skeleton
  container.innerHTML = createSkeletonHTML();
  
  // Check cache
  if (cache.has(jobId)) {
    displayJobDetails(cache.get(jobId), container);
    return;
  }
  
  try {
    // Simulate API call
    const response = await fetch(`/api/jobs/${jobId}`);
    const data = await response.json();
    
    // Cache the result
    cache.set(jobId, data);
    
    // Display details
    displayJobDetails(data, container);
    
    // Update URL without reload
    history.pushState(null, '', `?job=${jobId}`);
    
  } catch (error) {
    console.error('Error loading job:', error);
    container.innerHTML = '<p class="error">Failed to load job details.</p>';
  }
}

function displayJobDetails(data, container) {
  window.requestBatcher.write(() => {
    container.innerHTML = `
      <div class="job-detail animate-fadeInUp">
        <div class="job-detail-header">
          <img src="${data.logo}" alt="${data.company}" class="company-logo">
          <div>
            <h2>${data.title}</h2>
            <p class="company-name">${data.company}</p>
          </div>
          <button class="btn btn-primary">Apply Now</button>
        </div>
        <div class="job-detail-content">
          ${data.description}
        </div>
      </div>
    `;
  });
}

function createSkeletonHTML() {
  return `
    <div class="skeleton-loader">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-card"></div>
    </div>
  `;
}

/* ==========================================================================
   JOB APPLY MODAL
   ========================================================================== */
function initJobApplyModal() {
  const applyButtons = document.querySelectorAll('.btn-apply, [data-apply]');
  
  applyButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openApplyModal(btn.dataset.jobId);
    });
  });
}

function openApplyModal(jobId) {
  // Implementation for modal
  console.log('Opening apply modal for job:', jobId);
}

/* ==========================================================================
   STATISTIC COUNTERS - Animate on Scroll
   ========================================================================== */
function initStatisticCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  
  counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
  const target = parseInt(element.dataset.count);
  const duration = 2000;
  const start = 0;
  const increment = target / (duration / 16); // 60fps
  let current = start;
  
  const timer = setInterval(() => {
    current += increment;
    
    if (current >= target) {
      element.textContent = target.toLocaleString();
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current).toLocaleString();
    }
  }, 16);
}

/* ==========================================================================
   EVENT LISTENERS SETUP
   ========================================================================== */
function setupEventListeners() {
  // Resize handler
  window.addEventListener('resize', handleResize, { passive: true });
  
  // Online/Offline detection
  window.addEventListener('online', () => {
    document.body.classList.remove('offline');
    console.log('Connection restored');
  });
  
  window.addEventListener('offline', () => {
    document.body.classList.add('offline');
    console.log('Connection lost');
  });
  
  // Cleanup on unload
  window.addEventListener('beforeunload', cleanup);
}

/* ==========================================================================
   CLEANUP - Prevent Memory Leaks
   ========================================================================== */
function cleanup() {
  // Clear intervals and timeouts
  // Remove event listeners via EventManager
  if (window.eventManager) {
    window.eventManager.cleanup();
  }
  
  console.log('✓ Cleanup completed');
}

/* ==========================================================================
   POLYFILLS & FALLBACKS
   ========================================================================== */
if (!window.requestIdleCallback) {
  window.requestIdleCallback = function(callback, options) {
    const start = Date.now();
    return setTimeout(function() {
      callback({
        didTimeout: false,
        timeRemaining: function() {
          return Math.max(0, 50 - (Date.now() - start));
        }
      });
    }, 1);
  };
}

if (!window.cancelIdleCallback) {
  window.cancelIdleCallback = function(id) {
    clearTimeout(id);
  };
}

/* ==========================================================================
   EXPORT FOR TESTING
   ========================================================================== */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeApp,
    smoothScrollTo,
    AppState
  };
}
