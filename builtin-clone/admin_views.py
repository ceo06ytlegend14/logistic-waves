import html
import re
from datetime import datetime
import db

def e(value):
    return html.escape(str(value if value is not None else ""), quote=True)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")

def _csrf_field() -> str:
    """Return a hidden CSRF input using the current request token set by views._set_csrf()."""
    try:
        import views as _v
        tok = _v._get_csrf()
        if tok:
            return f"<input type='hidden' name='_csrf' value='{html.escape(tok, quote=True)}'>"
    except Exception:
        pass
    return ""

def circular_gauge_svg(percent, color="#3874ff"):
    circ = 175.93
    offset = circ - (percent / 100.0) * circ
    return (
        '<div class="stat-gauge-wrap">'
        '<svg class="stat-gauge-svg" viewBox="0 0 72 72">'
        '<circle class="stat-gauge-bg" cx="36" cy="36" r="28"></circle>'
        '<circle class="stat-gauge-fill" cx="36" cy="36" r="28"'
        ' stroke="' + color + '"'
        ' stroke-dasharray="' + f"{circ:.2f}" + '"'
        ' stroke-dashoffset="' + f"{offset:.2f}" + '"></circle>'
        '</svg>'
        '<span class="stat-gauge-val">' + str(percent) + '%</span>'
        '</div>'
    )

def mini_wave_svg(color="#10b981"):
    return (
        '<svg class="trend-wave" viewBox="0 0 50 18" fill="none">'
        '<path d="M1 14 C 10 16, 15 4, 25 10 C 35 15, 40 2, 49 4"'
        ' stroke="' + color + '" stroke-width="2" stroke-linecap="round"/>'
        '</svg>'
    )

def status_pill(status):
    colors = {
        "Applied":   ("pill-blue",   "fa-clock"),
        "Reviewing": ("pill-amber",  "fa-eye"),
        "Interview": ("pill-purple", "fa-calendar-check"),
        "Offer":     ("pill-green",  "fa-circle-check"),
        "Rejected":  ("pill-red",    "fa-xmark"),
    }
    cls, ico = colors.get(status, ("pill-blue", "fa-circle"))
    return '<span class="pill-badge ' + cls + '"><i class="fa-solid ' + ico + '"></i> ' + e(status) + '</span>'

def render_image_uploader_field(target_id, preview_id, label="Article Image / Cover", current_val=""):
    val = e(current_val or "/static/images/fw_today_1.jpg")
    return (
        "<div class='form-group'>"
        "<label class='form-label' style='display:flex;justify-content:space-between;align-items:center;'>"
        "<span><i class='fa-solid fa-image' style='color:#3874ff;'></i> " + label + "</span>"
        "<span style='font-size:11px;font-weight:600;color:#64748b;'>PNG, JPG, WEBP, SVG</span>"
        "</label>"
        "<div style='display:flex;gap:12px;align-items:flex-start;background:#f8fafc;padding:12px;border:1px solid #e2e8f0;border-radius:10px;'>"
        "<div style='width:110px;height:75px;border-radius:8px;border:1px solid #cbd5e1;background:#ffffff;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;'>"
        "<img id='" + preview_id + "' src='" + val + "' alt='Thumbnail preview' decoding='async' style='width:100%;height:100%;object-fit:cover;display:block;' onerror=\"this.onerror=null;this.src='/static/images/fw_today_1.jpg'\">"
        "</div>"
        "<div style='flex:1;display:flex;flex-direction:column;gap:8px;'>"
        "<div style='display:flex;gap:8px;'>"
        "<label style='flex:1;cursor:pointer;background:#eff6ff;border:1px dashed #3874ff;color:#1d4ed8;padding:7px 10px;border-radius:8px;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:6px;transition:0.2s;' title='Choose from Computer'>"
        "<i class='fa-solid fa-cloud-arrow-up'></i> Upload from Device"
        "<input type='file' accept='image/*' style='display:none;' onchange=\"handleImageFileUpload(this, '" + target_id + "', '" + preview_id + "')\">"
        "</label>"
        "<button type='button' onclick=\"clearImageUpload('" + target_id + "', '" + preview_id + "')\" style='padding:7px 12px;border-radius:8px;border:1px solid #fee2e2;background:#fff5f5;color:#ef4444;font-size:12px;font-weight:600;cursor:pointer;' title='Remove Image'>"
        "<i class='fa-solid fa-trash-can'></i> Clear"
        "</button>"
        "</div>"
        "<div style='display:flex;gap:6px;'>"
        "<input class='form-control' id='" + target_id + "' name='thumb' value='" + val + "' placeholder='Or paste web image URL (https://...)' style='font-size:12px;padding:6px 10px;' oninput=\"updateImagePreview(this.value, '" + preview_id + "')\">"
        "<button type='button' onclick=\"updateImagePreview(document.getElementById('" + target_id + "').value, '" + preview_id + "')\" style='padding:6px 12px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:8px;font-size:12px;font-weight:600;color:#334155;cursor:pointer;white-space:nowrap;'>"
        "<i class='fa-solid fa-magnifying-glass'></i> Fetch"
        "</button>"
        "</div>"
        "<div style='display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:2px;font-size:11.5px;color:#64748b;'>"
        "<span>Presets:</span>"
        "<button type='button' onclick=\"setPresetImage('" + target_id + "', '" + preview_id + "', '/static/images/fw_today_1.jpg')\" style='border:1px solid #e2e8f0;background:#fff;padding:2px 7px;border-radius:5px;font-size:11px;cursor:pointer;'>Port &amp; Ships</button>"
        "<button type='button' onclick=\"setPresetImage('" + target_id + "', '" + preview_id + "', '/static/images/fw_today_2.svg')\" style='border:1px solid #e2e8f0;background:#fff;padding:2px 7px;border-radius:5px;font-size:11px;cursor:pointer;'>Aviation</button>"
        "<button type='button' onclick=\"setPresetImage('" + target_id + "', '" + preview_id + "', '/static/images/fw_today_3.jpg')\" style='border:1px solid #e2e8f0;background:#fff;padding:2px 7px;border-radius:5px;font-size:11px;cursor:pointer;'>Container</button>"
        "<button type='button' onclick=\"setPresetImage('" + target_id + "', '" + preview_id + "', '/static/images/fw_today_4.jpg')\" style='border:1px solid #e2e8f0;background:#fff;padding:2px 7px;border-radius:5px;font-size:11px;cursor:pointer;'>Electric</button>"
        "</div>"
        "</div></div></div>"
    )

