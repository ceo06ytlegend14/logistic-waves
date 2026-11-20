/**
 * PERFORMANCE UTILITIES FOR HIGH-TRAFFIC SCENARIOS
 * Built In Design System - Optimized for scalability
 * 
 * Features:
 * - Debouncing & Throttling for event handling
 * - Intersection Observer for lazy loading
 * - Request batching with RAF
 * - Image lazy loading
 * - Memory leak prevention
 */

/* ==========================================================================
   DEBOUNCE - Limit function execution frequency
   Use for: resize, scroll, input events
   ========================================================================== */
function debounce(func, wait = 300, immediate = false) {
  let timeout;
  
  return function executedFunction(...args) {
    const context = this;
    
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    
    const callNow = immediate && !timeout;
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    
    if (callNow) func.apply(context, args);
  };
}

/* ==========================================================================
   THROTTLE - Ensure function runs at most once per interval
   Use for: scroll events, mouse movement
   ========================================================================== */
function throttle(func, limit = 100) {
  let inThrottle;
  let lastRan;
  
  return function executedFunction(...args) {
    const context = this;
    
    if (!inThrottle) {
      func.apply(context, args);
      lastRan = Date.now();
      inThrottle = true;
      
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/* ==========================================================================
   REQUEST ANIMATION FRAME THROTTLE
   Ensures updates happen at 60fps for smooth animations
   ========================================================================== */
function rafThrottle(func) {
  let ticking = false;
  
  return function executedFunction(...args) {
    const context = this;
    
    if (!ticking) {
      requestAnimationFrame(() => {
        func.apply(context, args);
        ticking = false;
      });
      
      ticking = true;
    }
  };
}

/* ==========================================================================
   INTERSECTION OBSERVER - Lazy Load Elements
   Automatically loads content when it enters viewport
   ========================================================================== */
class LazyLoader {
  constructor(options = {}) {
    this.options = {
      root: null,
      rootMargin: '50px', // Start loading 50px before element enters viewport
      threshold: 0.01,
      ...options
    };
    
    this.observer = null;
    this.elements = new Set();
    this.init();
  }
  
  init() {
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported, loading all content immediately');
      this.loadAllImmediately();
      return;
    }
    
    this.observer = new IntersectionObserver(
      this.handleIntersection.bind(this),
      this.options
    );
  }
  
  handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        this.loadElement(entry.target);
        this.observer.unobserve(entry.target);
        this.elements.delete(entry.target);
      }
    });
  }
  
  loadElement(element) {
    // Load images
    if (element.dataset.src) {
      element.src = element.dataset.src;
      element.classList.add('loaded');
    }
    
    // Load background images
    if (element.dataset.bgSrc) {
      element.style.backgroundImage = `url(${element.dataset.bgSrc})`;
      element.classList.add('loaded');
    }
    
    // Load iframes (videos, embeds)
    if (element.tagName === 'IFRAME' && element.dataset.src) {
      element.src = element.dataset.src;
    }
    
    // Execute custom load function
    if (element.dataset.onload) {
      try {
        const func = new Function(element.dataset.onload);
        func.call(element);
      } catch (e) {
        console.error('Error executing onload function:', e);
      }
    }
    
    // Trigger custom event
    element.dispatchEvent(new CustomEvent('lazyloaded', { 
      bubbles: true,
      detail: { element }
    }));
  }
  
  observe(element) {
    if (this.observer) {
      this.elements.add(element);
      this.observer.observe(element);
    } else {
      this.loadElement(element);
    }
  }
  
  observeAll(selector = '[data-src], [data-bg-src]') {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => this.observe(el));
    return elements.length;
  }
  
  loadAllImmediately() {
    const elements = document.querySelectorAll('[data-src], [data-bg-src]');
    elements.forEach(el => this.loadElement(el));
  }
  
  disconnect() {
    if (this.observer) {
      this.observer.disconnect();
      this.elements.clear();
    }
  }
}

/* ==========================================================================
   IMAGE LAZY LOADING - Optimized for performance
   ========================================================================== */
class ImageLazyLoader extends LazyLoader {
  constructor(options = {}) {
    super({
      rootMargin: '100px', // Load images earlier for smoother experience
      ...options
    });
  }
  
  loadElement(img) {
    if (img.dataset.src) {
      // Create a temporary image to ensure it loads before swapping
      const tempImg = new Image();
      
      tempImg.onload = () => {
        img.src = img.dataset.src;
        img.classList.add('loaded');
        
        // Load srcset if available
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
        }
        
        // Apply fade-in animation
        img.style.opacity = '0';
        requestAnimationFrame(() => {
          img.style.transition = 'opacity 300ms ease-in-out';
          img.style.opacity = '1';
        });
        
        img.dispatchEvent(new CustomEvent('imageloaded', { bubbles: true }));
      };
      
      tempImg.onerror = () => {
        console.error('Failed to load image:', img.dataset.src);
        img.classList.add('load-error');
      };
      
      tempImg.src = img.dataset.src;
    }
  }
}

