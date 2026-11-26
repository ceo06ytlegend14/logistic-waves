/* Client-side interactions & Seamless SPA Turbo Router for Logistic Waves. */
(function () {
  "use strict";

  const getLoggedIn = () => document.body.dataset.loggedIn === "true";

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function loginRedirect() {
    const next = window.location.pathname + window.location.search;
    window.location.href = "/auth/login?next=" + encodeURIComponent(next);
  }

  let toastTimer;
  function showToast(message, isError) {
    let el = document.getElementById("toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast";
      el.className = "toast";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    clearTimeout(toastTimer);
    el.textContent = message;
    el.classList.toggle("error", !!isError);
    el.classList.add("show");
    toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
  }
  window.showToast = showToast;

  async function api(url, options) {
    const opts = Object.assign({ credentials: "same-origin" }, options || {});
    const res = await fetch(url, opts);
    let data = {};
    try { data = await res.json(); } catch (e) { /* ignore */ }
    if (res.status === 401) {
      loginRedirect();
      throw new Error("login required");
    }
    if (!res.ok || data.ok === false) {
      throw new Error(data.error || data.message || "Something went wrong.");
    }
    return data;
  }

  function jsonPost(url, payload) {
    return api(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {})
    });
  }

  function jsonRequest(method, url, payload) {
    return api(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {})
    });
  }

  /* ==========================================================================
     Seamless SPA Turbo Router (Zero-Flash, Instant Page Swapping & Prefetching)
     ========================================================================== */

  let progressBar = document.getElementById("turbo-progress");
  if (!progressBar) {
    progressBar = document.createElement("div");
    progressBar.id = "turbo-progress";
    document.body.appendChild(progressBar);
  }
  progressBar.setAttribute("role", "progressbar");
  progressBar.setAttribute("aria-label", "Loading page");
  progressBar.setAttribute("aria-valuemin", "0");
  progressBar.setAttribute("aria-valuemax", "100");

  let progressTimer = null;
  function progressStart() {
    clearTimeout(progressTimer);
    progressBar.style.transition = "width 0.2s cubic-bezier(0.1, 0.9, 0.2, 1), opacity 0.25s ease";
    progressBar.classList.add("active");
    progressBar.style.width = "25%";
    progressTimer = setTimeout(() => {
      progressBar.style.width = "65%";
      progressTimer = setTimeout(() => {
        progressBar.style.width = "85%";
      }, 300);
    }, 150);
  }

  function progressDone() {
    clearTimeout(progressTimer);
    progressBar.style.width = "100%";
    setTimeout(() => {
      progressBar.classList.remove("active");
      setTimeout(() => {
        progressBar.style.transition = "none";
        progressBar.style.width = "0%";
      }, 250);
    }, 180);
  }

  const pageCache = new Map();
  const CACHE_TTL_MS = 90 * 1000; // 90 seconds cache

  function isEligibleUrl(urlString) {
    try {
      const url = new URL(urlString, window.location.origin);
      if (url.origin !== window.location.origin) return false;
      if (url.pathname.startsWith("/api/")) return false;
      if (url.pathname.startsWith("/admin")) return false;
      if (url.pathname.startsWith("/logout")) return false;
      if (url.pathname.endsWith(".xml") || url.pathname.endsWith(".txt") || url.pathname.endsWith(".pdf")) return false;
      return true;
    } catch (e) {
      return false;
    }
  }

  function prefetchUrl(urlString) {
    if (!isEligibleUrl(urlString)) return;
    const url = new URL(urlString, window.location.origin).href;
    const cached = pageCache.get(url);
    if (cached && (Date.now() - cached.time < CACHE_TTL_MS)) return;

    fetch(url, {
      credentials: "same-origin",
      headers: { "X-Requested-With": "LogisticWavesRouter" }
    })
      .then(res => res.ok ? res.text() : null)
      .then(html => {
        if (html) {
          pageCache.set(url, { html, time: Date.now() });
        }
      })
      .catch(() => {});
  }

  async function fetchPage(url) {
    const cached = pageCache.get(url);
    if (cached && (Date.now() - cached.time < CACHE_TTL_MS)) {
      return cached.html;
    }
    const res = await fetch(url, {
      credentials: "same-origin",
      headers: { "X-Requested-With": "LogisticWavesRouter" }
    });
    if (!res.ok) throw new Error("Fetch failed: " + res.status);
    const html = await res.text();
    pageCache.set(url, { html, time: Date.now() });
    return html;
  }

  function syncStylesheets(newDoc) {
    const incomingLinks = newDoc.querySelectorAll('link[rel="stylesheet"]');
    incomingLinks.forEach(link => {
      const href = link.getAttribute("href");
      if (href && !document.querySelector('link[rel="stylesheet"][href="' + href + '"]')) {
        const newLink = document.createElement("link");
        newLink.rel = "stylesheet";
        newLink.href = href;
        document.head.appendChild(newLink);
      }
    });
  }

  function executeInjectedScripts(container) {
    const scripts = container.querySelectorAll("script");
    scripts.forEach(oldScript => {
      const newScript = document.createElement("script");
      Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
      newScript.textContent = oldScript.textContent;
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }

  let isNavigating = false;
  async function seamlessNavigate(targetUrl, pushState = true) {
    if (isNavigating) return;
    const currentMain = document.getElementById("main-content");
    if (!currentMain) {
      window.location.href = targetUrl;
      return;
    }

    isNavigating = true;
    progressStart();
    currentMain.classList.add("page-loading");
    currentMain.setAttribute("aria-busy", "true");

    try {
      const html = await fetchPage(targetUrl);
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newMain = doc.getElementById("main-content");

      if (!newMain) {
        // Fallback to normal navigation if target page doesn't have #main-content
        window.location.href = targetUrl;
        return;
      }

      // Sync any new page-specific stylesheets
      syncStylesheets(doc);

      // Update page title
      if (doc.title) document.title = doc.title;

      // Update body classes and dataset
      if (doc.body) {
        document.body.className = doc.body.className;
        document.body.dataset.loggedIn = doc.body.dataset.loggedIn;
      }

      // Update primary navigation active links & header account actions
      const newNav = doc.querySelector(".main-nav");
      const curNav = document.querySelector(".main-nav");
      if (newNav && curNav) curNav.innerHTML = newNav.innerHTML;

      const newHeaderActions = doc.querySelector(".header-actions");
      const curHeaderActions = document.querySelector(".header-actions");
      if (newHeaderActions && curHeaderActions) curHeaderActions.innerHTML = newHeaderActions.innerHTML;

      const newMobileNav = doc.querySelector(".mobile-nav");
      const curMobileNav = document.querySelector(".mobile-nav");
      if (newMobileNav && curMobileNav) curMobileNav.innerHTML = newMobileNav.innerHTML;

      // Swap main content seamlessly (no white flash, header/footer untouched)
      currentMain.innerHTML = newMain.innerHTML;

      // Run any inline scripts inside the newly injected content
      executeInjectedScripts(currentMain);

      // Update URL in browser history
      if (pushState) {
        history.pushState({ url: targetUrl }, doc.title || "", targetUrl);
      }

      // Scroll to target hash or top
      const targetObj = new URL(targetUrl, window.location.origin);
      if (targetObj.hash) {
        const targetEl = document.querySelector(targetObj.hash);
        if (targetEl) targetEl.scrollIntoView();
        else window.scrollTo({ top: 0, behavior: "instant" });
      } else {
        window.scrollTo({ top: 0, behavior: "instant" });
      }

      // Close mobile nav & search if open
      const mobileNav = document.querySelector(".mobile-nav");
      if (mobileNav && mobileNav.classList.contains("open")) {
        mobileNav.classList.remove("open");
        const menuBtn = document.querySelector(".mobile-menu-btn");
        if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
      }
      hideSearch();

    } catch (err) {
      console.warn("Seamless navigation error, falling back to full reload:", err);
      window.location.href = targetUrl;
      return;
    } finally {
      currentMain.classList.remove("page-loading");
      currentMain.setAttribute("aria-busy", "false");
      progressDone();
      isNavigating = false;
    }
  }

  // Handle browser Back / Forward buttons
  window.addEventListener("popstate", () => {
    seamlessNavigate(window.location.href, false);
  });

  // Prefetch links on hover and touchstart for 0ms transition latency
  document.addEventListener("mouseover", ev => {
    const link = ev.target.closest("a[href]");
    if (!link) return;
    const href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
    prefetchUrl(link.href);
  }, { passive: true });

  document.addEventListener("touchstart", ev => {
    const link = ev.target.closest("a[href]");
    if (!link) return;
    const href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
    prefetchUrl(link.href);
  }, { passive: true });

  // Intercept standard link clicks
  document.addEventListener("click", ev => {
    const link = ev.target.closest("a[href]");
    if (!link) return;

    // Ignore clicks with modifiers (Cmd/Ctrl/Shift/Alt) or right/middle clicks
    if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button !== 0) return;

    // Ignore downloads or new tabs
    if (link.target && link.target !== "_self") return;
    if (link.hasAttribute("download")) return;

    const href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:")) return;

    if (!isEligibleUrl(link.href)) return;

    const targetUrl = new URL(link.href, window.location.origin);
    const currentUrl = new URL(window.location.href);

    // If clicking same page hash, let browser handle or smooth scroll
    if (targetUrl.pathname === currentUrl.pathname && targetUrl.search === currentUrl.search) {
      if (targetUrl.hash) return; // anchor jump
      ev.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    ev.preventDefault();
    seamlessNavigate(targetUrl.href, true);
  });

  /* ---------- mobile navigation toggle (Delegated) ---------- */
  document.addEventListener("click", ev => {
    const menuBtn = ev.target.closest(".mobile-menu-btn");
    if (!menuBtn) return;
    const mobileNav = document.querySelector(".mobile-nav");
    if (mobileNav) {
      const open = mobileNav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", String(open));
    }
  });

  /* ---------- global search ---------- */
  const overlay = document.getElementById("searchOverlay");
  const searchInput = document.getElementById("globalSearchInput");
  const searchResults = document.getElementById("globalSearchResults");
  let searchTimer;

  function openSearch() {
    if (!overlay) return;
    overlay.hidden = false;
    if (searchInput) setTimeout(() => searchInput.focus(), 30);
  }
  function hideSearch() {
    if (overlay) overlay.hidden = true;
  }

  document.addEventListener("click", ev => {
    if (ev.target.closest(".search-trigger")) {
      openSearch();
      return;
    }
    if (ev.target.closest("#closeSearch")) {
      hideSearch();
      return;
    }
    if (ev.target === overlay) {
      hideSearch();
      return;
    }
  });

  function renderSearchGroup(title, items, mapper) {
    if (!items || !items.length) return "";
    return '<section><h3>' + escapeHtml(title) + "</h3>" +
      items.map(mapper).join("") + "</section>";
  }

  async function runGlobalSearch(q) {
    if (!searchResults) return;
    if (!q.trim()) {
      searchResults.innerHTML = '<section><h3>Start typing</h3><a>Search jobs, companies and articles…</a></section>';
      return;
    }
    try {
      const data = await api("/api/search?q=" + encodeURIComponent(q));
      const html =
        renderSearchGroup("Jobs", data.jobs, j =>
          '<a href="/job/' + encodeURIComponent(j.slug || "job") + "/" + j.id + '">' +
          escapeHtml(j.title) + "<small>" + escapeHtml(j.company_name) + "</small></a>") +
        renderSearchGroup("Companies", data.companies, c =>
          '<a href="/company/' + encodeURIComponent(c.slug) + '">' +
          escapeHtml(c.name) + "<small>" + escapeHtml(c.location) + "</small></a>") +
        renderSearchGroup("Articles", data.articles, a =>
          '<a href="/articles/' + encodeURIComponent(a.slug) + '">' +
          escapeHtml(a.title) + "<small>" + escapeHtml(a.category) + "</small></a>");
      searchResults.innerHTML = html || '<section><h3>No results</h3><a>Try a different keyword.</a></section>';
    } catch (err) {
      if (err.message !== "login required") searchResults.innerHTML = '<section><h3>Search unavailable</h3></section>';
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimer);
      const q = searchInput.value;
      searchTimer = setTimeout(() => runGlobalSearch(q), 180);
    });
  }

  document.addEventListener("keydown", ev => {
    if (ev.key === "Escape") {
      hideSearch();
      document.querySelectorAll(".modal, .modal-backdrop").forEach(m => {
        m.hidden = true;
        m.style.display = "none";
      });
      document.body.style.overflow = "";
    }
    if (ev.key === "/" && !/input|textarea|select/i.test(document.activeElement.tagName)) {
      ev.preventDefault();
      openSearch();
    }
  });

  /* ---------- auto-submitting filters (Delegated) ---------- */
  document.addEventListener("change", ev => {
    if (ev.target.matches(".auto-submit")) {
      const form = ev.target.form;
      if (form) form.submit();
    }
  });

  document.addEventListener("click", ev => {
    if (!ev.target.closest(".all-filters")) {
      document.querySelectorAll(".all-filters[open]").forEach(d => { d.open = false; });
    }
  });

  /* ---------- saved jobs (Delegated) ---------- */
  function setSaveState(jobId, saved) {
    document.querySelectorAll('.save-btn[data-job-id="' + jobId + '"]').forEach(btn => {
      btn.classList.toggle("saved", saved);
      btn.setAttribute("aria-pressed", String(saved));
      const span = btn.querySelector("span");
      if (span) {
        const liStyle = btn.classList.contains("li-save-btn") || btn.classList.contains("li-btn");
        span.textContent = liStyle ? (saved ? "Saved" : "Save") : (saved ? "SAVED" : "SAVE JOB");
      }
      btn.setAttribute("aria-label", saved ? "Remove saved job" : "Save job");
      btn.setAttribute("title", saved ? "Remove saved job" : "Save job");
    });
  }

  document.addEventListener("click", async ev => {
    const btn = ev.target.closest(".save-btn[data-job-id]");
    if (!btn) return;
    const id = btn.dataset.jobId;
    if (!getLoggedIn()) { loginRedirect(); return; }
    const wasSaved = btn.classList.contains("saved");
    const buttons = Array.from(document.querySelectorAll('.save-btn[data-job-id="' + id + '"]'));
    buttons.forEach(button => { button.disabled = true; });
    setSaveState(id, !wasSaved);
    try {
      const data = await jsonPost("/api/saved/" + id + "/toggle", {});
      setSaveState(id, !!data.saved);
      pageCache.clear();
      showToast(data.saved ? "Job saved to your list." : "Job removed from saved.");
    } catch (err) {
      setSaveState(id, wasSaved);
      if (err.message !== "login required") showToast(err.message, true);
    } finally {
      buttons.forEach(button => { button.disabled = false; });
    }
  });

  /* ---------- followed companies (Delegated) ---------- */
  function setFollowState(companyId, followed) {
    document.querySelectorAll('.follow-btn[data-company-id="' + companyId + '"]').forEach(btn => {
      btn.classList.toggle("followed", followed);
      btn.setAttribute("aria-pressed", String(followed));
      const span = btn.querySelector("span");
      if (span) {
        const liStyle = btn.classList.contains("li-follow-btn") || btn.classList.contains("li-btn");
        span.textContent = liStyle ? (followed ? "Following" : "Follow") : (followed ? "SAVED" : "SAVE");
      }
    });
  }

  document.addEventListener("click", async ev => {
    const btn = ev.target.closest(".follow-btn[data-company-id]");
    if (!btn) return;
    const id = btn.dataset.companyId;
    if (!getLoggedIn()) { loginRedirect(); return; }
    const wasFollowed = btn.classList.contains("followed");
    setFollowState(id, !wasFollowed);
    try {
      const data = await jsonPost("/api/follow/" + id + "/toggle", {});
      setFollowState(id, !!data.followed);
      showToast(data.followed ? "Company followed." : "Company unfollowed.");
    } catch (err) {
      setFollowState(id, wasFollowed);
      if (err.message !== "login required") showToast(err.message, true);
    }
  });

  /* ---------- job application submit (Delegated) ---------- */
  document.addEventListener("submit", async ev => {
    const applyForm = ev.target.closest("#applyForm");
    if (!applyForm) return;
    ev.preventDefault();
    if (!getLoggedIn()) { loginRedirect(); return; }
    const id = applyForm.dataset.jobId;
    const noteField = applyForm.querySelector('[name="note"]');
    const submit = applyForm.querySelector('button[type="submit"]');
    if (submit) { submit.disabled = true; submit.textContent = "Submitting…"; }
    try {
      const data = await jsonPost("/api/apply/" + id, { note: noteField ? noteField.value : "" });
      const success = document.createElement("div");
      success.className = document.body.classList.contains("linkedin-style") ? "li-applied-box" : "applied-success";
      success.innerHTML = '<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"></path></svg>' +
        "<div><strong>Application submitted</strong><span>Track it in your <a href=\"/tracker\">Application Tracker</a>.</span></div>";
      applyForm.replaceWith(success);
      showToast(data.message || "Application submitted.");
    } catch (err) {
      if (submit) { submit.disabled = false; submit.textContent = "Submit Application"; }
      if (err.message !== "login required") showToast(err.message, true);
    }
  });

  /* ---------- save job alert modal (Delegated) ---------- */
  function closeModal(modal) {
    if (modal) modal.hidden = true;
    document.body.style.overflow = "";
  }
  function openModal(modal) {
    if (!modal) return;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    const input = modal.querySelector("input[name='query']");
    if (input) setTimeout(() => input.focus(), 30);
  }

  document.addEventListener("click", ev => {
    const saveAlertBtn = ev.target.closest("#saveAlertBtn");
    if (saveAlertBtn) {
      if (!getLoggedIn()) { loginRedirect(); return; }
      const alertModal = document.getElementById("alertModal");
      const alertForm = document.getElementById("alertForm");
      const queryInput = alertForm && alertForm.querySelector('input[name="query"]');
      if (queryInput && saveAlertBtn.dataset.query) queryInput.value = saveAlertBtn.dataset.query;
      openModal(alertModal);
      return;
    }
    const closeBtn = ev.target.closest("[data-close-modal]");
    if (closeBtn) {
      closeModal(closeBtn.closest(".modal"));
    }
  });

  document.addEventListener("submit", async ev => {
    const alertForm = ev.target.closest("#alertForm");
    if (!alertForm) return;
    ev.preventDefault();
    if (!getLoggedIn()) { loginRedirect(); return; }
    const fd = new FormData(alertForm);
    let filters = {};
    try { filters = JSON.parse(fd.get("filters") || "{}"); } catch (e) { filters = {}; }
    try {
      await jsonPost("/api/alerts", {
        query: fd.get("query") || "My job search",
        frequency: fd.get("frequency") || "Daily",
        filters: filters
      });
      closeModal(document.getElementById("alertModal"));
      showToast("Job alert created. Manage it in your account.");
    } catch (err) {
      if (err.message !== "login required") showToast(err.message, true);
    }
  });

  document.addEventListener("submit", async ev => {
    const editForm = ev.target.closest(".alert-edit-form");
    const deleteForm = ev.target.closest(".alert-delete-form");
    const applicationForm = ev.target.closest(".application-delete-form");
    const jobEditForm = ev.target.closest(".employer-job-edit-form");
    const jobArchiveForm = ev.target.closest(".employer-job-archive-form");

    if (editForm) {
      ev.preventDefault();
      const row = editForm.closest(".alert-row");
      const formData = new FormData(editForm);
      const query = String(formData.get("query") || "").trim();
      const frequency = String(formData.get("frequency") || "Daily");
      const summary = row && row.querySelector(".alert-row-summary");
      const title = summary && summary.querySelector("strong");
      const frequencyText = summary && summary.querySelector("span");
      const oldTitle = title && title.textContent;
      const oldFrequency = frequencyText && frequencyText.textContent;
      const submit = editForm.querySelector('button[type="submit"]');
      if (title) title.textContent = query;
      if (frequencyText) frequencyText.textContent = frequency + " · updated just now";
      if (submit) { submit.disabled = true; submit.textContent = "Saving…"; }
      try {
        await jsonRequest("PATCH", "/api/alerts/" + editForm.dataset.alertId, { query, frequency });
        pageCache.clear();
        const details = editForm.closest("details");
        if (details) details.open = false;
        showToast("Alert updated.");
      } catch (err) {
        if (title) title.textContent = oldTitle;
        if (frequencyText) frequencyText.textContent = oldFrequency;
        if (err.message !== "login required") showToast(err.message, true);
      } finally {
        if (submit) { submit.disabled = false; submit.textContent = "Save changes"; }
      }
      return;
    }

    if (deleteForm || applicationForm) {
      ev.preventDefault();
      const form = deleteForm || applicationForm;
      const id = form.dataset.alertId || form.dataset.applicationId;
      const row = form.closest(deleteForm ? ".alert-row" : "tr");
      if (!row) return;
      row.hidden = true;
      try {
        const endpoint = deleteForm ? "/api/alerts/" + id : "/api/applications/" + id;
        await api(endpoint, { method: "DELETE" });
        pageCache.clear();
        row.remove();
        if (deleteForm) {
          const list = row.closest(".account-alert-list");
          if (list && !list.querySelector(".alert-row")) {
            list.innerHTML = '<p class="muted">No alerts yet. Create one below to keep your search close.</p>';
          }
        } else {
          const tbody = row.parentElement;
          if (tbody && !tbody.querySelector(".application-delete-form")) {
            tbody.innerHTML = '<tr><td colspan="6">No applications yet. Find a role and submit your first application.</td></tr>';
          }
        }
        showToast(deleteForm ? "Alert deleted." : "Application withdrawn.");
      } catch (err) {
        row.hidden = false;
        if (err.message !== "login required") showToast(err.message, true);
      }
      return;
    }

    if (jobEditForm) {
      ev.preventDefault();
      const row = jobEditForm.closest(".employer-job-row");
      const title = row && row.querySelector(".employer-job-title");
      const previousTitle = title && title.textContent;
      const formData = new FormData(jobEditForm);
      const payload = {};
      formData.forEach((value, key) => { payload[key] = value; });
      if (title) title.textContent = payload.title;
      const submit = jobEditForm.querySelector('button[type="submit"]');
      if (submit) { submit.disabled = true; submit.textContent = "Saving…"; }
      try {
        const data = await jsonRequest("PUT", "/api/employer/jobs/" + jobEditForm.dataset.jobId, payload);
        const jobLink = row && row.querySelector(".employer-job-info > a");
        if (jobLink && data.slug) jobLink.href = "/job/" + encodeURIComponent(data.slug) + "/" + jobEditForm.dataset.jobId;
        const selectedCompany = jobEditForm.querySelector('[name="company_slug"]');
        const jobInfo = row && row.querySelector(".employer-job-info > span");
        if (jobInfo) {
          const companyName = selectedCompany && selectedCompany.selectedOptions[0]
            ? selectedCompany.selectedOptions[0].textContent : "";
          jobInfo.textContent = companyName + " · " + (payload.location || "Location flexible");
        }
        const status = row && row.querySelector(".job-status-badge");
        if (status) {
          status.classList.remove("closed");
          status.textContent = "Live";
        }
        const archiveButton = row && row.querySelector(".employer-job-archive-form button");
        if (archiveButton) {
          archiveButton.disabled = false;
          archiveButton.textContent = "Archive";
        }
        pageCache.clear();
        const details = jobEditForm.closest("details");
        if (details) details.open = false;
        showToast("Job updated.");
      } catch (err) {
        if (title) title.textContent = previousTitle;
        if (err.message !== "login required") showToast(err.message, true);
      } finally {
        if (submit) { submit.disabled = false; submit.textContent = "Save changes"; }
      }
      return;
    }

    if (jobArchiveForm) {
      ev.preventDefault();
      const row = jobArchiveForm.closest(".employer-job-row");
      const button = jobArchiveForm.querySelector('button[type="submit"]');
      if (!row) return;
      row.hidden = true;
      if (button) button.disabled = true;
      try {
        await api("/api/employer/jobs/" + jobArchiveForm.dataset.jobId, { method: "DELETE" });
        pageCache.clear();
        row.remove();
        const list = document.querySelector(".employer-job-list");
        if (list && !list.querySelector(".employer-job-row")) {
          list.innerHTML = '<div class="empty-state"><div class="empty-icon">+</div><h3>No open roles</h3><p>Create a listing whenever you are ready to hire again.</p><a class="btn btn-primary" href="/employers#post">Post a job</a></div>';
        }
        showToast("Job archived.");
      } catch (err) {
        row.hidden = false;
        if (button) button.disabled = false;
        if (err.message !== "login required") showToast(err.message, true);
      }
    }
  });

  /* ---------- newsletter (Delegated) ---------- */
  document.addEventListener("submit", async ev => {
    const newsletterForm = ev.target.closest("#newsletterForm");
    if (!newsletterForm) return;
    ev.preventDefault();
    const input = newsletterForm.querySelector('input[name="email"]');
    try {
      const data = await jsonPost("/api/newsletter", { email: input ? input.value : "" });
      newsletterForm.reset();
      showToast(data.message || "You're subscribed.");
    } catch (err) {
      showToast(err.message, true);
    }
  });

  /* ---------- job detail expanders (Delegated) ---------- */
  document.addEventListener("toggle", ev => {
    const details = ev.target.closest(".job-expand");
    if (details && details.open) {
      document.querySelectorAll(".job-expand[open]").forEach(other => {
        if (other !== details) other.open = false;
      });
    }
  }, true);

})();