def render_edit_modals(all_companies):
    company_options = "".join([
        "<option value='" + e(c['slug']) + "'>" + e(c['name']) + "</option>"
        for c in all_companies
    ])
    return (
        "<!-- Article/Video Edit Modal -->\n"
        "<div class='admin-modal-backdrop' id='edit-article-modal'>\n"
        "<div class='admin-modal-dialog'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-pen-to-square' style='color:#3874ff;'></i> Edit Article / Video</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/articles/update' class='admin-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-article-id'>\n"
        "<input type='hidden' name='tab' id='edit-article-tab' value='articles'>\n"
        f"{_csrf_field()}\n"
        "<div class='form-group'><label class='form-label'>Title *</label><input class='form-control' name='title' id='edit-article-title' required></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Category</label><input class='form-control' name='category' id='edit-article-category'></div>\n"
        "<div class='form-group'><label class='form-label'>Tag / Theme</label><input class='form-control' name='tag' id='edit-article-tag'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Author</label><input class='form-control' name='author' id='edit-article-author'></div>\n"
        "<div class='form-group'><label class='form-label'>Guest (Video)</label><input class='form-control' name='guest' id='edit-article-guest'></div>\n"
        "<div class='form-group'><label class='form-label'>Read Time</label><input class='form-control' name='read_time' id='edit-article-read-time'></div>\n"
        "</div>\n"
        "<div class='form-group'><label class='form-label'>Duration (Video only)</label><input class='form-control' name='duration' id='edit-article-duration' placeholder='e.g. 15:00 min'></div>\n"
        + render_image_uploader_field('edit-article-thumb', 'edit-article-preview', 'Featured Article / Video Cover Image', '') +
        "<div class='form-group'><label class='form-label'>Excerpt / Summary</label><textarea class='form-control' name='excerpt' id='edit-article-excerpt' rows='2'></textarea></div>\n"
        "<div class='form-group'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:8px;'>"
        "<label class='form-label' style='margin:0;'>Body Content (Markdown &amp; Galleries Supported)</label>"
        "<div style='display:flex;gap:6px;'>"
        "<button type='button' onclick=\"insertImageMarkdown('edit-article-body', 'single')\" style='border:1px solid #cbd5e1;background:#fff;color:#3874ff;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 1 full-width photo'>"
        "<i class='fa-solid fa-image'></i> + 1 Photo"
        "</button>"
        "<button type='button' onclick=\"insertImageMarkdown('edit-article-body', 'gallery2')\" style='border:1px solid #cbd5e1;background:#fff;color:#10b981;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 2 photos side-by-side'>"
        "<i class='fa-solid fa-table-columns'></i> + 2-Photo Gallery"
        "</button>"
        "<button type='button' onclick=\"insertImageMarkdown('edit-article-body', 'gallery3')\" style='border:1px solid #cbd5e1;background:#fff;color:#8b5cf6;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 3 photos gallery grid'>"
        "<i class='fa-solid fa-table-cells'></i> + 3-Photo Grid"
        "</button>"
        "</div></div>"
        "<textarea class='form-control' name='body' id='edit-article-body' rows='6'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save'><i class='fa-solid fa-check'></i> Save Changes</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Job Edit Modal -->\n"
        "<div class='admin-modal-backdrop' id='edit-job-modal'>\n"
        "<div class='admin-modal-dialog'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-briefcase' style='color:#10b981;'></i> Edit Job Listing</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/jobs/update' class='admin-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-job-id'>\n"
        "<input type='hidden' name='tab' id='edit-job-tab' value='jobs'>\n"
        f"{_csrf_field()}\n"
        "<div class='form-group'><label class='form-label'>Job Title *</label><input class='form-control' name='title' id='edit-job-title' required></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Company *</label><select class='form-control' name='company_slug' id='edit-job-company-slug'>" + company_options + "</select></div>\n"
        "<div class='form-group'><label class='form-label'>Category</label><input class='form-control' name='category' id='edit-job-category'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Workplace</label><select class='form-control' name='workplace' id='edit-job-workplace'><option value='Hybrid'>Hybrid</option><option value='Fully Remote'>Fully Remote</option><option value='On Site'>On Site</option></select></div>\n"
        "<div class='form-group'><label class='form-label'>Level</label><input class='form-control' name='level' id='edit-job-level' placeholder='e.g. Mid-Senior'></div>\n"
        "<div class='form-group'><label class='form-label'>Location</label><input class='form-control' name='location' id='edit-job-location'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Salary Min ($)</label><input type='number' class='form-control' name='salary_min' id='edit-job-salary-min'></div>\n"
        "<div class='form-group'><label class='form-label'>Salary Max ($)</label><input type='number' class='form-control' name='salary_max' id='edit-job-salary-max'></div>\n"
        "<div class='form-group'><label class='form-label'>Display (e.g. $50k-$80k)</label><input class='form-control' name='salary_display' id='edit-job-salary-display'></div>\n"
        "</div>\n"
        "<div class='form-group'><label class='form-label'>Skills &amp; Stack</label><input class='form-control' name='skills' id='edit-job-skills' placeholder='Comma separated tags'></div>\n"
        "<div class='form-group'><label class='form-label'>Job Description</label><textarea class='form-control' name='description' id='edit-job-description' rows='3'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save' style='background:#10b981;border-color:#10b981;'><i class='fa-solid fa-check'></i> Save Changes</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Company Edit Modal -->\n"
        "<div class='admin-modal-backdrop' id='edit-company-modal'>\n"
        "<div class='admin-modal-dialog'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-building' style='color:#8b5cf6;'></i> Edit Company</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/companies/update' class='admin-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-company-id'>\n"
        "<input type='hidden' name='tab' id='edit-company-tab' value='companies'>\n"
        f"{_csrf_field()}\n"
        "<div class='form-group'><label class='form-label'>Company Name *</label><input class='form-control' name='name' id='edit-company-name' required></div>\n"
        "<div class='form-group'><label class='form-label'>Tagline</label><input class='form-control' name='tagline' id='edit-company-tagline'></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Industries</label><input class='form-control' name='industries' id='edit-company-industries'></div>\n"
        "<div class='form-group'><label class='form-label'>Location</label><input class='form-control' name='location' id='edit-company-location'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Employees</label><input type='number' class='form-control' name='employees' id='edit-company-employees'></div>\n"
        "<div class='form-group'><label class='form-label'>Brand Color</label><input class='form-control' name='color' id='edit-company-color'></div>\n"
        "<div class='form-group'><label class='form-label'>Website</label><input class='form-control' name='website' id='edit-company-website'></div>\n"
        "</div>\n"
        "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' id='edit-company-description' rows='3'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save' style='background:#8b5cf6;border-color:#8b5cf6;'><i class='fa-solid fa-check'></i> Save Changes</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Salary Edit Modal -->\n"
        "<div class='admin-modal-backdrop' id='edit-salary-modal'>\n"
        "<div class='admin-modal-dialog'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-chart-bar' style='color:#10b981;'></i> Edit Salary Benchmark</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/salaries/update' class='admin-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-salary-id'>\n"
        "<input type='hidden' name='tab' id='edit-salary-tab' value='salaries'>\n"
        f"{_csrf_field()}\n"
        "<div class='form-group'><label class='form-label'>Job Title *</label><input class='form-control' name='title' id='edit-salary-title' required></div>\n"
        "<div class='form-group'><label class='form-label'>Category</label><input class='form-control' name='category' id='edit-salary-category'></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;'>\n"
        "<div class='form-group'><label class='form-label'>Median ($)</label><input type='number' class='form-control' name='median' id='edit-salary-median'></div>\n"
        "<div class='form-group'><label class='form-label'>Low ($)</label><input type='number' class='form-control' name='low' id='edit-salary-low'></div>\n"
        "<div class='form-group'><label class='form-label'>High ($)</label><input type='number' class='form-control' name='high' id='edit-salary-high'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Samples (reports)</label><input type='number' class='form-control' name='samples' id='edit-salary-samples'></div>\n"
        "<div class='form-group'><label class='form-label'>Trend</label><input class='form-control' name='trend' id='edit-salary-trend'></div>\n"
        "</div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save' style='background:#10b981;border-color:#10b981;'><i class='fa-solid fa-check'></i> Save Changes</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<script>\n"
        "function closeAllModals() {\n"
        "  document.querySelectorAll('.admin-modal-backdrop').forEach(function(m) { m.classList.remove('active'); });\n"
        "}\n"
        "document.querySelectorAll('.admin-modal-backdrop').forEach(function(m) {\n"
        "  m.addEventListener('click', function(e) { if(e.target === this) closeAllModals(); });\n"
        "});\n"
        "document.addEventListener('keydown', function(e) { if(e.key === 'Escape') closeAllModals(); });\n"
        "function openArticleEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-article-id').value = d.id || '';\n"
        "  document.getElementById('edit-article-tab').value = d.tab || 'articles';\n"
        "  document.getElementById('edit-article-title').value = d.title || '';\n"
        "  document.getElementById('edit-article-category').value = d.category || '';\n"
        "  document.getElementById('edit-article-author').value = d.author || '';\n"
        "  document.getElementById('edit-article-tag').value = d.tag || '';\n"
        "  document.getElementById('edit-article-read-time').value = d.readTime || '';\n"
        "  document.getElementById('edit-article-guest').value = d.guest || '';\n"
        "  document.getElementById('edit-article-duration').value = d.duration || '';\n"
        "  document.getElementById('edit-article-thumb').value = d.thumb || '';\n"
        "  updateImagePreview(d.thumb, 'edit-article-preview');\n"
        "  document.getElementById('edit-article-excerpt').value = d.excerpt || '';\n"
        "  document.getElementById('edit-article-body').value = d.body || '';\n"
        "  document.getElementById('edit-article-modal').classList.add('active');\n"
        "}\n"
        "function handleImageFileUpload(fileInput, targetInputId, previewImgId) {\n"
        "  if (!fileInput.files || !fileInput.files[0]) return;\n"
        "  var file = fileInput.files[0];\n"
        "  var reader = new FileReader();\n"
        "  reader.onload = function(e) {\n"
        "    var rawData = e.target.result;\n"
        "    var img = new Image();\n"
        "    img.onload = function() {\n"
        "      var maxW = 1200;\n"
        "      var maxH = 800;\n"
        "      var w = img.width;\n"
        "      var h = img.height;\n"
        "      if (w > maxW || h > maxH) {\n"
        "        if (w / maxW > h / maxH) { h = Math.round(h * (maxW / w)); w = maxW; }\n"
        "        else { w = Math.round(w * (maxH / h)); h = maxH; }\n"
        "      }\n"
        "      var canvas = document.createElement('canvas');\n"
        "      canvas.width = w; canvas.height = h;\n"
        "      var ctx = canvas.getContext('2d');\n"
        "      ctx.drawImage(img, 0, 0, w, h);\n"
        "      var optimized = canvas.toDataURL('image/jpeg', 0.85);\n"
        "      document.getElementById(targetInputId).value = optimized;\n"
        "      var prev = document.getElementById(previewImgId);\n"
        "      if (prev) prev.src = optimized;\n"
        "    };\n"
        "    img.src = rawData;\n"
        "  };\n"
        "  reader.readAsDataURL(file);\n"
        "}\n"
        "function updateImagePreview(url, previewImgId) {\n"
        "  var prev = document.getElementById(previewImgId);\n"
        "  if (!prev) return;\n"
        "  if (!url || !url.trim()) {\n"
        "    prev.src = '/static/images/fw_today_1.jpg';\n"
        "  } else {\n"
        "    prev.src = url.trim();\n"
        "  }\n"
        "}\n"
        "function clearImageUpload(targetInputId, previewImgId) {\n"
        "  document.getElementById(targetInputId).value = '';\n"
        "  var prev = document.getElementById(previewImgId);\n"
        "  if (prev) prev.src = 'data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"100\" height=\"70\" viewBox=\"0 0 100 70\"><rect width=\"100\" height=\"70\" fill=\"%23f1f5f9\"/><text x=\"50\" y=\"38\" font-family=\"sans-serif\" font-size=\"11\" fill=\"%2394a3b8\" text-anchor=\"middle\">No Image</text></svg>';\n"
        "}\n"
        "function setPresetImage(targetInputId, previewImgId, url) {\n"
        "  document.getElementById(targetInputId).value = url;\n"
        "  updateImagePreview(url, previewImgId);\n"
        "}\n"
        "function insertImageMarkdown(targetBodyId, mode) {\n"
        "  var txt = document.getElementById(targetBodyId);\n"
        "  if (!txt) return;\n"
        "  if (mode === 'gallery2') {\n"
        "    var md = '\\n\\n![Berth Operations & Gantry Crane](https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80)\\n![Automated Cargo Vessel](https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80)\\n\\n';\n"
        "    txt.value += md;\n"
        "    txt.focus();\n"
        "    return;\n"
        "  }\n"
        "  if (mode === 'gallery3') {\n"
        "    var md = '\\n\\n![Deepwater Quay](https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80)\\n![Smart Container Yard](https://images.unsplash.com/photo-1542296332-2e4473faf563?auto=format&fit=crop&w=800&q=80)\\n![Intermodal Rail Connection](https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80)\\n\\n';\n"
        "    txt.value += md;\n"
        "    txt.focus();\n"
        "    return;\n"
        "  }\n"
        "  var url = prompt('Enter Image URL to insert into article:', 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80');\n"
        "  if (!url) return;\n"
        "  var cap = prompt('Enter caption for this image (optional):', 'Port operations and logistics facility');\n"
        "  var md = '\\n\\n![' + (cap || 'Article Image') + '](' + url + ')\\n\\n';\n"
        "  txt.value += md;\n"
        "  txt.focus();\n"
        "}\n"
        "function openJobEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-job-id').value = d.id || '';\n"
        "  document.getElementById('edit-job-tab').value = d.tab || 'jobs';\n"
        "  document.getElementById('edit-job-title').value = d.title || '';\n"
        "  document.getElementById('edit-job-company-slug').value = d.companySlug || '';\n"
        "  document.getElementById('edit-job-category').value = d.category || '';\n"
        "  document.getElementById('edit-job-level').value = d.level || '';\n"
        "  document.getElementById('edit-job-workplace').value = d.workplace || '';\n"
        "  document.getElementById('edit-job-location').value = d.location || '';\n"
        "  document.getElementById('edit-job-salary-min').value = d.salaryMin || '';\n"
        "  document.getElementById('edit-job-salary-max').value = d.salaryMax || '';\n"
        "  document.getElementById('edit-job-salary-display').value = d.salaryDisplay || '';\n"
        "  document.getElementById('edit-job-skills').value = d.skills || '';\n"
        "  document.getElementById('edit-job-description').value = d.description || '';\n"
        "  document.getElementById('edit-job-modal').classList.add('active');\n"
        "}\n"
        "function openCompanyEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-company-id').value = d.id || '';\n"
        "  document.getElementById('edit-company-tab').value = d.tab || 'companies';\n"
        "  document.getElementById('edit-company-name').value = d.name || '';\n"
        "  document.getElementById('edit-company-tagline').value = d.tagline || '';\n"
        "  document.getElementById('edit-company-industries').value = d.industries || '';\n"
        "  document.getElementById('edit-company-location').value = d.location || '';\n"
        "  document.getElementById('edit-company-employees').value = d.employees || '';\n"
        "  document.getElementById('edit-company-color').value = d.color || '#3874ff';\n"
        "  document.getElementById('edit-company-website').value = d.website || '';\n"
        "  document.getElementById('edit-company-description').value = d.description || '';\n"
        "  document.getElementById('edit-company-modal').classList.add('active');\n"
        "}\n"
        "function openSalaryEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-salary-id').value = d.id || '';\n"
        "  document.getElementById('edit-salary-tab').value = d.tab || 'salaries';\n"
        "  document.getElementById('edit-salary-title').value = d.title || '';\n"
        "  document.getElementById('edit-salary-category').value = d.category || '';\n"
        "  document.getElementById('edit-salary-median').value = d.median || '';\n"
        "  document.getElementById('edit-salary-low').value = d.low || '';\n"
        "  document.getElementById('edit-salary-high').value = d.high || '';\n"
        "  document.getElementById('edit-salary-samples').value = d.samples || '';\n"
        "  document.getElementById('edit-salary-trend').value = d.trend || '';\n"
        "  document.getElementById('edit-salary-modal').classList.add('active');\n"
        "}\n"
        "function toggleAdminSidebar() {\n"
        "  var sb = document.getElementById('adminSidebar');\n"
        "  var ov = document.getElementById('adminMobileOverlay');\n"
        "  if (!sb) return;\n"
        "  var isOpen = sb.classList.contains('mobile-open');\n"
        "  if (isOpen) {\n"
        "    sb.classList.remove('mobile-open');\n"
        "    if (ov) ov.classList.remove('active');\n"
        "  } else {\n"
        "    sb.classList.add('mobile-open');\n"
        "    if (ov) ov.classList.add('active');\n"
        "  }\n"
        "}\n"
        "function closeAdminSidebar() {\n"
        "  var sb = document.getElementById('adminSidebar');\n"
        "  var ov = document.getElementById('adminMobileOverlay');\n"
        "  if (sb) sb.classList.remove('mobile-open');\n"
        "  if (ov) ov.classList.remove('active');\n"
        "}\n"
        "function filterAdminTable(query) {\n"
        "  var q = (query || '').trim().toLowerCase();\n"
        "  document.querySelectorAll('.clean-table tbody').forEach(function(tbody) {\n"
        "    var rows = Array.from(tbody.querySelectorAll('tr:not(.admin-empty-filter-row)'));\n"
        "    var shown = 0;\n"
        "    rows.forEach(function(r) {\n"
        "      var match = !q || r.textContent.toLowerCase().indexOf(q) !== -1;\n"
        "      r.style.display = match ? '' : 'none';\n"
        "      if (match) shown++;\n"
        "    });\n"
        "    var emptyRow = tbody.querySelector('.admin-empty-filter-row');\n"
        "    if (q && shown === 0 && rows.length > 0) {\n"
        "      if (!emptyRow) {\n"
        "        emptyRow = document.createElement('tr');\n"
        "        emptyRow.className = 'admin-empty-filter-row';\n"
        "        emptyRow.innerHTML = \"<td colspan='8' style='text-align:center;padding:24px;color:#64748b;'>No visible rows match your filter. Press <strong>Enter</strong> to search the full database.</td>\";\n"
        "        tbody.appendChild(emptyRow);\n"
        "      }\n"
        "      emptyRow.style.display = '';\n"
        "    } else if (emptyRow) {\n"
        "      emptyRow.style.display = 'none';\n"
        "    }\n"
        "  });\n"
        "}\n"
        "function toggleAdminNotifMenu(ev) {\n"
        "  if (ev) ev.preventDefault();\n"
        "  var m = document.getElementById('adminNotifMenu');\n"
        "  var u = document.getElementById('adminUserMenu');\n"
        "  if (u) u.style.display = 'none';\n"
        "  if (m) m.style.display = m.style.display === 'block' ? 'none' : 'block';\n"
        "}\n"
        "function toggleAdminUserMenu() {\n"
        "  var m = document.getElementById('adminUserMenu');\n"
        "  var n = document.getElementById('adminNotifMenu');\n"
        "  if (n) n.style.display = 'none';\n"
        "  if (m) m.style.display = m.style.display === 'block' ? 'none' : 'block';\n"
        "}\n"
        "document.addEventListener('click', function(ev) {\n"
        "  if (!ev.target.closest('#adminNotifWrap')) {\n"
        "    var n = document.getElementById('adminNotifMenu');\n"
        "    if (n) n.style.display = 'none';\n"
        "  }\n"
        "  if (!ev.target.closest('#adminUserWrap')) {\n"
        "    var u = document.getElementById('adminUserMenu');\n"
        "    if (u) u.style.display = 'none';\n"
        "  }\n"
        "});\n"
        "</script>\n"
    )