/* ==========================================================================
   REQUEST BATCHER - Batch multiple DOM reads/writes
   Prevents layout thrashing
   ========================================================================== */
class RequestBatcher {
  constructor() {
    this.readQueue = [];
    this.writeQueue = [];
    this.scheduled = false;
  }
  
  read(callback) {
    this.readQueue.push(callback);
    this.schedule();
  }
  
  write(callback) {
    this.writeQueue.push(callback);
    this.schedule();
  }
  
  schedule() {
    if (!this.scheduled) {
      this.scheduled = true;
      requestAnimationFrame(() => this.flush());
    }
  }
  
  flush() {
    // Execute all reads first (batched)
    while (this.readQueue.length > 0) {
      const callback = this.readQueue.shift();
      try {
        callback();
      } catch (e) {
        console.error('Error in read batch:', e);
      }
    }
    
    // Then execute all writes (batched)
    while (this.writeQueue.length > 0) {
      const callback = this.writeQueue.shift();
      try {
        callback();
      } catch (e) {
        console.error('Error in write batch:', e);
      }
    }
    
    this.scheduled = false;
  }
  
  clear() {
    this.readQueue = [];
    this.writeQueue = [];
    this.scheduled = false;
  }
}

/* ==========================================================================
   SCROLL PERFORMANCE MONITOR
   Detects scroll performance and adjusts animations
   ========================================================================== */
class ScrollPerformanceMonitor {
  constructor(threshold = 16.67) { // 60fps = 16.67ms per frame
    this.threshold = threshold;
    this.lastScrollTime = 0;
    this.frameDrops = 0;
    this.isSlowScrolling = false;
  }
  
  measure() {
    const now = performance.now();
    const delta = now - this.lastScrollTime;
    
    if (this.lastScrollTime > 0 && delta > this.threshold) {
      this.frameDrops++;
      
      // If we've dropped 5 frames in a row, we're scrolling slowly
      if (this.frameDrops >= 5 && !this.isSlowScrolling) {
        this.isSlowScrolling = true;
        this.disableExpensiveAnimations();
      }
    } else {
      this.frameDrops = 0;
      
      if (this.isSlowScrolling) {
        this.isSlowScrolling = false;
        this.enableExpensiveAnimations();
      }
    }
    
    this.lastScrollTime = now;
  }
  
  disableExpensiveAnimations() {
    document.body.classList.add('performance-mode');
    console.log('Performance mode enabled: reducing animations');
  }
  
  enableExpensiveAnimations() {
    document.body.classList.remove('performance-mode');
    console.log('Performance mode disabled: restoring animations');
  }
}

/* ==========================================================================
   MEMORY LEAK PREVENTION
   Automatic cleanup of event listeners and timers
   ========================================================================== */
class EventManager {
  constructor() {
    this.listeners = new Map();
  }
  
  addEventListener(element, event, handler, options) {
    const key = `${event}-${handler.toString()}`;
    
    if (!this.listeners.has(element)) {
      this.listeners.set(element, new Map());
    }
    
    element.addEventListener(event, handler, options);
    this.listeners.get(element).set(key, { event, handler, options });
  }
  
  removeEventListener(element, event, handler) {
    const key = `${event}-${handler.toString()}`;
    
    if (this.listeners.has(element)) {
      const elementListeners = this.listeners.get(element);
      const listener = elementListeners.get(key);
      
      if (listener) {
        element.removeEventListener(listener.event, listener.handler, listener.options);
        elementListeners.delete(key);
        
        if (elementListeners.size === 0) {
          this.listeners.delete(element);
        }
      }
    }
  }
  
  removeAllListeners(element) {
    if (this.listeners.has(element)) {
      const elementListeners = this.listeners.get(element);
      
      elementListeners.forEach((listener) => {
        element.removeEventListener(listener.event, listener.handler, listener.options);
      });
      
      this.listeners.delete(element);
    }
  }
  
  cleanup() {
    this.listeners.forEach((elementListeners, element) => {
      this.removeAllListeners(element);
    });
    this.listeners.clear();
  }
}

/* ==========================================================================
   VIEWPORT UTILITIES
   Detect viewport visibility and size changes
   ========================================================================== */
const ViewportUtils = {
  /**
   * Check if element is in viewport
   */
  isInViewport(element, offset = 0) {
    const rect = element.getBoundingClientRect();
    
    return (
      rect.top >= -offset &&
      rect.left >= -offset &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + offset &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth) + offset
    );
  },
  
  /**
   * Get viewport dimensions
   */
  getViewport() {
    return {
      width: window.innerWidth || document.documentElement.clientWidth,
      height: window.innerHeight || document.documentElement.clientHeight
    };
  },
  
  /**
   * Check if mobile viewport
   */
  isMobile() {
    return this.getViewport().width < 768;
  },
  
  /**
   * Check if tablet viewport
   */
  isTablet() {
    const width = this.getViewport().width;
    return width >= 768 && width < 1024;
  },
  
  /**
   * Check if desktop viewport
   */
  isDesktop() {
    return this.getViewport().width >= 1024;
  }
};

/* ==========================================================================
   NETWORK SPEED DETECTOR
   Adjust content loading based on connection speed
   ========================================================================== */
class NetworkDetector {
  constructor() {
    this.connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    this.effectiveType = this.getEffectiveType();
  }
  
  getEffectiveType() {
    if (!this.connection) {
      return 'unknown';
    }
    
    // effectiveType: 'slow-2g', '2g', '3g', '4g'
    return this.connection.effectiveType || 'unknown';
  }
  
  isSlowConnection() {
    const type = this.getEffectiveType();
    return type === 'slow-2g' || type === '2g';
  }
  
  isFastConnection() {
    const type = this.getEffectiveType();
    return type === '4g';
  }
  
  shouldReduceData() {
    if (!this.connection) {
      return false;
    }
    
    // Reduce data if saveData is enabled or connection is slow
    return this.connection.saveData || this.isSlowConnection();
  }
  
  onConnectionChange(callback) {
    if (this.connection) {
      this.connection.addEventListener('change', () => {
        this.effectiveType = this.getEffectiveType();
        callback(this.effectiveType);
      });
    }
  }
}

/* ==========================================================================
   CACHE MANAGER - Client-side caching
   ========================================================================== */
class CacheManager {
  constructor(maxSize = 50, ttl = 300000) { // 5 minutes default TTL
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttl = ttl;
  }
  
  set(key, value, customTTL = null) {
    // Remove oldest entry if cache is full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl: customTTL || this.ttl
    });
  }
  
  get(key) {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }
    
    // Check if entry has expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.value;
  }
  
  has(key) {
    return this.get(key) !== null;
  }
  
  delete(key) {
    this.cache.delete(key);
  }
  
  clear() {
    this.cache.clear();
  }
  
  size() {
    return this.cache.size;
  }
}

/* ==========================================================================
   PREFETCH MANAGER - Preload resources intelligently
   ========================================================================== */
class PrefetchManager {
  constructor() {
    this.prefetched = new Set();
  }
  
  /**
   * Prefetch a resource
   */
  prefetch(url, as = 'fetch') {
    if (this.prefetched.has(url)) {
      return;
    }
    
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    link.as = as;
    
    document.head.appendChild(link);
    this.prefetched.add(url);
  }
  
  /**
   * Preload critical resource
   */
  preload(url, as = 'fetch') {
    if (this.prefetched.has(url)) {
      return;
    }
    
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = as;
    
    document.head.appendChild(link);
    this.prefetched.add(url);
  }
  
  /**
   * Prefetch on hover (predictive loading)
   */
  prefetchOnHover(selector, urlAttribute = 'href') {
    document.addEventListener('mouseover', (e) => {
      const element = e.target.closest(selector);
      
      if (element) {
        const url = element.getAttribute(urlAttribute);
        
        if (url && !this.prefetched.has(url)) {
          this.prefetch(url);
        }
      }
    }, { passive: true });
  }
}

/* ==========================================================================
   INITIALIZE PERFORMANCE UTILITIES
   ========================================================================== */
const PerformanceUtils = {
  debounce,
  throttle,
  rafThrottle,
  LazyLoader,
  ImageLazyLoader,
  RequestBatcher,
  ScrollPerformanceMonitor,
  EventManager,
  ViewportUtils,
  NetworkDetector,
  CacheManager,
  PrefetchManager
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PerformanceUtils;
}

// Global namespace
if (typeof window !== 'undefined') {
  window.PerformanceUtils = PerformanceUtils;
}

/* ==========================================================================
   AUTO-INITIALIZE ON DOM READY
   ========================================================================== */
if (typeof document !== 'undefined') {
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPerformanceUtils);
  } else {
    initPerformanceUtils();
  }
}

function initPerformanceUtils() {
  // Initialize lazy loading for images
  window.imageLazyLoader = new ImageLazyLoader();
  window.imageLazyLoader.observeAll('img[data-src], [data-bg-src]');
  
  // Initialize request batcher
  window.requestBatcher = new RequestBatcher();
  
  // Initialize event manager
  window.eventManager = new EventManager();
  
  // Initialize cache manager
  window.cacheManager = new CacheManager(100, 600000); // 100 items, 10 min TTL
  
  // Initialize prefetch manager
  window.prefetchManager = new PrefetchManager();
  
  // Detect network conditions
  window.networkDetector = new NetworkDetector();
  
  // Add data-saver class to body if needed
  if (window.networkDetector.shouldReduceData()) {
    document.body.classList.add('data-saver-mode');
    console.log('Data saver mode enabled');
  }
  
  // Log initialization
  console.log('✓ Performance utilities initialized');
}

// Cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    if (window.imageLazyLoader) {
      window.imageLazyLoader.disconnect();
    }
    
    if (window.eventManager) {
      window.eventManager.cleanup();
    }
  });
}