def _render_pagination(tab: str, page: int, total: int, per_page: int = 20, q: str = "") -> str:
    """Render server-side pagination controls for admin tables."""
    import urllib.parse as _up
    q_suffix = f"&amp;q={_up.quote(q)}" if q else ""
    total_pages = max(1, (total + per_page - 1) // per_page)
    if total_pages <= 1:
        return ""
    page = max(1, min(page, total_pages))
    prev_btn = (
        f"<a href='/admin?tab={e(tab)}&amp;page={page - 1}{q_suffix}' class='btn-ctrl btn-ctrl-light' style='padding:5px 12px;font-size:12px;'>&laquo; Prev</a>"
        if page > 1 else
        "<span class='btn-ctrl btn-ctrl-light' style='padding:5px 12px;font-size:12px;opacity:.45;cursor:not-allowed;'>&laquo; Prev</span>"
    )
    next_btn = (
        f"<a href='/admin?tab={e(tab)}&amp;page={page + 1}{q_suffix}' class='btn-ctrl btn-ctrl-light' style='padding:5px 12px;font-size:12px;'>Next &raquo;</a>"
        if page < total_pages else
        "<span class='btn-ctrl btn-ctrl-light' style='padding:5px 12px;font-size:12px;opacity:.45;cursor:not-allowed;'>Next &raquo;</span>"
    )
    return (
        "<div style='display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-top:1px solid #e2e8f0;'>"
        f"<span style='font-size:12.5px;color:#64748b;'>Page <strong>{page}</strong> of <strong>{total_pages}</strong> ({total} total)</span>"
        f"<div style='display:flex;gap:8px;'>{prev_btn}{next_btn}</div>"
        "</div>"
    )


def render_admin_dashboard(conn, user, message="", error="", tab="overview", page=1, q=""):
    page = max(1, int(page or 1))
    q = (q or "").strip()
    per_page = 20
    offset = (page - 1) * per_page

    # Batched counts — single round-trip instead of 5+ separate queries
    _c = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM jobs WHERE status='active') as jobs,
            (SELECT COUNT(*) FROM jobs) as total_jobs,
            (SELECT COUNT(*) FROM companies) as companies,
            (SELECT COUNT(*) FROM articles) as articles,
            (SELECT COUNT(*) FROM jobs WHERE is_remote=1 AND status='active') as remote,
            (SELECT COUNT(*) FROM users) as users,
            (SELECT COUNT(*) FROM articles WHERE tag='Logistic Waves Today' OR is_today=1) as today_videos,
            (SELECT COUNT(*) FROM applications) as applications,
            (SELECT COUNT(*) FROM subscribers) as subscribers
    """).fetchone()
    counts = dict(_c)
    today_videos_count = counts.pop("today_videos", 0)
    applications_count = counts.pop("applications", 0)
    subscribers_count  = counts.pop("subscribers", 0)
    total_jobs_count   = counts.pop("total_jobs", 0)
    users_count        = counts.get("users", 0)

    like = f"%{db._escape_like(q)}%" if q else None
    tab_total = None

    # Lazy-tab querying: only fetch rows needed for the active tab (with optional ?q= server search)
    today_videos = []
    all_articles = []
    all_jobs = []
    all_companies = []
    all_users = []
    all_applications = []
    all_subscribers = []
    all_salaries = []

    if tab in ("overview", "videos"):
        v_limit = 5 if tab == "overview" else 100
        if like and tab == "videos":
            today_videos = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, author, guest, duration, thumb, published, category, excerpt, body, tag, is_today, read_time "
                "FROM articles WHERE (tag='Logistic Waves Today' OR is_today=1) AND (title LIKE ? ESCAPE '\\' OR guest LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\') "
                "ORDER BY id DESC LIMIT ?",
                (like, like, like, v_limit)
            ).fetchall()]
        else:
            today_videos = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, author, guest, duration, thumb, published, category, excerpt, body, tag, is_today, read_time "
                "FROM articles WHERE tag='Logistic Waves Today' OR is_today=1 ORDER BY id DESC LIMIT ?",
                (v_limit,)
            ).fetchall()]

    if tab == "articles":
        if like:
            tab_total = conn.execute(
                "SELECT COUNT(*) FROM articles WHERE title LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\' OR author LIKE ? ESCAPE '\\'",
                (like, like, like)
            ).fetchone()[0]
            all_articles = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, category, tag, author, published, is_today, read_time, duration, guest, thumb, excerpt, body "
                "FROM articles WHERE title LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\' OR author LIKE ? ESCAPE '\\' "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (like, like, like, per_page, offset)
            ).fetchall()]
        else:
            tab_total = counts["articles"]
            all_articles = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, category, tag, author, published, is_today, read_time, duration, guest, thumb, excerpt, body "
                "FROM articles ORDER BY id DESC LIMIT ? OFFSET ?",
                (per_page, offset)
            ).fetchall()]

    if tab in ("overview", "jobs"):
        j_limit = 5 if tab == "overview" else per_page
        j_offset = 0 if tab == "overview" else offset
        if like and tab == "jobs":
            total_jobs_count = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE title LIKE ? ESCAPE '\\' OR company_name LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\'",
                (like, like, like)
            ).fetchone()[0]
            all_jobs = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, company_id, company_slug, company_name, category, level, workplace, location, salary_min, salary_max, salary_display, skills, description, posted_at "
                "FROM jobs WHERE title LIKE ? ESCAPE '\\' OR company_name LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\' "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (like, like, like, j_limit, j_offset)
            ).fetchall()]
        else:
            all_jobs = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, company_id, company_slug, company_name, category, level, workplace, location, salary_min, salary_max, salary_display, skills, description, posted_at "
                "FROM jobs ORDER BY id DESC LIMIT ? OFFSET ?",
                (j_limit, j_offset)
            ).fetchall()]

    if tab == "companies":
        if like:
            tab_total = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE name LIKE ? ESCAPE '\\' OR industries LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\'",
                (like, like, like)
            ).fetchone()[0]
            all_companies = [dict(r) for r in conn.execute(
                "SELECT id, slug, name, initials, color, tagline, industries, location, employees, website, description, open_jobs "
                "FROM companies WHERE name LIKE ? ESCAPE '\\' OR industries LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\' "
                "ORDER BY name ASC LIMIT ? OFFSET ?",
                (like, like, like, per_page, offset)
            ).fetchall()]
        else:
            tab_total = counts["companies"]
            all_companies = [dict(r) for r in conn.execute(
                "SELECT id, slug, name, initials, color, tagline, industries, location, employees, website, description, open_jobs "
                "FROM companies ORDER BY name ASC LIMIT ? OFFSET ?",
                (per_page, offset)
            ).fetchall()]
    elif tab in ("overview", "jobs"):
        all_companies = [dict(r) for r in conn.execute(
            "SELECT slug, name FROM companies ORDER BY name ASC"
        ).fetchall()]

    if tab == "users":
        if like:
            all_users = [dict(r) for r in conn.execute(
                "SELECT id, name, email, role, created_at FROM users WHERE name LIKE ? ESCAPE '\\' OR email LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT 100",
                (like, like)
            ).fetchall()]
        else:
            all_users = [dict(r) for r in conn.execute(
                "SELECT id, name, email, role, created_at FROM users ORDER BY id DESC LIMIT 100"
            ).fetchall()]

    if tab == "applications":
        try:
            if like:
                applications_count = conn.execute(
                    "SELECT COUNT(*) FROM applications a JOIN jobs j ON a.job_id=j.id JOIN users u ON a.user_id=u.id "
                    "WHERE j.title LIKE ? ESCAPE '\\' OR u.name LIKE ? ESCAPE '\\' OR u.email LIKE ? ESCAPE '\\'",
                    (like, like, like)
                ).fetchone()[0]
                all_applications = [dict(r) for r in conn.execute(
                    "SELECT a.id, a.status, a.note, a.created_at,"
                    " j.title as job_title, j.id as job_id, j.slug as job_slug,"
                    " u.name as user_name, u.email as user_email"
                    " FROM applications a"
                    " JOIN jobs j ON a.job_id=j.id"
                    " JOIN users u ON a.user_id=u.id"
                    " WHERE j.title LIKE ? ESCAPE '\\' OR u.name LIKE ? ESCAPE '\\' OR u.email LIKE ? ESCAPE '\\'"
                    " ORDER BY a.id DESC LIMIT ? OFFSET ?",
                    (like, like, like, per_page, offset)
                ).fetchall()]
            else:
                all_applications = [dict(r) for r in conn.execute(
                    "SELECT a.id, a.status, a.note, a.created_at,"
                    " j.title as job_title, j.id as job_id, j.slug as job_slug,"
                    " u.name as user_name, u.email as user_email"
                    " FROM applications a"
                    " JOIN jobs j ON a.job_id=j.id"
                    " JOIN users u ON a.user_id=u.id"
                    " ORDER BY a.id DESC LIMIT ? OFFSET ?",
                    (per_page, offset)
                ).fetchall()]
        except Exception:
            pass

    if tab == "subscribers":
        if like:
            all_subscribers = [dict(r) for r in conn.execute(
                "SELECT id, email, created_at FROM subscribers WHERE email LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT 100",
                (like,)
            ).fetchall()]
        else:
            all_subscribers = [dict(r) for r in conn.execute(
                "SELECT id, email, created_at FROM subscribers ORDER BY id DESC LIMIT 100"
            ).fetchall()]

    if tab == "salaries":
        if like:
            all_salaries = [dict(r) for r in conn.execute(
                "SELECT id, title, category, median, low, high, samples, trend "
                "FROM salaries WHERE title LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT 100",
                (like, like)
            ).fetchall()]
        else:
            all_salaries = [dict(r) for r in conn.execute(
                "SELECT id, title, category, median, low, high, samples, trend "
                "FROM salaries ORDER BY id DESC LIMIT 100"
            ).fetchall()]

    # Alert banner
    alert_html = ""
    if message:
        alert_html = '<div class="admin-alert admin-alert-success"><i class="fa-solid fa-circle-check"></i> ' + e(message) + '</div>'
    elif error:
        alert_html = '<div class="admin-alert admin-alert-error"><i class="fa-solid fa-triangle-exclamation"></i> ' + e(error) + '</div>'

    def nav_active(t):
        return "sidebar-link active" if tab == t else "sidebar-link"

    def _empty_row(colspan, default_msg):
        if q:
            return (
                f"<tr><td colspan='{colspan}' style='text-align:center;padding:32px;color:#64748b;'>"
                f"No results match <strong>&ldquo;{e(q)}&rdquo;</strong>. "
                f"<a href='/admin?tab={e(tab)}' style='color:#3874ff;font-weight:700;margin-left:6px;'>Clear search</a>"
                "</td></tr>"
            )
        return f"<tr><td colspan='{colspan}' style='text-align:center;padding:32px;color:#94a3b8;'>{default_msg}</td></tr>"

    def render_video_row(v, tab_ctx):
        thumb = e(v['thumb'] or '/static/images/fw_today_1.jpg')
        is_overview = (tab_ctx == "overview")
        second_col = (
            "<td style='min-width:220px;'><strong>" + e(v['title']) + "</strong><br>"
            "<small style='color:#64748b;'>Guest: " + e(v['guest'] or 'N/A') + "</small></td>"
            "<td><span class='pill-badge pill-blue'>" + e(v['category'] or 'Video') + "</span></td>"
            if is_overview else
            "<td><strong>" + e(v['title']) + "</strong><br><small style='color:#64748b;'>/" + e(v['slug']) + "</small></td>"
            "<td><strong style='color:#3874ff;'>" + e(v['guest'] or '—') + "</strong></td>"
            "<td><span class='pill-badge pill-blue'>" + e(v['category'] or 'Maritime') + "</span></td>"
        )
        return (
            "<tr>"
            "<td style='width:72px;'><img src='" + thumb + "' width='64' height='40' loading='lazy' decoding='async' class='table-thumb' alt='thumb' onerror=\"this.onerror=null;this.src='/static/images/fw_today_1.jpg';\"></td>"
            + second_col +
            "<td style='white-space:nowrap;'>" + e(v['duration'] or '15:00 min') + "</td>"
            "<td style='white-space:nowrap;color:#64748b;'>" + e(v['published']) + "</td>"
            "<td style='width:120px;text-align:center;'>"
            "<div class='action-btns' style='justify-content:center;'>"
            "<button type='button' class='btn-action-round btn-action-edit' title='Edit Video' "
            "data-id='" + str(v['id']) + "' data-tab='" + tab_ctx + "' "
            "data-title='" + e(v['title']) + "' data-category='" + e(v.get('category') or '') + "' "
            "data-author='" + e(v.get('author') or '') + "' data-tag='" + e(v.get('tag') or 'Logistic Waves Today') + "' "
            "data-read-time='" + e(v.get('read_time') or '') + "' data-guest='" + e(v.get('guest') or '') + "' "
            "data-duration='" + e(v.get('duration') or '') + "' data-thumb='" + e(v.get('thumb') or '') + "' "
            "data-excerpt='" + e(v.get('excerpt') or '') + "' data-body='" + e(v.get('body') or '') + "' "
            "onclick='openArticleEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
            "<a href='/articles/" + e(v['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='id' value='" + str(v['id']) + "'>"
            "<input type='hidden' name='tab' value='" + tab_ctx + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    def render_job_row(j, tab_ctx):
        is_overview = (tab_ctx == "overview")
        posted_td = "" if is_overview else "<td style='color:#64748b;'>" + e(j['posted_at']) + "</td>"
        cat_td = "<td><span class='pill-badge pill-blue'>" + e(j['category']) + "</span></td>" if is_overview else "<td>" + e(j['category']) + "</td>"
        wp_cls = "pill-amber" if is_overview else "pill-blue"
        return (
            "<tr>"
            "<td style='min-width:200px;'><strong>" + e(j['title']) + "</strong><br>"
            "<small style='color:#64748b;'>" + e(j['company_name']) + "</small></td>"
            + cat_td +
            "<td><span class='pill-badge " + wp_cls + "'>" + e(j['workplace']) + "</span></td>"
            "<td style='color:#475569;'>" + e(j['location']) + "</td>"
            "<td style='font-weight:700;color:#0f172a;'>" + e(j['salary_display'] or 'Competitive') + "</td>"
            + posted_td +
            "<td style='width:120px;text-align:center;'>"
            "<div class='action-btns' style='justify-content:center;'>"
            "<button type='button' class='btn-action-round btn-action-edit' title='Edit Job' "
            "data-id='" + str(j['id']) + "' data-tab='" + tab_ctx + "' "
            "data-title='" + e(j['title']) + "' data-company-slug='" + e(j.get('company_slug') or '') + "' "
            "data-category='" + e(j.get('category') or '') + "' data-level='" + e(j.get('level') or 'Mid-Senior') + "' "
            "data-workplace='" + e(j.get('workplace') or 'Hybrid') + "' data-location='" + e(j.get('location') or '') + "' "
            "data-salary-min='" + str(j.get('salary_min') or 50000) + "' data-salary-max='" + str(j.get('salary_max') or 85000) + "' "
            "data-salary-display='" + e(j.get('salary_display') or '') + "' data-skills='" + e(j.get('skills') or '') + "' "
            "data-description='" + e(j.get('description') or '') + "' "
            "onclick='openJobEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
            "<a href='/job/" + e(j['slug']) + "/" + str(j['id']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/jobs/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='id' value='" + str(j['id']) + "'>"
            "<input type='hidden' name='tab' value='" + tab_ctx + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    # Render ONLY the active tab content
    if tab == "videos":
        video_rows = "".join([render_video_row(v, "videos") for v in today_videos]) or \
            _empty_row(7, 'No Today episodes yet. Click "Seed Today Videos" above.')
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-circle-plus' style='color:#3874ff;'></i> Add New Today Video</h3>"
            "<form method='post' action='/admin/videos/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='videos'>"
            "<div class='form-group'><label class='form-label'>Episode Title *</label><input class='form-control' name='title' placeholder='e.g. Next-Gen Port Automation' required></div>"
            "<div class='form-group'><label class='form-label'>Featured Guest</label><input class='form-control' name='guest' placeholder='e.g. Capt. Nguyen Van A'></div>"
            "<div class='form-group'><label class='form-label'>Duration</label><input class='form-control' name='duration' value='14:20 min'></div>"
            "<div class='form-group'><label class='form-label'>Category</label>"
            "<select class='form-control' name='category'>"
            "<option value='Maritime &amp; Tech'>Maritime &amp; Tech</option>"
            "<option value='Port Automation'>Port Automation</option>"
            "<option value='Air Cargo'>Air Cargo</option>"
            "<option value='Container Shipping'>Container Shipping</option>"
            "<option value='Clean Freight'>Clean Freight</option>"
            "</select></div>"
            + render_image_uploader_field('vtinput', 'vtpreview', 'Episode Video Thumbnail / Cover', '/static/images/fw_today_1.jpg') +
            "<div class='form-group'><label class='form-label'>Short Summary</label><textarea class='form-control' name='excerpt' rows='2' placeholder='Brief hook...'></textarea></div>"
            "<div class='form-group'><label class='form-label'>Transcript / Notes</label><textarea class='form-control' name='body' rows='3' placeholder='Full notes...'></textarea></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-upload'></i> Publish Episode</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>Today Episodes (" + str(len(today_videos)) + ")</h3>"
            "<span style='font-size:13px;color:#64748b;'>Feeds homepage &amp; article-blogs</span></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Thumb</th><th>Title &amp; Slug</th><th>Guest</th><th>Category</th><th>Duration</th><th>Date</th><th>Action</th></tr></thead>"
            "<tbody>" + video_rows + "</tbody>"
            "</table></div></div>"
        )

    elif tab == "articles":
        def article_row(a):
            today_badge = "<span class='pill-badge pill-blue' style='margin-left:6px;'>Today</span>" if a['is_today'] else ""
            return (
                "<tr>"
                "<td><strong>" + e(a['title']) + "</strong><br>"
                "<small style='color:#64748b;'>/" + e(a['slug']) + "</small>" + today_badge + "</td>"
                "<td><span class='pill-badge pill-amber'>" + e(a['category'] or 'General') + "</span></td>"
                "<td>" + e(a['tag'] or '—') + "</td>"
                "<td>" + e(a['author'] or 'Editorial Staff') + "</td>"
                "<td style='white-space:nowrap;color:#64748b;'>" + e(a['published']) + "</td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Edit Article' "
                "data-id='" + str(a['id']) + "' data-tab='articles' "
                "data-title='" + e(a['title']) + "' data-category='" + e(a.get('category') or '') + "' "
                "data-author='" + e(a.get('author') or '') + "' data-tag='" + e(a.get('tag') or '') + "' "
                "data-read-time='" + e(a.get('read_time') or '') + "' data-guest='" + e(a.get('guest') or '') + "' "
                "data-duration='" + e(a.get('duration') or '') + "' data-thumb='" + e(a.get('thumb') or '') + "' "
                "data-excerpt='" + e(a.get('excerpt') or '') + "' data-body='" + e(a.get('body') or '') + "' "
                "onclick='openArticleEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
                "<a href='/articles/" + e(a['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
                "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
                "<input type='hidden' name='tab' value='articles'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        articles_rows = "".join([article_row(a) for a in all_articles]) or _empty_row(6, "No articles found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-pen-nib' style='color:#3874ff;'></i> Publish New Article</h3>"
            "<form method='post' action='/admin/articles/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='articles'>"
            "<div class='form-group'><label class='form-label'>Article Title *</label><input class='form-control' name='title' placeholder='e.g. 2027 Maritime Freight Trends' required></div>"
            "<div class='form-group'><label class='form-label'>Category</label>"
            "<select class='form-control' name='category'>"
            "<option value='Maritime &amp; Supply Chain'>Maritime &amp; Supply Chain</option>"
            "<option value='Logistics Tech'>Logistics Tech</option>"
            "<option value='Port Infrastructure'>Port Infrastructure</option>"
            "<option value='Freight Rates'>Freight Rates</option>"
            "<option value='Technology'>Technology</option>"
            "<option value='Career &amp; Talent'>Career &amp; Talent</option>"
            "</select></div>"
            "<div class='form-group'><label class='form-label'>Author Name</label><input class='form-control' name='author' value='Editorial Staff'></div>"
            "<div class='form-group'><label class='form-label'>Tag / Theme</label><input class='form-control' name='tag' value='Maritime Insights'></div>"
            "<div class='form-group'><label class='form-label'>Read Time</label><input class='form-control' name='read_time' value='6 min read'></div>"
            + render_image_uploader_field('art-create-thumb', 'art-create-preview', 'Featured Article Cover Image', '/static/images/fw_today_1.jpg') +
            "<div class='form-group'><label class='form-label'>Excerpt / Summary</label><textarea class='form-control' name='excerpt' rows='2' placeholder='Brief summary...'></textarea></div>"
            "<div class='form-group'>"
            "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:8px;'>"
            "<label class='form-label' style='margin:0;'>Article Content (Markdown supported) *</label>"
            "<div style='display:flex;gap:6px;'>"
            "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'single')\" style='border:1px solid #cbd5e1;background:#fff;color:#3874ff;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 1 full-width photo'>"
            "<i class='fa-solid fa-image'></i> + 1 Photo"
            "</button>"
            "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'gallery2')\" style='border:1px solid #cbd5e1;background:#fff;color:#10b981;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 2 photos side-by-side'>"
            "<i class='fa-solid fa-table-columns'></i> + 2-Photo Gallery"
            "</button>"
            "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'gallery3')\" style='border:1px solid #cbd5e1;background:#fff;color:#8b5cf6;font-size:11.5px;font-weight:700;cursor:pointer;padding:3px 8px;border-radius:6px;' title='Insert 3 photos gallery grid'>"
            "<i class='fa-solid fa-table-cells'></i> + 3-Photo Grid"
            "</button>"
            "</div></div>"
            "<textarea class='form-control' name='body' id='art-create-body' rows='6' placeholder='Write your story... Click above buttons to add single images or multi-photo galleries!' required></textarea></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-upload'></i> Publish Article</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>All Articles &amp; Reports (" + str(tab_total if tab_total is not None else counts['articles']) + ")</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Title &amp; Slug</th><th>Category</th><th>Tag</th><th>Author</th><th>Date</th><th>Action</th></tr></thead>"
            "<tbody>" + articles_rows + "</tbody>"
            "</table>" + _render_pagination("articles", page, tab_total if tab_total is not None else counts["articles"], per_page, q) + "</div></div>"
        )

    elif tab == "jobs":
        company_options = "".join([
            "<option value='" + e(c["slug"]) + "'>" + e(c["name"]) + "</option>"
            for c in all_companies
        ])
        jobs_rows = "".join([render_job_row(j, "jobs") for j in all_jobs]) or _empty_row(7, "No jobs found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-briefcase' style='color:#10b981;'></i> Post New Job</h3>"
            "<form method='post' action='/admin/jobs/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='jobs'>"
            "<div class='form-group'><label class='form-label'>Job Title *</label><input class='form-control' name='title' placeholder='e.g. Port Terminal Automation Specialist' required></div>"
            "<div class='form-group'><label class='form-label'>Company *</label>"
            "<select class='form-control' name='company_slug' required>" + company_options + "</select></div>"
            "<div class='form-group'><label class='form-label'>Category</label>"
            "<select class='form-control' name='category'>"
            "<option value='Engineering &amp; Architecture'>Engineering &amp; Architecture</option>"
            "<option value='Operations &amp; Robotics'>Operations &amp; Robotics</option>"
            "<option value='Data &amp; AI'>Data &amp; AI</option>"
            "<option value='Product Management'>Product Management</option>"
            "<option value='Supply Chain Solutions'>Supply Chain Solutions</option>"
            "</select></div>"
            "<div class='form-group'><label class='form-label'>Workplace</label>"
            "<select class='form-control' name='workplace'>"
            "<option value='Hybrid'>Hybrid</option>"
            "<option value='Fully Remote'>Fully Remote</option>"
            "<option value='On Site'>On Site</option>"
            "</select></div>"
            "<div class='form-group'><label class='form-label'>Location</label><input class='form-control' name='location' value='Haiphong / Da Nang / Remote'></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Min Salary ($)</label><input type='number' class='form-control' name='salary_min' value='50000'></div>"
            "<div class='form-group'><label class='form-label'>Max Salary ($)</label><input type='number' class='form-control' name='salary_max' value='85000'></div>"
            "</div>"
            "<div class='form-group'><label class='form-label'>Skills &amp; Stack</label><input class='form-control' name='skills' placeholder='e.g. SCADA, TOS, Python, IoT'></div>"
            "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' rows='3' placeholder='Core responsibilities, qualifications...'></textarea></div>"
            "<button type='submit' class='btn-submit-clean' style='background:#10b981;'><i class='fa-solid fa-plus'></i> Publish Job Listing</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>Active Job Listings (" + str(total_jobs_count) + ")</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Title &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th>Posted</th><th>Action</th></tr></thead>"
            "<tbody>" + jobs_rows + "</tbody>"
            "</table>" + _render_pagination("jobs", page, total_jobs_count, per_page, q) + "</div></div>"
        )

    elif tab == "companies":
        def company_row(c):
            clr = e(c.get('color') or '#3874ff')
            return (
                "<tr>"
                "<td><div style='display:flex;align-items:center;gap:12px;'>"
                "<span style='display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:10px;background:" + clr + ";color:#fff;font-weight:800;font-size:13px;'>" + e(c.get('initials') or 'CO') + "</span>"
                "<div><strong>" + e(c.get('name') or '') + "</strong><br><small style='color:#64748b;'>" + e(c.get('slug') or '') + "</small></div>"
                "</div></td>"
                "<td><span class='pill-badge pill-blue'>" + e(c.get('industries') or 'Logistics') + "</span></td>"
                "<td>" + e(c.get('location') or '') + "</td>"
                "<td>" + format(c.get('employees') or 0, ',') + " employees</td>"
                "<td><span class='pill-badge pill-green'>" + str(c.get('open_jobs') or 0) + " Openings</span></td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Edit Company' "
                "data-id='" + str(c.get('id') or '') + "' data-tab='companies' "
                "data-name='" + e(c.get('name') or '') + "' data-tagline='" + e(c.get('tagline') or '') + "' "
                "data-industries='" + e(c.get('industries') or '') + "' data-location='" + e(c.get('location') or '') + "' "
                "data-employees='" + str(c.get('employees') or 1000) + "' data-color='" + e(c.get('color') or '#3874ff') + "' "
                "data-website='" + e(c.get('website') or '') + "' data-description='" + e(c.get('description') or '') + "' "
                "onclick='openCompanyEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
                "<a href='/company/" + e(c.get('slug') or '') + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
                "<form method='post' action='/admin/companies/delete' onsubmit=\"return confirm('Delete company and all jobs?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(c.get('id') or '') + "'>"
                "<input type='hidden' name='tab' value='companies'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        companies_rows = "".join([company_row(c) for c in all_companies]) or _empty_row(6, "No companies found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-building' style='color:#8b5cf6;'></i> Register Company</h3>"
            "<form method='post' action='/admin/companies/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='companies'>"
            "<div class='form-group'><label class='form-label'>Company Name *</label><input class='form-control' name='name' placeholder='e.g. Saigon Port Authority' required></div>"
            "<div class='form-group'><label class='form-label'>Tagline</label><input class='form-control' name='tagline' placeholder='e.g. Modern Deepwater Port &amp; Logistics Hub'></div>"
            "<div class='form-group'><label class='form-label'>Industries</label><input class='form-control' name='industries' value='Logistics &amp; Maritime Shipping'></div>"
            "<div class='form-group'><label class='form-label'>Headquarters</label><input class='form-control' name='location' value='Ho Chi Minh City, Vietnam'></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Employees</label><input type='number' class='form-control' name='employees' value='1500'></div>"
            "<div class='form-group'><label class='form-label'>Brand Color</label><input class='form-control' name='color' value='#034f9a'></div>"
            "</div>"
            "<div class='form-group'><label class='form-label'>Website</label><input class='form-control' name='website' placeholder='https://company.com'></div>"
            "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' rows='3' placeholder='Overview...'></textarea></div>"
            "<button type='submit' class='btn-submit-clean' style='background:#8b5cf6;'><i class='fa-solid fa-plus'></i> Register Company</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>Registered Companies (" + str(tab_total if tab_total is not None else counts['companies']) + ")</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Team Size</th><th>Jobs</th><th>Action</th></tr></thead>"
            "<tbody>" + companies_rows + "</tbody>"
            "</table>" + _render_pagination("companies", page, tab_total if tab_total is not None else counts["companies"], per_page, q) + "</div></div>"
        )

    elif tab == "users":
        def user_row(u):
            initial = e((u['name'] or 'U')[0].upper())
            role_opts = ""
            for rv in ["candidate", "employer", "admin"]:
                sel = " selected" if u["role"] == rv else ""
                role_opts += "<option value='" + rv + "'" + sel + ">" + rv.capitalize() + "</option>"
            return (
                "<tr>"
                "<td><div style='display:flex;align-items:center;gap:10px;'>"
                "<div style='width:34px;height:34px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0;'>" + initial + "</div>"
                "<div><strong>" + e(u['name']) + "</strong><br><small style='color:#64748b;'>" + e(u['email']) + "</small></div>"
                "</div></td>"
                "<td><form method='post' action='/admin/users/role' style='display:inline-flex;align-items:center;gap:6px;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(u['id']) + "'>"
                "<select name='role' class='form-control' style='padding:4px 8px;font-size:12px;min-width:110px;' onchange='this.form.submit()'>"
                + role_opts +
                "</select></form></td>"
                "<td style='color:#64748b;font-size:13px;'>" + e((u['created_at'] or '—')[:10]) + "</td>"
                "<td><div class='action-btns'>"
                "<form method='post' action='/admin/users/delete' onsubmit=\"return confirm('Permanently delete this user?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(u['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        users_rows = "".join([user_row(u) for u in all_users]) or _empty_row(4, "No users found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-user-plus' style='color:#3874ff;'></i> Create User Account</h3>"
            "<form method='post' action='/admin/users/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='users'>"
            "<div class='form-group'><label class='form-label'>Full Name *</label><input class='form-control' name='name' placeholder='e.g. Nguyen Van A' required></div>"
            "<div class='form-group'><label class='form-label'>Email *</label><input class='form-control' type='email' name='email' placeholder='e.g. user@logisticwaves.com' required></div>"
            "<div class='form-group'><label class='form-label'>Password</label><input class='form-control' type='password' name='password' placeholder='Min 6 characters' required></div>"
            "<div class='form-group'><label class='form-label'>Role</label>"
            "<select class='form-control' name='role'>"
            "<option value='candidate'>Candidate (Job Seeker)</option>"
            "<option value='employer'>Employer (Company)</option>"
            "<option value='admin'>Admin</option>"
            "</select></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-plus'></i> Create User</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'>"
            "<h3 class='table-title'>Registered Users (" + str(len(all_users)) + ")</h3>"
            "<span style='font-size:13px;color:#64748b;'>Change role via dropdown</span>"
            "</div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Name &amp; Email</th><th>Role</th><th>Joined</th><th>Action</th></tr></thead>"
            "<tbody>" + users_rows + "</tbody>"
            "</table></div></div>"
        )

    elif tab == "applications":
        app_statuses_list = ["Applied", "Reviewing", "Interview", "Offer", "Rejected"]
        def app_row(a):
            status_btns = "".join([
                "<button type='submit' name='status' value='" + s + "' "
                "style='display:block;width:100%;text-align:left;padding:5px 8px;border:none;background:none;cursor:pointer;font-size:13px;border-radius:6px;' "
                "onmouseover=\"this.style.background='#f1f5f9'\" onmouseout=\"this.style.background='none'\">" + s + "</button>"
                for s in app_statuses_list
            ])
            note_text = (a['note'] or '')
            note_short = note_text[:60] + ("..." if len(note_text) > 60 else "")
            return (
                "<tr>"
                "<td><strong>" + e(a['user_name']) + "</strong><br><small style='color:#64748b;'>" + e(a['user_email']) + "</small></td>"
                "<td><a href='/job/" + e(a['job_slug']) + "/" + str(a['job_id']) + "' target='_blank' style='color:#3874ff;font-weight:700;text-decoration:none;'>" + e(a['job_title']) + "</a></td>"
                "<td>" + status_pill(a['status']) + "</td>"
                "<td style='max-width:180px;font-size:13px;color:#475569;'>" + e(note_short) + "</td>"
                "<td style='color:#64748b;font-size:13px;white-space:nowrap;'>" + e((a['created_at'] or '')[:10]) + "</td>"
                "<td><div class='action-btns'>"
                "<details style='position:relative;'>"
                "<summary class='btn-action-round' style='list-style:none;cursor:pointer;' title='Update Status'><i class='fa-solid fa-pen-to-square'></i></summary>"
                "<div style='position:absolute;right:0;top:30px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:8px;z-index:50;min-width:140px;box-shadow:0 4px 20px rgba(0,0,0,.12);'>"
                "<form method='post' action='/admin/applications/status'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
                + status_btns +
                "</form></div></details>"
                "<form method='post' action='/admin/applications/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        status_counts = {}
        for a in all_applications:
            status_counts[a['status']] = status_counts.get(a['status'], 0) + 1
        status_summary = "".join([
            "<span class='pill-badge pill-blue' style='margin-right:6px;'>" + s + ": <strong>" + str(c) + "</strong></span>"
            for s, c in status_counts.items()
        ]) or ("<span style='color:#94a3b8;font-size:13px;'>No matching applications</span>" if q else "<span style='color:#94a3b8;font-size:13px;'>No applications yet</span>")
        applications_rows = "".join([app_row(a) for a in all_applications]) or _empty_row(6, "No applications yet. Users apply from individual job pages.")
        active_content = (
            "<div class='table-card'>"
            "<div class='table-header-bar'>"
            "<h3 class='table-title'><i class='fa-solid fa-file-signature' style='color:#8b5cf6;margin-right:8px;'></i> Job Applications (" + str(applications_count) + ")</h3>"
            "<div>" + status_summary + "</div>"
            "</div>"
            "<div style='padding:0 24px 12px;'><p style='font-size:13px;color:#64748b;margin:0;'>"
            "Applications submitted by candidates. Click <i class='fa-solid fa-pen-to-square'></i> to update status."
            "</p></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Applicant</th><th>Job Position</th><th>Status</th><th>Notes</th><th>Applied</th><th>Action</th></tr></thead>"
            "<tbody>" + applications_rows + "</tbody>"
            "</table>" + _render_pagination("applications", page, applications_count, per_page, q) + "</div>"
        )

    elif tab == "subscribers":
        def sub_row(s):
            return (
                "<tr>"
                "<td style='font-weight:600;'>" + e(s['email']) + "</td>"
                "<td style='color:#64748b;font-size:13px;'>" + e((s['created_at'] or '')[:10]) + "</td>"
                "<td><div class='action-btns'>"
                "<form method='post' action='/admin/subscribers/delete' onsubmit=\"return confirm('Remove subscriber?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(s['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        subs_rows = "".join([sub_row(s) for s in all_subscribers]) or _empty_row(3, "No subscribers yet. Newsletter signups appear here automatically.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-envelope' style='color:#3874ff;'></i> Newsletter Info</h3>"
            "<div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:20px;margin-bottom:16px;text-align:center;'>"
            "<div style='font-size:40px;font-weight:800;color:#1d4ed8;'>" + str(subscribers_count) + "</div>"
            "<div style='font-size:14px;color:#3b82f6;font-weight:600;'>Total Subscribers</div>"
            "</div>"
            "<div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px;margin-bottom:16px;'>"
            "<p style='font-size:13px;color:#166534;margin:0;'>"
            "<i class='fa-solid fa-circle-info'></i> Subscribers sign up via the newsletter form in the site footer. "
            "New signups appear here automatically."
            "</p></div>"
            "<div style='padding:14px;background:#fafafa;border:1px solid #e2e8f0;border-radius:10px;'>"
            "<h4 style='font-size:14px;font-weight:700;margin:0 0 8px;'>Quick Stats</h4>"
            "<div style='font-size:13px;color:#475569;line-height:1.9;'>"
            "<div>&#10003; Total subscribers: <strong>" + str(subscribers_count) + "</strong></div>"
            "<div>&#10003; Signup form: <strong>/ homepage footer</strong></div>"
            "<div>&#10003; API: <strong>POST /api/newsletter</strong></div>"
            "</div></div>"
            "</div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>All Subscribers (" + str(len(all_subscribers)) + ")</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Email Address</th><th>Subscribed On</th><th>Action</th></tr></thead>"
            "<tbody>" + subs_rows + "</tbody>"
            "</table></div></div>"
        )

    elif tab == "salaries":
        def salary_row(s):
            return (
                "<tr>"
                "<td><strong>" + e(s['title']) + "</strong></td>"
                "<td><span class='pill-badge pill-amber'>" + e(s['category']) + "</span></td>"
                "<td style='font-weight:700;color:#0f172a;'>$" + format(s['median'], ',') + "</td>"
                "<td style='color:#64748b;'>$" + format(s['low'], ',') + " &ndash; $" + format(s['high'], ',') + "</td>"
                "<td style='color:#64748b;'>" + format(s['samples'], ',') + " reports</td>"
                "<td style='color:#10b981;font-weight:700;'>" + e(s['trend']) + "</td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Edit Salary' "
                "data-id='" + str(s['id']) + "' data-tab='salaries' "
                "data-title='" + e(s['title']) + "' data-category='" + e(s.get('category') or '') + "' "
                "data-median='" + str(s.get('median') or 80000) + "' data-low='" + str(s.get('low') or 60000) + "' "
                "data-high='" + str(s.get('high') or 110000) + "' data-samples='" + str(s.get('samples') or 500) + "' "
                "data-trend='" + e(s.get('trend') or '+2.0%') + "' "
                "onclick='openSalaryEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
                "<a href='/salaries' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
                "<form method='post' action='/admin/salaries/delete' onsubmit=\"return confirm('Delete salary entry?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(s['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        salaries_rows = "".join([salary_row(s) for s in all_salaries]) or _empty_row(7, "No salary data found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-chart-bar' style='color:#10b981;'></i> Add Salary Benchmark</h3>"
            "<form method='post' action='/admin/salaries/create'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='tab' value='salaries'>"
            "<div class='form-group'><label class='form-label'>Job Title *</label><input class='form-control' name='title' placeholder='e.g. Logistics Software Engineer' required></div>"
            "<div class='form-group'><label class='form-label'>Category</label>"
            "<select class='form-control' name='category'>"
            "<option value='Logistics &amp; Supply Chain'>Logistics &amp; Supply Chain</option>"
            "<option value='Engineering'>Engineering</option>"
            "<option value='Data &amp; Analytics'>Data &amp; Analytics</option>"
            "<option value='Operations'>Operations</option>"
            "<option value='Product Management'>Product Management</option>"
            "<option value='Sales'>Sales</option>"
            "</select></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;'>"
            "<div class='form-group'><label class='form-label'>Median ($)</label><input type='number' class='form-control' name='median' value='85000'></div>"
            "<div class='form-group'><label class='form-label'>Low ($)</label><input type='number' class='form-control' name='low' value='62000'></div>"
            "<div class='form-group'><label class='form-label'>High ($)</label><input type='number' class='form-control' name='high' value='118000'></div>"
            "</div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Samples (reports)</label><input type='number' class='form-control' name='samples' value='1200'></div>"
            "<div class='form-group'><label class='form-label'>Trend</label><input class='form-control' name='trend' value='+3.1%'></div>"
            "</div>"
            "<button type='submit' class='btn-submit-clean' style='background:#10b981;'><i class='fa-solid fa-plus'></i> Add Salary Entry</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'>"
            "<h3 class='table-title'>Salary Benchmarks (" + str(len(all_salaries)) + ")</h3>"
            "<a href='/salaries' target='_blank' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>Live Salaries Page &rarr;</a>"
            "</div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Job Title</th><th>Category</th><th>Median</th><th>Range</th><th>Reports</th><th>Trend</th><th>Action</th></tr></thead>"
            "<tbody>" + salaries_rows + "</tbody>"
            "</table></div></div>"
        )

    elif tab == "courses":
        all_courses = db.list_courses(conn, include_inactive=True)
        def course_row(c):
            return (
                "<tr>"
                "<td><img src='" + e(c.get('thumb') or '/static/images/fw_today_1.svg') + "' style='width:56px;height:36px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;'></td>"
                "<td><strong>" + e(c['title']) + "</strong><br><small style='color:#64748b;'>/" + e(c.get('slug') or '') + "</small></td>"
                "<td><span class='pill-badge pill-blue'>" + e(c.get('channel') or 'Academy') + "</span></td>"
                "<td>" + e(c.get('instructor') or 'Faculty') + "</td>"
                "<td>" + e(c.get('duration') or '25m') + "</td>"
                "<td>" + status_pill(c.get('status') or 'active') + "</td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Edit Course' "
                "data-id='" + str(c['id']) + "' data-title='" + e(c['title']) + "' "
                "data-channel='" + e(c.get('channel') or '') + "' data-instructor='" + e(c.get('instructor') or '') + "' "
                "data-duration='" + e(c.get('duration') or '') + "' data-date='" + e(c.get('published_date') or '') + "' "
                "data-thumb='" + e(c.get('thumb') or '') + "' data-desc='" + e(c.get('description') or '') + "' "
                "data-status='" + e(c.get('status') or 'active') + "' "
                "onclick='openCourseEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
                "<form method='post' action='/admin/courses/delete' onsubmit=\"return confirm('Delete this course?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(c['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        courses_rows = "".join([course_row(c) for c in all_courses]) or _empty_row(7, "No courses found.")
        active_content = (
            "<div class='form-panel-grid'>"
            "<div class='clean-card-form'>"
            "<h3 class='form-title'><i class='fa-solid fa-graduation-cap' style='color:#3874ff;'></i> Publish New Course</h3>"
            "<form method='post' action='/admin/courses/create'>"
            f"{_csrf_field()}"
            "<div class='form-group'><label class='form-label'>Course Title *</label><input class='form-control' name='title' placeholder='e.g. Container Terminal Automation 2026' required></div>"
            "<div class='form-group'><label class='form-label'>Channel / Track</label><input class='form-control' name='channel' value='Logistic Wave Today'></div>"
            "<div class='form-group'><label class='form-label'>Instructor</label><input class='form-control' name='instructor' value='Logistics Waves Faculty'></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Duration</label><input class='form-control' name='duration' value='35m'></div>"
            "<div class='form-group'><label class='form-label'>Published Date</label><input class='form-control' name='published_date' value='Nov 2026'></div>"
            "</div>"
            + render_image_uploader_field('crs-create-thumb', 'crs-create-preview', 'Course Thumbnail', '/static/images/fw_today_1.svg') +
            "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' rows='3' placeholder='Course overview...'></textarea></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-plus'></i> Publish Course</button>"
            "</form></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'>Live Courses (" + str(len(all_courses)) + ")</h3>"
            "<a href='/courses' target='_blank' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>Live Courses Page &rarr;</a></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Thumb</th><th>Title</th><th>Track</th><th>Instructor</th><th>Duration</th><th>Status</th><th>Action</th></tr></thead>"
            "<tbody>" + courses_rows + "</tbody>"
            "</table></div></div>"
            "<div id='courseEditModal' style='display:none;position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:3000;align-items:center;justify-content:center;padding:20px;'>"
            "<div style='background:#fff;border-radius:16px;max-width:560px;width:100%;padding:24px;max-height:90vh;overflow:auto;'>"
            "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;'>"
            "<h3 style='margin:0;font-size:18px;'>Edit Course</h3>"
            "<button type='button' onclick=\"document.getElementById('courseEditModal').style.display='none'\" style='background:none;border:none;font-size:20px;cursor:pointer;'>&times;</button></div>"
            "<form method='post' action='/admin/courses/update'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='id' id='edit-crs-id'>"
            "<div class='form-group'><label class='form-label'>Title *</label><input class='form-control' name='title' id='edit-crs-title' required></div>"
            "<div class='form-group'><label class='form-label'>Channel / Track</label><input class='form-control' name='channel' id='edit-crs-channel'></div>"
            "<div class='form-group'><label class='form-label'>Instructor</label><input class='form-control' name='instructor' id='edit-crs-instructor'></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;'>"
            "<div class='form-group'><label class='form-label'>Duration</label><input class='form-control' name='duration' id='edit-crs-duration'></div>"
            "<div class='form-group'><label class='form-label'>Date</label><input class='form-control' name='published_date' id='edit-crs-date'></div>"
            "<div class='form-group'><label class='form-label'>Status</label><select class='form-control' name='status' id='edit-crs-status'><option value='active'>active</option><option value='inactive'>inactive</option></select></div>"
            "</div>"
            "<div class='form-group'><label class='form-label'>Thumbnail URL</label><input class='form-control' name='thumb' id='edit-crs-thumb'></div>"
            "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' id='edit-crs-desc' rows='3'></textarea></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-check'></i> Save Course</button>"
            "</form></div></div>"
            "<script>function openCourseEditModal(btn){"
            "document.getElementById('edit-crs-id').value=btn.dataset.id||'';"
            "document.getElementById('edit-crs-title').value=btn.dataset.title||'';"
            "document.getElementById('edit-crs-channel').value=btn.dataset.channel||'';"
            "document.getElementById('edit-crs-instructor').value=btn.dataset.instructor||'';"
            "document.getElementById('edit-crs-duration').value=btn.dataset.duration||'';"
            "document.getElementById('edit-crs-date').value=btn.dataset.date||'';"
            "document.getElementById('edit-crs-thumb').value=btn.dataset.thumb||'';"
            "document.getElementById('edit-crs-desc').value=btn.dataset.desc||'';"
            "document.getElementById('edit-crs-status').value=btn.dataset.status||'active';"
            "document.getElementById('courseEditModal').style.display='flex';}</script>"
        )

    elif tab == "settings":
        site = db.get_site_settings(conn)
        imgs = site.get("hero_images_list") or []
        while len(imgs) < 4:
            imgs.append("")
        hero_imgs_text = "\n".join(site.get("hero_images_list") or [])
        active_content = (
            "<div class='clean-card-form' style='max-width:920px;'>"
            "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;'>"
            "<h3 class='form-title' style='margin:0;'><i class='fa-solid fa-sliders' style='color:#3874ff;'></i> Live Site &amp; Hero Banner Controls</h3>"
            "<a href='/' target='_blank' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>Preview Live Homepage &rarr;</a>"
            "</div>"
            "<p style='color:#64748b;font-size:13px;margin-bottom:18px;'>All changes here are saved to Supabase PostgreSQL and update the live homepage immediately.</p>"
            "<form method='post' action='/admin/settings/save'>"
            f"{_csrf_field()}"
            "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Hero Title Prefix</label><input class='form-control' name='hero_title_prefix' value='" + e(site.get('hero_title_prefix') or '') + "' required></div>"
            "<div class='form-group'><label class='form-label'>Hero Highlight (Blue)</label><input class='form-control' name='hero_title_highlight' value='" + e(site.get('hero_title_highlight') or '') + "' required></div>"
            "<div class='form-group'><label class='form-label'>Hero Title Suffix</label><input class='form-control' name='hero_title_suffix' value='" + e(site.get('hero_title_suffix') or '') + "'></div>"
            "</div>"
            "<div class='form-group'><label class='form-label'>Hero Subtitle</label><textarea class='form-control' name='hero_subtitle' rows='2'>" + e(site.get('hero_subtitle') or '') + "</textarea></div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr 1fr 120px;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Primary Button Label</label><input class='form-control' name='hero_primary_label' value='" + e(site.get('hero_primary_label') or '') + "'></div>"
            "<div class='form-group'><label class='form-label'>Primary Button Link</label><input class='form-control' name='hero_primary_href' value='" + e(site.get('hero_primary_href') or '') + "'></div>"
            "<div class='form-group'><label class='form-label'>Secondary Button Label</label><input class='form-control' name='hero_secondary_label' value='" + e(site.get('hero_secondary_label') or '') + "'></div>"
            "<div class='form-group'><label class='form-label'>Swap (sec)</label><input type='number' min='3' max='60' class='form-control' name='hero_interval_sec' value='" + e(site.get('hero_interval_sec') or '10') + "'></div>"
            "</div>"
            "<h4 style='margin:16px 0 10px;font-size:14px;color:#0f172a;'>Hero Banner Slideshow Images (Auto-Swap)</h4>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
            "<div class='form-group'><label class='form-label'>Slide 1 Image URL</label><input class='form-control' name='hero_img_1' value='" + e(imgs[0]) + "'></div>"
            "<div class='form-group'><label class='form-label'>Slide 2 Image URL</label><input class='form-control' name='hero_img_2' value='" + e(imgs[1]) + "'></div>"
            "<div class='form-group'><label class='form-label'>Slide 3 Image URL</label><input class='form-control' name='hero_img_3' value='" + e(imgs[2]) + "'></div>"
            "<div class='form-group'><label class='form-label'>Slide 4 Image URL</label><input class='form-control' name='hero_img_4' value='" + e(imgs[3]) + "'></div>"
            "</div>"
            "<input type='hidden' name='hero_images_text' value='" + e(hero_imgs_text) + "'>"
            "<div class='form-group'><label class='form-label'>Footer Brand Tagline</label><textarea class='form-control' name='footer_tagline' rows='2'>" + e(site.get('footer_tagline') or '') + "</textarea></div>"
            "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-floppy-disk'></i> Save All Live Settings</button>"
            "</form></div>"
        )

    else:  # overview
        recent_videos_rows = "".join([render_video_row(v, "overview") for v in today_videos[:5]]) or \
            _empty_row(6, 'No videos yet. Click "Seed Today Videos" above.')
        recent_jobs_rows = "".join([render_job_row(j, "overview") for j in all_jobs[:5]]) or \
            _empty_row(6, "No jobs found.")
        active_content = (
            "<div class='charts-grid'>"
            "<div class='chart-card'>"
            "<div class='chart-header'><h3 class='chart-title'>Platform Activity per Month (2026)</h3>"
            "<div class='chart-legend'>"
            "<span><span class='legend-dot' style='background:#3874ff;'></span> Broadcast Videos</span>"
            "<span><span class='legend-dot' style='background:#60a5fa;'></span> Jobs &amp; Reports</span>"
            "</div></div>"
            "<div class='bar-chart-container'>"
            "<svg viewBox='0 0 650 200' style='width:100%;height:100%;'>"
            "<line x1='40' y1='20' x2='630' y2='20' stroke='#f1f5f9' stroke-width='1'/>"
            "<line x1='40' y1='60' x2='630' y2='60' stroke='#f1f5f9' stroke-width='1'/>"
            "<line x1='40' y1='100' x2='630' y2='100' stroke='#f1f5f9' stroke-width='1'/>"
            "<line x1='40' y1='140' x2='630' y2='140' stroke='#f1f5f9' stroke-width='1'/>"
            "<line x1='40' y1='180' x2='630' y2='180' stroke='#e2e8f0' stroke-width='1'/>"
            "<text x='25' y='24' fill='#94a3b8' font-size='10' text-anchor='end'>25</text>"
            "<text x='25' y='64' fill='#94a3b8' font-size='10' text-anchor='end'>20</text>"
            "<text x='25' y='104' fill='#94a3b8' font-size='10' text-anchor='end'>15</text>"
            "<text x='25' y='144' fill='#94a3b8' font-size='10' text-anchor='end'>10</text>"
            "<text x='25' y='184' fill='#94a3b8' font-size='10' text-anchor='end'>5</text>"
            "<rect x='58' y='70' width='5' height='110' rx='2.5' fill='#3874ff'/><rect x='66' y='90' width='5' height='90' rx='2.5' fill='#93c5fd'/><text x='64' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Jan</text>"
            "<rect x='110' y='80' width='5' height='100' rx='2.5' fill='#3874ff'/><rect x='118' y='125' width='5' height='55' rx='2.5' fill='#93c5fd'/><text x='116' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Feb</text>"
            "<rect x='162' y='30' width='5' height='150' rx='2.5' fill='#3874ff'/><rect x='170' y='95' width='5' height='85' rx='2.5' fill='#93c5fd'/><text x='168' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Mar</text>"
            "<rect x='214' y='130' width='5' height='50' rx='2.5' fill='#3874ff'/><rect x='222' y='145' width='5' height='35' rx='2.5' fill='#93c5fd'/><text x='220' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Apr</text>"
            "<rect x='266' y='115' width='5' height='65' rx='2.5' fill='#3874ff'/><rect x='274' y='135' width='5' height='45' rx='2.5' fill='#93c5fd'/><text x='272' y='196' fill='#64748b' font-size='10' text-anchor='middle'>May</text>"
            "<rect x='318' y='120' width='5' height='60' rx='2.5' fill='#3874ff'/><rect x='326' y='155' width='5' height='25' rx='2.5' fill='#93c5fd'/><text x='324' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Jun</text>"
            "<rect x='370' y='75' width='5' height='105' rx='2.5' fill='#3874ff'/><rect x='378' y='90' width='5' height='90' rx='2.5' fill='#93c5fd'/><text x='376' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Jul</text>"
            "<rect x='422' y='65' width='5' height='115' rx='2.5' fill='#3874ff'/><rect x='430' y='100' width='5' height='80' rx='2.5' fill='#93c5fd'/><text x='428' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Sep</text>"
            "<rect x='474' y='105' width='5' height='75' rx='2.5' fill='#3874ff'/><rect x='482' y='115' width='5' height='65' rx='2.5' fill='#93c5fd'/><text x='480' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Oct</text>"
            "<rect x='526' y='80' width='5' height='100' rx='2.5' fill='#3874ff'/><rect x='534' y='130' width='5' height='50' rx='2.5' fill='#93c5fd'/><text x='532' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Nov</text>"
            "<rect x='578' y='45' width='5' height='135' rx='2.5' fill='#3874ff'/><rect x='586' y='95' width='5' height='85' rx='2.5' fill='#93c5fd'/><text x='584' y='196' fill='#64748b' font-size='10' text-anchor='middle'>Dec</text>"
            "</svg></div></div>"
            "<div class='chart-card'>"
            "<div class='chart-header'><h3 class='chart-title'>Platform Entities</h3>"
            "<span style='color:#94a3b8;font-size:13px;font-weight:600;'>Distribution</span></div>"
            "<div class='donut-chart-container'>"
            "<svg width='150' height='150' viewBox='0 0 42 42'>"
            "<circle cx='21' cy='21' r='15.91549430918954' fill='#ffffff'></circle>"
            "<circle cx='21' cy='21' r='15.91549430918954' fill='transparent' stroke='#3874ff' stroke-width='5' stroke-dasharray='54 46' stroke-dashoffset='25'></circle>"
            "<circle cx='21' cy='21' r='15.91549430918954' fill='transparent' stroke='#34d399' stroke-width='5' stroke-dasharray='30 70' stroke-dashoffset='71'></circle>"
            "<circle cx='21' cy='21' r='15.91549430918954' fill='transparent' stroke='#f87171' stroke-width='5' stroke-dasharray='16 84' stroke-dashoffset='41'></circle>"
            "<text x='21' y='22' font-size='7' font-weight='800' text-anchor='middle' fill='#202224' dy='.3em'>100%</text>"
            "</svg>"
            "<div class='donut-legend-list'>"
            "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#3874ff;'></span> Editorial Articles</span><strong>" + str(counts['articles']) + "</strong></div>"
            "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#34d399;'></span> Active Jobs</span><strong>" + str(counts['jobs']) + "</strong></div>"
            "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#f87171;'></span> Today Broadcasts</span><strong>" + str(today_videos_count) + "</strong></div>"
            "</div></div></div></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'>"
            "<h3 class='table-title'><i class='fa-solid fa-video' style='color:#3874ff;margin-right:8px;'></i> Live Today Broadcast Episodes</h3>"
            "<a href='/admin?tab=videos' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>View All (" + str(today_videos_count) + ") &rarr;</a>"
            "</div>"
            "<table class='clean-table'>"
            "<thead><tr><th style='width:72px;'>Thumb</th><th>Title &amp; Guest</th><th>Category</th><th>Duration</th><th>Published</th><th style='width:120px;text-align:center;'>Action</th></tr></thead>"
            "<tbody>" + recent_videos_rows + "</tbody>"
            "</table></div>"
            "<div class='table-card'>"
            "<div class='table-header-bar'>"
            "<h3 class='table-title'><i class='fa-solid fa-briefcase' style='color:#10b981;margin-right:8px;'></i> Active Job Listings</h3>"
            "<a href='/admin?tab=jobs' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>View All (" + str(counts['jobs']) + ") &rarr;</a>"
            "</div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Role &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th style='width:120px;text-align:center;'>Action</th></tr></thead>"
            "<tbody>" + recent_jobs_rows + "</tbody>"
            "</table></div>"
        )

    admin_name    = (user["name"] if user else "Admin")
    admin_initial = admin_name[0].upper() if admin_name else "A"

    # Stat gauge percents (dynamic, clamped)
    pct_videos  = min(99, max(5, today_videos_count * 8))
    pct_arts    = min(99, 40 + counts['articles'] // 3)
    pct_jobs    = min(99, 30 + counts['jobs'] // 4)
    pct_users   = min(99, 50 + users_count * 5)

    return (
        "<!doctype html>\n<html lang='en'>\n<head>\n"
        "<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        "<title>Admin Dashboard | Logistic Waves</title>\n"
        "<link rel='icon' type='image/png' href='/static/favicon.png'>\n"
        "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css' crossorigin='anonymous' referrerpolicy='no-referrer'>\n"
        "<link rel='stylesheet' href='/static/admin.css?v=20261112_03'>\n"
        "</head>\n<body class='admin-body'>\n"
        "<div class='admin-layout'>\n"

        # --- Sidebar ---
        "<div class='admin-mobile-overlay' id='adminMobileOverlay' onclick='closeAdminSidebar()'></div>\n"
        "<aside class='admin-sidebar' id='adminSidebar'>\n"
        "<div class='sidebar-header'>"
        "<div class='sidebar-brand-icon'><i class='fa-solid fa-shapes'></i></div>"
        "<a href='/admin' class='sidebar-brand-title'>Dashboard</a>"
        "</div>\n"
        "<ul class='sidebar-menu'>"
        "<li><a href='/admin?tab=overview' class='" + nav_active('overview') + "'><i class='fa-solid fa-house'></i> Overview</a></li>"
        "<li><a href='/admin?tab=videos' class='" + nav_active('videos') + "'><i class='fa-solid fa-video'></i> Videos / Today</a></li>"
        "<li><a href='/admin?tab=articles' class='" + nav_active('articles') + "'><i class='fa-solid fa-file-lines'></i> Articles</a></li>"
        "<li><a href='/admin?tab=jobs' class='" + nav_active('jobs') + "'><i class='fa-solid fa-briefcase'></i> Jobs &amp; Careers</a></li>"
        "<li><a href='/admin?tab=companies' class='" + nav_active('companies') + "'><i class='fa-solid fa-building'></i> Companies</a></li>"
        "<li style='height:1px;background:rgba(255,255,255,.12);margin:12px 20px;'></li>"
        "<li><a href='/admin?tab=users' class='" + nav_active('users') + "'><i class='fa-solid fa-users'></i> Users <span style='background:rgba(255,255,255,.18);border-radius:12px;padding:2px 7px;font-size:11px;margin-left:4px;'>" + str(users_count) + "</span></a></li>"
        "<li><a href='/admin?tab=applications' class='" + nav_active('applications') + "'><i class='fa-solid fa-file-signature'></i> Applications <span style='background:rgba(255,255,255,.18);border-radius:12px;padding:2px 7px;font-size:11px;margin-left:4px;'>" + str(applications_count) + "</span></a></li>"
        "<li><a href='/admin?tab=subscribers' class='" + nav_active('subscribers') + "'><i class='fa-solid fa-envelope'></i> Subscribers <span style='background:rgba(255,255,255,.18);border-radius:12px;padding:2px 7px;font-size:11px;margin-left:4px;'>" + str(subscribers_count) + "</span></a></li>"
        "<li><a href='/admin?tab=salaries' class='" + nav_active('salaries') + "'><i class='fa-solid fa-chart-bar'></i> Salary Data</a></li>"
        "<li><a href='/admin?tab=courses' class='" + nav_active('courses') + "'><i class='fa-solid fa-graduation-cap'></i> Courses</a></li>"
        "<li><a href='/admin?tab=settings' class='" + nav_active('settings') + "'><i class='fa-solid fa-sliders'></i> Site &amp; Hero</a></li>"
        "</ul>\n"
        "<div class='sidebar-footer'><a href='/' target='_blank'><i class='fa-solid fa-arrow-right-from-bracket'></i> Live Website</a></div>"
        "</aside>\n"

        # --- Main ---
        "<main class='admin-main'>\n"
        "<header class='admin-topbar'>"
        "<div class='topbar-left'>"
        "<button class='admin-mobile-toggle' onclick='toggleAdminSidebar()' aria-label='Toggle navigation'>"
        "<i class='fa-solid fa-bars'></i> Menu</button>"
        "<a href='/admin?tab=videos' class='btn-add-new'><i class='fa-solid fa-plus'></i> Add New</a>"
        "<div class='search-box'><i class='fa-solid fa-magnifying-glass'></i>"
        "<input type='text' class='search-input' value='" + e(q) + "' placeholder='Filter or press Enter to search...' aria-label='Search' "
        "oninput='filterAdminTable(this.value)' "
        "onkeydown=\"if(event.key==='Enter'){window.location='/admin?tab=" + e(tab) + "&q='+encodeURIComponent(this.value);}\"></div>"
        "</div>"
        "<div class='topbar-right'>"
        "<div id='adminUserWrap' style='position:relative;'>"
        "<button type='button' class='topbar-user' onclick='toggleAdminUserMenu()' style='background:none;border:none;cursor:pointer;padding:4px 8px;border-radius:10px;'>"
        "<div style='width:36px;height:36px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;'>" + e(admin_initial) + "</div>"
        "<div class='topbar-user-info'>"
        "<span class='topbar-user-name'>" + e(admin_name) + "</span>"
        "<span class='topbar-user-role'>Admin</span>"
        "</div>"
        "<i class='fa-solid fa-chevron-down' style='font-size:11px;color:#94a3b8;'></i>"
        "</button>"
        "<div id='adminUserMenu' style='display:none;position:absolute;right:0;top:50px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 12px 30px rgba(15,23,42,.15);min-width:190px;padding:6px;z-index:2000;'>"
        "<a href='/profile' style='display:flex;align-items:center;gap:8px;padding:8px 12px;font-size:13px;color:#1e293b;border-radius:8px;text-decoration:none;'><i class='fa-solid fa-user' style='color:#3874ff;width:16px;'></i> Member Profile</a>"
        "<a href='/' target='_blank' style='display:flex;align-items:center;gap:8px;padding:8px 12px;font-size:13px;color:#1e293b;border-radius:8px;text-decoration:none;'><i class='fa-solid fa-globe' style='color:#10b981;width:16px;'></i> Live Website</a>"
        "<form method='post' action='/logout' style='margin:4px 0 0;padding-top:4px;border-top:1px solid #f1f5f9;'>"
        f"{_csrf_field()}"
        "<button type='submit' style='width:100%;display:flex;align-items:center;gap:8px;padding:8px 12px;font-size:13px;color:#ef4444;background:none;border:none;border-radius:8px;cursor:pointer;font-weight:600;text-align:left;'><i class='fa-solid fa-right-from-bracket' style='width:16px;'></i> Log Out</button>"
        "</form></div></div>"
        "<div id='adminNotifWrap' style='position:relative;'>"
        "<button type='button' id='adminNotifBtn' onclick='toggleAdminNotifMenu(event)' class='topbar-icon-btn' title='Notifications' style='border:none;cursor:pointer;'><i class='fa-regular fa-bell'></i><span class='notification-dot'></span></button>"
        "<div id='adminNotifMenu' style='display:none;position:absolute;right:0;top:48px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 12px 30px rgba(15,23,42,.15);width:290px;padding:12px;z-index:2000;'>"
        "<div style='font-size:13px;font-weight:800;color:#0f172a;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;'><span>Platform Activity</span><span style='font-size:11px;color:#3874ff;'>Live DB</span></div>"
        "<a href='/admin?tab=applications' style='display:flex;align-items:center;justify-content:space-between;padding:8px 10px;background:#f8fafc;border-radius:8px;margin-bottom:6px;text-decoration:none;color:#1e293b;font-size:12.5px;'>"
        "<span><i class='fa-solid fa-file-signature' style='color:#8b5cf6;margin-right:6px;'></i> Job Applications</span><strong style='color:#3874ff;'>" + str(applications_count) + "</strong></a>"
        "<a href='/admin?tab=subscribers' style='display:flex;align-items:center;justify-content:space-between;padding:8px 10px;background:#f8fafc;border-radius:8px;margin-bottom:6px;text-decoration:none;color:#1e293b;font-size:12.5px;'>"
        "<span><i class='fa-solid fa-envelope' style='color:#10b981;margin-right:6px;'></i> Newsletter Subscribers</span><strong style='color:#10b981;'>" + str(subscribers_count) + "</strong></a>"
        "<a href='/admin?tab=jobs' style='display:flex;align-items:center;justify-content:space-between;padding:8px 10px;background:#f8fafc;border-radius:8px;text-decoration:none;color:#1e293b;font-size:12.5px;'>"
        "<span><i class='fa-solid fa-briefcase' style='color:#06b6d4;margin-right:6px;'></i> Active Jobs</span><strong>" + str(counts['jobs']) + "</strong></a>"
        "</div></div>"
        "<a href='/' class='topbar-icon-btn' title='Exit to Site'><i class='fa-solid fa-arrow-right-from-bracket'></i></a>"
        "</div></header>\n"

        "<div class='admin-container'>\n"
        + alert_html +
        "\n<div class='admin-seed-control-card'>"
        "<div class='seed-control-info'>"
        "<div class='seed-control-icon'><i class='fa-solid fa-bolt'></i></div>"
        "<div class='seed-control-text'>"
        "<h3>Fast Data Controls &amp; Seeders</h3>"
        "<p>One-click population of Logistic Waves Today videos, companies, and jobs.</p>"
        "</div></div>"
        "<form method='post' action='/admin/seed' class='seed-control-buttons'>"
        f"{_csrf_field()}"
        "<input type='hidden' name='tab' value='" + e(tab) + "'>"
        "<button type='submit' name='action' value='seed_videos' class='btn-ctrl btn-ctrl-primary'><i class='fa-solid fa-play'></i> Seed Today Videos (6)</button>"
        "<button type='submit' name='action' value='seed_logistics' class='btn-ctrl btn-ctrl-success'><i class='fa-solid fa-truck-fast'></i> Seed Logistics &amp; Jobs</button>"
        "<button type='submit' name='action' value='reseed_all' class='btn-ctrl btn-ctrl-purple'><i class='fa-solid fa-database'></i> Reseed Full System</button>"
        "<button type='submit' name='action' value='clear_videos' class='btn-ctrl btn-ctrl-light' onclick=\"return confirm('Reset all Today videos?');\"><i class='fa-solid fa-trash-can'></i> Reset Videos</button>"
        "</form></div>\n"

        # Stat cards (clickable shortcuts to each section)
        "<div class='stat-cards-grid'>"
        "<div class='stat-card' style='cursor:pointer;' onclick=\"window.location='/admin?tab=videos'\"><div class='stat-card-left'>"
        + circular_gauge_svg(pct_videos, "#3874ff") +
        "<div class='stat-card-info'><h4>Today<br>Videos</h4><div class='stat-number'>" + str(today_videos_count) + "</div>"
        "<div class='stat-card-trend trend-up'>Live " + mini_wave_svg("#3874ff") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card' style='cursor:pointer;' onclick=\"window.location='/admin?tab=articles'\"><div class='stat-card-left'>"
        + circular_gauge_svg(pct_arts, "#10b981") +
        "<div class='stat-card-info'><h4>Editorial<br>Articles</h4><div class='stat-number'>" + str(counts['articles']) + "</div>"
        "<div class='stat-card-trend trend-up'>16% &uarr; " + mini_wave_svg("#10b981") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card' style='cursor:pointer;' onclick=\"window.location='/admin?tab=jobs'\"><div class='stat-card-left'>"
        + circular_gauge_svg(pct_jobs, "#06b6d4") +
        "<div class='stat-card-info'><h4>Active<br>Jobs</h4><div class='stat-number'>" + str(counts['jobs']) + "</div>"
        "<div class='stat-card-trend trend-up'>12% &uarr; " + mini_wave_svg("#06b6d4") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card' style='cursor:pointer;' onclick=\"window.location='/admin?tab=users'\"><div class='stat-card-left'>"
        + circular_gauge_svg(pct_users, "#8b5cf6") +
        "<div class='stat-card-info'><h4>Users &amp;<br>Members</h4><div class='stat-number'>" + str(users_count) + "</div>"
        "<div class='stat-card-trend trend-up'>" + str(applications_count) + " apps " + mini_wave_svg("#8b5cf6") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"
        "</div>\n"

        + active_content +
        "\n" + render_edit_modals(all_companies) +
        "\n</div></main></div></body></html>"
    )
