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

def render_create_modals(all_companies):
    company_options = "".join([
        "<option value='" + e(c["slug"]) + "'>" + e(c["name"]) + "</option>"
        for c in all_companies
    ])
    return (
        "<!-- Create Article Modal -->\n"
        "<div class='admin-modal-backdrop' id='create-article-modal'>\n"
        "<div class='admin-modal-dialog' style='max-width:880px;'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-pen-nib' style='color:#3874ff;'></i> Publish New Article</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/articles/create' class='admin-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='articles'>\n"
        "<div class='form-group'><label class='form-label'>Article Title *</label><input class='form-control' name='title' placeholder='e.g. 2027 Maritime Freight Trends' required></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Category</label>\n"
        "<select class='form-control' name='category'>\n"
        "<option value='Maritime &amp; Supply Chain'>Maritime &amp; Supply Chain</option>\n"
        "<option value='Logistics Tech'>Logistics Tech</option>\n"
        "<option value='Port Infrastructure'>Port Infrastructure</option>\n"
        "<option value='Freight Rates'>Freight Rates</option>\n"
        "<option value='Technology'>Technology</option>\n"
        "<option value='Career &amp; Talent'>Career &amp; Talent</option>\n"
        "</select></div>\n"
        "<div class='form-group'><label class='form-label'>Tag / Theme</label><input class='form-control' name='tag' value='Maritime Insights'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Author Name</label><input class='form-control' name='author' value='Editorial Staff'></div>\n"
        "<div class='form-group'><label class='form-label'>Read Time</label><input class='form-control' name='read_time' value='6 min read'></div>\n"
        "</div>\n"
        + render_image_uploader_field('art-create-thumb', 'art-create-preview', 'Featured Article Cover Image', '/static/images/fw_today_1.jpg') +
        "<div class='form-group'><label class='form-label'>Excerpt / Summary</label><textarea class='form-control' name='excerpt' rows='2' placeholder='Brief summary...'></textarea></div>\n"
        "<div class='form-group'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:8px;'>"
        "<label class='form-label' style='margin:0;'><i class='fa-solid fa-pen-nib' style='color:#3874ff;'></i> Article Content (WYSIWYG: Highlight, Drag &amp; Resize Images)</label>"
        "<div style='display:flex;gap:6px;flex-wrap:wrap;'>"
        "<label style='border:1px solid #bbf7d0;background:#f0fdf4;color:#15803d;font-size:11.5px;font-weight:700;cursor:pointer;padding:4px 9px;border-radius:6px;display:flex;align-items:center;gap:5px;' title='Upload photo directly from computer'>"
        "<i class='fa-solid fa-cloud-arrow-up'></i> Upload Device Photo"
        "<input type='file' accept='image/*' style='display:none;' onchange=\"insertUploadedImageToEditor(this, 'art-create-body')\">"
        "</label>"
        "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'single')\" style='border:1px solid #cbd5e1;background:#fff;color:#3874ff;font-size:11.5px;font-weight:700;cursor:pointer;padding:4px 9px;border-radius:6px;' title='Fetch &amp; insert real image from web URL or Unsplash'>"
        "<i class='fa-solid fa-globe'></i> Insert Web Image"
        "</button>"
        "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'gallery2')\" style='border:1px solid #cbd5e1;background:#fff;color:#0284c7;font-size:11.5px;font-weight:700;cursor:pointer;padding:4px 9px;border-radius:6px;' title='Insert 2 photos side-by-side'>"
        "<i class='fa-solid fa-table-columns'></i> + 2-Photo Gallery"
        "</button>"
        "<button type='button' onclick=\"insertImageMarkdown('art-create-body', 'gallery3')\" style='border:1px solid #cbd5e1;background:#fff;color:#8b5cf6;font-size:11.5px;font-weight:700;cursor:pointer;padding:4px 9px;border-radius:6px;' title='Insert 3 photos gallery grid'>"
        "<i class='fa-solid fa-table-cells'></i> + 3-Photo Grid"
        "</button>"
        "</div></div>"
        "<textarea class='form-control rich-editor' name='body' id='art-create-body' rows='10' placeholder='Write your story...'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save'><i class='fa-solid fa-upload'></i> Publish Article</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Create Today Video Modal -->\n"
        "<div class='admin-modal-backdrop' id='create-video-modal'>\n"
        "<div class='admin-modal-dialog' style='max-width:750px;'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-circle-plus' style='color:#3874ff;'></i> Add New Today Video</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/videos/create' class='admin-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='videos'>\n"
        "<div class='form-group'><label class='form-label'>Episode Title *</label><input class='form-control' name='title' placeholder='e.g. Next-Gen Port Automation' required></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Featured Guest</label><input class='form-control' name='guest' placeholder='e.g. Capt. Nguyen Van A'></div>\n"
        "<div class='form-group'><label class='form-label'>Duration</label><input class='form-control' name='duration' value='14:20 min'></div>\n"
        "</div>\n"
        "<div class='form-group'><label class='form-label'>Category</label>\n"
        "<select class='form-control' name='category'>\n"
        "<option value='Maritime &amp; Tech'>Maritime &amp; Tech</option>\n"
        "<option value='Port Automation'>Port Automation</option>\n"
        "<option value='Air Cargo'>Air Cargo</option>\n"
        "<option value='Container Shipping'>Container Shipping</option>\n"
        "<option value='Clean Freight'>Clean Freight</option>\n"
        "</select></div>\n"
        + render_image_uploader_field('vtinput', 'vtpreview', 'Episode Video Thumbnail / Cover', '/static/images/fw_today_1.jpg') +
        "<div class='form-group'><label class='form-label'>Short Summary</label><textarea class='form-control' name='excerpt' rows='2' placeholder='Brief hook...'></textarea></div>\n"
        "<div class='form-group'><label class='form-label'>Transcript / Notes</label><textarea class='form-control' name='body' rows='3' placeholder='Full notes...'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save'><i class='fa-solid fa-upload'></i> Publish Episode</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Create Job Modal (Landscape 2-Column) -->\n"
        "<div class='admin-modal-backdrop cms-modal-backdrop' id='create-job-modal'>\n"
        "<div class='cms-modal-dialog'>\n"
        "<div class='cms-modal-header'>\n"
        "<h3 class='cms-modal-title'><i class='fa-solid fa-briefcase' style='color:#2563eb;'></i> Post New Job</h3>\n"
        "<button type='button' class='cms-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/jobs/create' id='admin-create-job-form' class='cms-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='jobs'>\n"
        "<input type='hidden' name='skills' id='create-job-skills'>\n"
        "<div class='cms-layout-2col'>\n"
        "  <div class='cms-col-left'>\n"
        "    <div class='cms-job-company-card'>\n"
        "      <div class='cms-job-company-avatar' style='background:#2563eb;'><i class='fa-solid fa-briefcase'></i></div>\n"
        "      <div class='cms-job-company-name'>New Job Listing</div>\n"
        "      <div class='cms-job-company-loc'>Select company &amp; publish</div>\n"
        "    </div>\n"
        "    <nav class='cms-side-nav'>\n"
        "      <button type='button' class='cms-side-nav-btn active' onclick=\"switchCmsTab(this,'admin-cjob-tab-basic')\"><i class='fa-solid fa-briefcase'></i> Basic Info</button>\n"
        "      <button type='button' class='cms-side-nav-btn' onclick=\"switchCmsTab(this,'admin-cjob-tab-apply')\"><i class='fa-solid fa-paper-plane'></i> Application &amp; Pay</button>\n"
        "    </nav>\n"
        "  </div>\n"
        "  <div class='cms-col-center'>\n"
        "    <div class='cms-tab-pane active' id='admin-cjob-tab-basic'>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Job Title *</label><input class='cms-form-control' name='title' placeholder='e.g. Port Terminal Automation Specialist' required></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Company *</label><select class='cms-form-control' name='company_slug' required>" + company_options + "</select></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Category</label><input class='cms-form-control' name='category' value='Engineering &amp; Architecture'></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Workplace</label><select class='cms-form-control' name='workplace'><option value='Hybrid'>Hybrid</option><option value='Fully Remote'>Fully Remote</option><option value='On Site'>On Site</option></select></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Location</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-location-dot'></i><input class='cms-form-control' name='location' value='Ho Chi Minh City, VN'></div></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Employment Level</label><input class='cms-form-control' name='level' value='Mid-Senior'></div>\n"
        "      </div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Skills</label><div class='cms-chips-wrap' id='create-job-skills-wrap'><button type='button' class='cms-chip-add-btn' onclick=\"addCmsChip('create-job-skills-wrap','create-job-skills','skill')\">+ Add</button></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Job Description</label><textarea class='cms-form-control' name='description' rows='4' placeholder='Core responsibilities, qualifications...'></textarea></div>\n"
        "    </div>\n"
        "    <div class='cms-tab-pane' id='admin-cjob-tab-apply'>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Min Salary ($)</label><input type='number' class='cms-form-control' name='salary_min' value='50000'></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Max Salary ($)</label><input type='number' class='cms-form-control' name='salary_max' value='85000'></div>\n"
        "      </div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Salary Display</label><input class='cms-form-control' name='salary_display' placeholder='$50,000 - $85,000'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Application URL</label><input class='cms-form-control' name='apply_url' placeholder='https://...'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Application Email</label><input class='cms-form-control' name='apply_email' placeholder='careers@company.com'></div>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        "</form>\n"
        "<div class='cms-modal-footer'>\n"
        "<div class='cms-footer-left'><button type='button' class='cms-btn cms-btn-cancel' onclick='closeAllModals()'>Cancel</button></div>\n"
        "<div class='cms-footer-right'><button type='button' class='cms-btn cms-btn-save' onclick=\"document.getElementById('admin-create-job-form').submit()\"><i class='fa-solid fa-paper-plane'></i> Publish Job Listing</button></div>\n"
        "</div>\n"
        "</div></div>\n"

        "<!-- Create Company Modal (Landscape 3-Column) -->\n"
        "<div class='admin-modal-backdrop cms-modal-backdrop' id='create-company-modal'>\n"
        "<div class='cms-modal-dialog'>\n"
        "<div class='cms-modal-header'>\n"
        "<h3 class='cms-modal-title'><i class='fa-solid fa-building' style='color:#2563eb;'></i> Register Company</h3>\n"
        "<button type='button' class='cms-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/companies/create' id='admin-create-company-form' class='cms-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='companies'>\n"
        "<input type='hidden' name='social_links' id='create-company-social-links'>\n"
        "<div class='cms-layout-3col'>\n"
        "  <div class='cms-col-left'>\n"
        "    <div class='cms-logo-box'>\n"
        "      <img id='create-company-logo-prev' src='/static/images/logo_emblem.png' alt='Logo'>\n"
        "      <label class='cms-btn-sm-outline'><i class='fa-solid fa-camera'></i> Upload Logo<input type='file' accept='image/*' style='display:none;' onchange=\"handleCmsImageUpload(this, 'create-company-logo-url', 'create-company-logo-prev')\"></label>\n"
        "      <input class='cms-form-control' id='create-company-logo-url' name='logo_url' placeholder='Logo URL...' style='font-size:11.5px;padding:5px 8px;' oninput=\"updateCmsImagePreview(this.value, 'create-company-logo-prev')\">\n"
        "    </div>\n"
        "    <div class='cms-cover-card'>\n"
        "      <img id='create-company-banner-prev' src='/static/images/fw_today_1.jpg' alt='Banner'>\n"
        "      <label class='cms-cover-overlay-btn'><i class='fa-solid fa-camera'></i> Upload Banner<input type='file' accept='image/*' style='display:none;' onchange=\"handleCmsImageUpload(this, 'create-company-banner-url', 'create-company-banner-prev')\"></label>\n"
        "    </div>\n"
        "    <input class='cms-form-control' id='create-company-banner-url' name='banner_url' placeholder='Banner URL...' style='font-size:11.5px;padding:5px 8px;' oninput=\"updateCmsImagePreview(this.value, 'create-company-banner-prev')\">\n"
        "  </div>\n"
        "  <div class='cms-col-center'>\n"
        "    <div class='cms-grid-2'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Company Name *</label><input class='cms-form-control' name='name' placeholder='e.g. Saigon Port Authority' required></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Tagline</label><input class='cms-form-control' name='tagline' placeholder='e.g. Modern Deepwater Port Hub'></div>\n"
        "    </div>\n"
        "    <div class='cms-grid-2'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Industries</label><input class='cms-form-control' name='industries' value='Logistics &amp; Maritime Shipping'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Headquarters</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-location-dot'></i><input class='cms-form-control' name='location' value='Ho Chi Minh City, Vietnam'></div></div>\n"
        "    </div>\n"
        "    <div class='cms-grid-2'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Employees</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-users'></i><input type='number' class='cms-form-control' name='employees' value='1500'></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Website</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-globe'></i><input class='cms-form-control' name='website' placeholder='https://company.com'></div></div>\n"
        "    </div>\n"
        "    <div class='cms-form-group'><label class='cms-form-label'>About the Company</label><textarea class='cms-form-control' name='description' rows='5' placeholder='Overview...'></textarea></div>\n"
        "  </div>\n"
        "  <div class='cms-col-right'>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>Company Settings</h4>\n"
        "      <label class='cms-toggle-row'><span><i class='fa-solid fa-circle-check' style='color:#2563eb;'></i> Verified Company</span><span class='cms-switch'><input type='checkbox' name='verified' value='1' checked><span class='cms-switch-slider'></span></span></label>\n"
        "      <label class='cms-toggle-row'><span>Featured Company</span><span class='cms-switch'><input type='checkbox' name='featured' value='1'><span class='cms-switch-slider'></span></span></label>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Brand Color</label><div class='cms-color-row'><input type='color' class='cms-color-swatch' value='#2563eb' oninput=\"document.getElementById('create-comp-color-hex').value=this.value\"><input class='cms-form-control' id='create-comp-color-hex' name='color' value='#2563eb'></div></div>\n"
        "    </div>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>Social Links</h4>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-linkedin' style='color:#0a66c2;'></i></span><input class='cms-form-control cms-social-linkedin' placeholder='LinkedIn URL'></div>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-youtube' style='color:#dc2626;'></i></span><input class='cms-form-control cms-social-youtube' placeholder='YouTube / X URL'></div>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-facebook' style='color:#1877f2;'></i></span><input class='cms-form-control cms-social-facebook' placeholder='Facebook URL'></div>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        "</form>\n"
        "<div class='cms-modal-footer'>\n"
        "<div class='cms-footer-left'><button type='button' class='cms-btn cms-btn-cancel' onclick='closeAllModals()'>Cancel</button></div>\n"
        "<div class='cms-footer-right'><button type='button' class='cms-btn cms-btn-save' onclick=\"syncCmsSocialLinks(document.getElementById('admin-create-company-form'));document.getElementById('admin-create-company-form').submit()\"><i class='fa-solid fa-plus'></i> Register Company</button></div>\n"
        "</div>\n"
        "</div></div>\n"

        "<!-- Create User Modal -->\n"
        "<div class='admin-modal-backdrop' id='create-user-modal'>\n"
        "<div class='admin-modal-dialog' style='max-width:580px;'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-user-plus' style='color:#3874ff;'></i> Create User Account</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/users/create' class='admin-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='users'>\n"
        "<div class='form-group'><label class='form-label'>Full Name *</label><input class='form-control' name='name' placeholder='e.g. Nguyen Van A' required></div>\n"
        "<div class='form-group'><label class='form-label'>Email *</label><input class='form-control' type='email' name='email' placeholder='e.g. user@logisticwaves.com' required></div>\n"
        "<div class='form-group'><label class='form-label'>Password *</label><input class='form-control' type='password' name='password' placeholder='Min 6 characters' required></div>\n"
        "<div class='form-group'><label class='form-label'>Role</label>\n"
        "<select class='form-control' name='role'>\n"
        "<option value='candidate'>Candidate (Job Seeker)</option>\n"
        "<option value='employer'>Employer (Company)</option>\n"
        "<option value='admin'>Admin</option>\n"
        "</select></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save'><i class='fa-solid fa-plus'></i> Create User</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Create Salary Modal -->\n"
        "<div class='admin-modal-backdrop' id='create-salary-modal'>\n"
        "<div class='admin-modal-dialog' style='max-width:680px;'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-chart-bar' style='color:#10b981;'></i> Add Salary Benchmark</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/salaries/create' class='admin-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<input type='hidden' name='tab' value='salaries'>\n"
        "<div class='form-group'><label class='form-label'>Job Title *</label><input class='form-control' name='title' placeholder='e.g. Logistics Software Engineer' required></div>\n"
        "<div class='form-group'><label class='form-label'>Category</label>\n"
        "<select class='form-control' name='category'>\n"
        "<option value='Logistics &amp; Supply Chain'>Logistics &amp; Supply Chain</option>\n"
        "<option value='Engineering'>Engineering</option>\n"
        "<option value='Data &amp; Analytics'>Data &amp; Analytics</option>\n"
        "<option value='Operations'>Operations</option>\n"
        "<option value='Product Management'>Product Management</option>\n"
        "<option value='Sales'>Sales</option>\n"
        "</select></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;'>\n"
        "<div class='form-group'><label class='form-label'>Median ($)</label><input type='number' class='form-control' name='median' value='85000'></div>\n"
        "<div class='form-group'><label class='form-label'>Low ($)</label><input type='number' class='form-control' name='low' value='62000'></div>\n"
        "<div class='form-group'><label class='form-label'>High ($)</label><input type='number' class='form-control' name='high' value='118000'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Samples (reports)</label><input type='number' class='form-control' name='samples' value='1200'></div>\n"
        "<div class='form-group'><label class='form-label'>Trend</label><input class='form-control' name='trend' value='+3.1%'></div>\n"
        "</div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save' style='background:#10b981;border-color:#10b981;'><i class='fa-solid fa-plus'></i> Add Salary Entry</button>\n"
        "</div>\n"
        "</form></div></div>\n"

        "<!-- Create Course Modal -->\n"
        "<div class='admin-modal-backdrop' id='create-course-modal'>\n"
        "<div class='admin-modal-dialog' style='max-width:700px;'>\n"
        "<div class='admin-modal-header'>\n"
        "<h3 class='admin-modal-title'><i class='fa-solid fa-graduation-cap' style='color:#3874ff;'></i> Publish New Course</h3>\n"
        "<button type='button' class='admin-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "<form method='post' action='/admin/courses/create' class='admin-modal-body'>\n"
        f"{_csrf_field()}\n"
        "<div class='form-group'><label class='form-label'>Course Title *</label><input class='form-control' name='title' placeholder='e.g. Container Terminal Automation 2026' required></div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Channel / Track</label><input class='form-control' name='channel' value='Logistic Wave Today'></div>\n"
        "<div class='form-group'><label class='form-label'>Instructor</label><input class='form-control' name='instructor' value='Logistics Waves Faculty'></div>\n"
        "</div>\n"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>\n"
        "<div class='form-group'><label class='form-label'>Duration</label><input class='form-control' name='duration' value='35m'></div>\n"
        "<div class='form-group'><label class='form-label'>Published Date</label><input class='form-control' name='published_date' value='Nov 2026'></div>\n"
        "</div>\n"
        + render_image_uploader_field('crs-create-thumb', 'crs-create-preview', 'Course Thumbnail', '/static/images/fw_today_1.svg') +
        "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' rows='3' placeholder='Course overview...'></textarea></div>\n"
        "<div class='admin-modal-footer' style='margin:0 -24px -24px;border-bottom-left-radius:16px;border-bottom-right-radius:16px;'>\n"
        "<button type='button' class='btn-modal-cancel' onclick='closeAllModals()'>Cancel</button>\n"
        "<button type='submit' class='btn-modal-save'><i class='fa-solid fa-plus'></i> Publish Course</button>\n"
        "</div>\n"
        "</form></div></div>\n"
    )

def render_edit_modals(all_companies):
    company_options = "".join([
        "<option value='" + e(c['slug']) + "'>" + e(c['name']) + "</option>"
        for c in all_companies
    ])
    return (
        "<!-- Article/Video Edit Modal (Landscape 3-Column) -->\n"
        "<div class='admin-modal-backdrop cms-modal-backdrop' id='edit-article-modal'>\n"
        "<div class='cms-modal-dialog'>\n"
        "<div class='cms-modal-header'>\n"
        "<h3 class='cms-modal-title'><i class='fa-solid fa-pen-to-square' style='color:#2563eb;'></i> Edit Article / Video</h3>\n"
        "<div class='cms-header-actions'>\n"
        "<button type='button' class='cms-header-preview-btn' id='edit-article-preview-btn' onclick=\"var s=document.getElementById('edit-article-slug').value; if(s) previewCmsItem('/articles/'+s);\"><i class='fa-regular fa-eye'></i> Preview</button>\n"
        "<button type='button' class='cms-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "</div>\n"
        "<form method='post' action='/admin/articles/update' id='admin-edit-article-form' class='cms-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-article-id'>\n"
        "<input type='hidden' name='tab' id='edit-article-tab' value='articles'>\n"
        "<input type='hidden' name='tag' id='edit-article-tag'>\n"
        f"{_csrf_field()}\n"
        "<div class='cms-layout-3col'>\n"
        "  <div class='cms-col-left'>\n"
        "    <div class='cms-cover-card'>\n"
        "      <img id='edit-article-preview' src='/static/images/fw_today_1.jpg' alt='Cover' onerror=\"this.onerror=null;this.src='/static/images/fw_today_1.jpg'\">\n"
        "      <label class='cms-cover-overlay-btn'><i class='fa-solid fa-camera'></i> Change Image<input type='file' accept='image/*' style='display:none;' onchange=\"handleCmsImageUpload(this, 'edit-article-thumb', 'edit-article-preview')\"></label>\n"
        "    </div>\n"
        "    <input class='cms-form-control' id='edit-article-thumb' name='thumb' placeholder='Image URL...' style='font-size:12px;padding:6px 9px;' oninput=\"updateCmsImagePreview(this.value, 'edit-article-preview')\">\n"
        "    <div class='cms-gallery-strip'>\n"
        "      <div class='cms-gallery-thumb' onclick=\"setPresetImage('edit-article-thumb','edit-article-preview','/static/images/fw_today_1.jpg')\"><img src='/static/images/fw_today_1.jpg' alt='P1'></div>\n"
        "      <div class='cms-gallery-thumb' onclick=\"setPresetImage('edit-article-thumb','edit-article-preview','/static/images/fw_today_3.jpg')\"><img src='/static/images/fw_today_3.jpg' alt='P2'></div>\n"
        "      <div class='cms-gallery-thumb' onclick=\"setPresetImage('edit-article-thumb','edit-article-preview','/static/images/fw_today_4.jpg')\"><img src='/static/images/fw_today_4.jpg' alt='P3'></div>\n"
        "      <label class='cms-gallery-add' title='Insert Photo into Article'>+<input type='file' accept='image/*' style='display:none;' onchange=\"insertUploadedImageToEditor(this, 'edit-article-body')\"></label>\n"
        "    </div>\n"
        "  </div>\n"
        "  <div class='cms-col-center'>\n"
        "    <div class='cms-grid-2'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Title *</label><input class='cms-form-control' name='title' id='edit-article-title' required></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Category</label><input class='cms-form-control' name='category' id='edit-article-category'></div>\n"
        "    </div>\n"
        "    <div class='cms-grid-4'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Author</label><div class='cms-input-icon-wrap'><i class='fa-regular fa-user'></i><input class='cms-form-control' name='author' id='edit-article-author'></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Guest / Presenter</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-microphone'></i><input class='cms-form-control' name='guest' id='edit-article-guest'></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Reading Time</label><div class='cms-input-icon-wrap'><i class='fa-regular fa-clock'></i><input class='cms-form-control' name='read_time' id='edit-article-read-time'></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Video Duration</label><div class='cms-input-icon-wrap'><i class='fa-regular fa-circle-play'></i><input class='cms-form-control' name='duration' id='edit-article-duration' placeholder='12:30'></div></div>\n"
        "    </div>\n"
        "    <div class='cms-form-group'><label class='cms-form-label'>Tags</label><div class='cms-chips-wrap' id='edit-art-tags-wrap'><button type='button' class='cms-chip-add-btn' onclick=\"addCmsChip('edit-art-tags-wrap','edit-article-tag','tag')\">+ Add Tag</button></div></div>\n"
        "    <div class='cms-form-group'><label class='cms-form-label'>Summary</label><textarea class='cms-form-control' name='excerpt' id='edit-article-excerpt' rows='2'></textarea></div>\n"
        "    <div class='cms-form-group'><label class='cms-form-label'>Article Content</label><textarea class='cms-form-control rich-editor' name='body' id='edit-article-body' rows='7'></textarea></div>\n"
        "  </div>\n"
        "  <div class='cms-col-right'>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>Publishing Options</h4>\n"
        "      <div class='cms-form-group'><select class='cms-form-control' name='status' id='edit-article-status'><option value='published'>Published</option><option value='draft'>Draft</option><option value='archived'>Archived</option></select></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Publish Date</label><input class='cms-form-control' name='published' id='edit-article-published'></div>\n"
        "      <label class='cms-toggle-row'><span>Featured Article</span><span class='cms-switch'><input type='checkbox' name='featured' id='edit-article-featured' value='1'><span class='cms-switch-slider'></span></span></label>\n"
        "      <label class='cms-toggle-row'><span>Allow Comments</span><span class='cms-switch'><input type='checkbox' name='allow_comments' id='edit-article-allow-comments' value='1' checked><span class='cms-switch-slider'></span></span></label>\n"
        "    </div>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>SEO Settings</h4>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>SEO Title</label><input class='cms-form-control' name='seo_title' id='edit-article-seo-title'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Meta Description</label><textarea class='cms-form-control' name='seo_description' id='edit-article-seo-description' rows='2'></textarea></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>URL Slug</label><input class='cms-form-control' name='slug' id='edit-article-slug' readonly style='background:#f1f5f9;color:#64748b;'></div>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        "</form>\n"
        "<div class='cms-modal-footer'>\n"
        "<div class='cms-footer-left'><button type='button' class='cms-btn cms-btn-cancel' onclick='closeAllModals()'>Cancel</button><button type='button' class='cms-btn cms-btn-archive' onclick=\"submitCmsPublish('admin-edit-article-form','archived')\"><i class='fa-solid fa-box-archive'></i> Archive</button></div>\n"
        "<div class='cms-footer-right'><button type='button' class='cms-btn cms-btn-draft' onclick=\"submitCmsPublish('admin-edit-article-form','draft')\"><i class='fa-regular fa-floppy-disk'></i> Save Draft</button><button type='button' class='cms-btn cms-btn-save' onclick=\"submitCmsPublish('admin-edit-article-form','published')\"><i class='fa-solid fa-paper-plane'></i> Publish Update</button></div>\n"
        "</div>\n"
        "</div></div>\n"

        "<!-- Job Edit Modal (Landscape 2-Column Tabbed) -->\n"
        "<div class='admin-modal-backdrop cms-modal-backdrop' id='edit-job-modal'>\n"
        "<div class='cms-modal-dialog'>\n"
        "<div class='cms-modal-header'>\n"
        "<h3 class='cms-modal-title'><i class='fa-solid fa-briefcase' style='color:#2563eb;'></i> Edit Job Listing</h3>\n"
        "<div class='cms-header-actions'>\n"
        "<button type='button' class='cms-header-preview-btn' onclick=\"var jid=document.getElementById('edit-job-id').value; var s=document.getElementById('edit-job-slug').value||'job'; if(jid) previewCmsItem('/job/'+s+'/'+jid);\"><i class='fa-regular fa-eye'></i> Preview</button>\n"
        "<button type='button' class='cms-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "</div>\n"
        "<form method='post' action='/admin/jobs/update' id='admin-edit-job-form' class='cms-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-job-id'>\n"
        "<input type='hidden' name='slug' id='edit-job-slug'>\n"
        "<input type='hidden' name='tab' id='edit-job-tab' value='jobs'>\n"
        "<input type='hidden' name='skills' id='edit-job-skills'>\n"
        f"{_csrf_field()}\n"
        "<div class='cms-layout-2col'>\n"
        "  <div class='cms-col-left'>\n"
        "    <div class='cms-job-company-card'>\n"
        "      <div class='cms-job-company-avatar' id='edit-job-company-avatar'>CO</div>\n"
        "      <div class='cms-job-company-name' id='edit-job-company-name'>Company</div>\n"
        "      <div class='cms-job-company-loc' id='edit-job-company-loc'>Location</div>\n"
        "    </div>\n"
        "    <nav class='cms-side-nav'>\n"
        "      <button type='button' class='cms-side-nav-btn active' onclick=\"switchCmsTab(this,'admin-job-tab-basic')\"><i class='fa-solid fa-briefcase'></i> Basic Info</button>\n"
        "      <button type='button' class='cms-side-nav-btn' onclick=\"switchCmsTab(this,'admin-job-tab-req')\"><i class='fa-solid fa-list-check'></i> Requirements</button>\n"
        "      <button type='button' class='cms-side-nav-btn' onclick=\"switchCmsTab(this,'admin-job-tab-apply')\"><i class='fa-solid fa-paper-plane'></i> Application</button>\n"
        "      <button type='button' class='cms-side-nav-btn' onclick=\"switchCmsTab(this,'admin-job-tab-settings')\"><i class='fa-solid fa-gear'></i> Settings</button>\n"
        "    </nav>\n"
        "  </div>\n"
        "  <div class='cms-col-center'>\n"
        "    <div class='cms-tab-pane active' id='admin-job-tab-basic'>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Job Title *</label><input class='cms-form-control' name='title' id='edit-job-title' required></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Company *</label><select class='cms-form-control' name='company_slug' id='edit-job-company-slug'>" + company_options + "</select></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Category</label><input class='cms-form-control' name='category' id='edit-job-category'></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Workplace</label><select class='cms-form-control' name='workplace' id='edit-job-workplace'><option value='Hybrid'>Hybrid</option><option value='Fully Remote'>Fully Remote</option><option value='On Site'>On Site</option></select></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Location</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-location-dot'></i><input class='cms-form-control' name='location' id='edit-job-location'></div></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Salary Range (USD)</label><input class='cms-form-control' name='salary_display' id='edit-job-salary-display'></div>\n"
        "      </div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Skills</label><div class='cms-chips-wrap' id='edit-job-skills-wrap'><button type='button' class='cms-chip-add-btn' onclick=\"addCmsChip('edit-job-skills-wrap','edit-job-skills','skill')\">+ Add</button></div></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Job Description</label><textarea class='cms-form-control' name='description' id='edit-job-description' rows='5'></textarea></div>\n"
        "    </div>\n"
        "    <div class='cms-tab-pane' id='admin-job-tab-req'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Employment Level</label><input class='cms-form-control' name='level' id='edit-job-level' placeholder='e.g. Mid-Senior'></div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Salary Min ($)</label><input type='number' class='cms-form-control' name='salary_min' id='edit-job-salary-min'></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Salary Max ($)</label><input type='number' class='cms-form-control' name='salary_max' id='edit-job-salary-max'></div>\n"
        "      </div>\n"
        "    </div>\n"
        "    <div class='cms-tab-pane' id='admin-job-tab-apply'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Application URL</label><input class='cms-form-control' name='apply_url' id='edit-job-apply-url' placeholder='https://...'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Application Email</label><input class='cms-form-control' name='apply_email' id='edit-job-apply-email' placeholder='careers@company.com'></div>\n"
        "    </div>\n"
        "    <div class='cms-tab-pane' id='admin-job-tab-settings'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Listing Status</label><select class='cms-form-control' name='status' id='edit-job-status'><option value='active'>Published (Active)</option><option value='draft'>Draft</option><option value='archived'>Archived</option></select></div>\n"
        "      <label class='cms-toggle-row'><span>Featured Job Listing</span><span class='cms-switch'><input type='checkbox' name='featured' id='edit-job-featured' value='1'><span class='cms-switch-slider'></span></span></label>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        "</form>\n"
        "<div class='cms-modal-footer'>\n"
        "<div class='cms-footer-left'><button type='button' class='cms-btn cms-btn-cancel' onclick='closeAllModals()'>Cancel</button><button type='button' class='cms-btn cms-btn-archive' onclick=\"submitCmsPublish('admin-edit-job-form','archived')\"><i class='fa-solid fa-box-archive'></i> Archive</button></div>\n"
        "<div class='cms-footer-right'><button type='button' class='cms-btn cms-btn-draft' onclick=\"submitCmsPublish('admin-edit-job-form','draft')\"><i class='fa-regular fa-floppy-disk'></i> Save Draft</button><button type='button' class='cms-btn cms-btn-save' onclick=\"submitCmsPublish('admin-edit-job-form','active')\"><i class='fa-solid fa-paper-plane'></i> Publish Job</button></div>\n"
        "</div>\n"
        "</div></div>\n"

        "<!-- Company Edit Modal (Landscape 3-Column) -->\n"
        "<div class='admin-modal-backdrop cms-modal-backdrop' id='edit-company-modal'>\n"
        "<div class='cms-modal-dialog'>\n"
        "<div class='cms-modal-header'>\n"
        "<h3 class='cms-modal-title'><i class='fa-solid fa-building' style='color:#2563eb;'></i> Edit Company</h3>\n"
        "<div class='cms-header-actions'>\n"
        "<button type='button' class='cms-header-preview-btn' onclick=\"var s=document.getElementById('edit-company-slug').value; if(s) previewCmsItem('/company/'+s);\"><i class='fa-regular fa-eye'></i> Preview</button>\n"
        "<button type='button' class='cms-modal-close' onclick='closeAllModals()'><i class='fa-solid fa-xmark'></i></button>\n"
        "</div>\n"
        "</div>\n"
        "<form method='post' action='/admin/companies/update' id='admin-edit-company-form' class='cms-modal-body'>\n"
        "<input type='hidden' name='id' id='edit-company-id'>\n"
        "<input type='hidden' name='slug' id='edit-company-slug'>\n"
        "<input type='hidden' name='tab' id='edit-company-tab' value='companies'>\n"
        "<input type='hidden' name='status' id='edit-company-status' value='published'>\n"
        "<input type='hidden' name='social_links' id='edit-company-social-links'>\n"
        f"{_csrf_field()}\n"
        "<div class='cms-layout-3col'>\n"
        "  <div class='cms-col-left'>\n"
        "    <div class='cms-logo-box'>\n"
        "      <img id='edit-company-logo-prev' src='/static/images/logo_emblem.png' alt='Logo' onerror=\"this.onerror=null;this.src='/static/images/logo_emblem.png'\">\n"
        "      <label class='cms-btn-sm-outline'><i class='fa-solid fa-camera'></i> Change Logo<input type='file' accept='image/*' style='display:none;' onchange=\"handleCmsImageUpload(this, 'edit-company-logo-url', 'edit-company-logo-prev')\"></label>\n"
        "      <input class='cms-form-control' id='edit-company-logo-url' name='logo_url' placeholder='Logo URL...' style='font-size:11.5px;padding:5px 8px;' oninput=\"updateCmsImagePreview(this.value, 'edit-company-logo-prev')\">\n"
        "    </div>\n"
        "    <div class='cms-cover-card'>\n"
        "      <img id='edit-company-banner-prev' src='/static/images/fw_today_1.jpg' alt='Banner' onerror=\"this.onerror=null;this.src='/static/images/fw_today_1.jpg'\">\n"
        "      <label class='cms-cover-overlay-btn'><i class='fa-solid fa-camera'></i> Change Banner<input type='file' accept='image/*' style='display:none;' onchange=\"handleCmsImageUpload(this, 'edit-company-banner-url', 'edit-company-banner-prev')\"></label>\n"
        "    </div>\n"
        "    <input class='cms-form-control' id='edit-company-banner-url' name='banner_url' placeholder='Banner URL...' style='font-size:11.5px;padding:5px 8px;' oninput=\"updateCmsImagePreview(this.value, 'edit-company-banner-prev')\">\n"
        "    <nav class='cms-side-nav'>\n"
        "      <button type='button' class='cms-side-nav-btn active' onclick=\"switchCmsTab(this,'admin-comp-tab-overview')\"><i class='fa-solid fa-house'></i> Overview</button>\n"
        "      <button type='button' class='cms-side-nav-btn' onclick=\"switchCmsTab(this,'admin-comp-tab-benefits')\"><i class='fa-solid fa-gift'></i> Benefits &amp; Offices</button>\n"
        "    </nav>\n"
        "  </div>\n"
        "  <div class='cms-col-center'>\n"
        "    <div class='cms-tab-pane active' id='admin-comp-tab-overview'>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Company Name *</label><input class='cms-form-control' name='name' id='edit-company-name' required></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Tagline</label><input class='cms-form-control' name='tagline' id='edit-company-tagline'></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Industries</label><input class='cms-form-control' name='industries' id='edit-company-industries'></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Location</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-location-dot'></i><input class='cms-form-control' name='location' id='edit-company-location'></div></div>\n"
        "      </div>\n"
        "      <div class='cms-grid-2'>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Employees</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-users'></i><input type='number' class='cms-form-control' name='employees' id='edit-company-employees'></div></div>\n"
        "        <div class='cms-form-group'><label class='cms-form-label'>Website</label><div class='cms-input-icon-wrap'><i class='fa-solid fa-globe'></i><input class='cms-form-control' name='website' id='edit-company-website'></div></div>\n"
        "      </div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>About the Company</label><textarea class='cms-form-control' name='description' id='edit-company-description' rows='6'></textarea></div>\n"
        "    </div>\n"
        "    <div class='cms-tab-pane' id='admin-comp-tab-benefits'>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Benefits</label><input class='cms-form-control' name='benefits' id='edit-company-benefits'></div>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Offices</label><input class='cms-form-control' name='offices' id='edit-company-offices'></div>\n"
        "    </div>\n"
        "  </div>\n"
        "  <div class='cms-col-right'>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>Company Settings</h4>\n"
        "      <label class='cms-toggle-row'><span><i class='fa-solid fa-circle-check' style='color:#2563eb;'></i> Verified Company</span><span class='cms-switch'><input type='checkbox' name='verified' id='edit-company-verified' value='1'><span class='cms-switch-slider'></span></span></label>\n"
        "      <label class='cms-toggle-row'><span>Featured Company</span><span class='cms-switch'><input type='checkbox' name='featured' id='edit-company-featured' value='1'><span class='cms-switch-slider'></span></span></label>\n"
        "      <label class='cms-toggle-row'><span>Active Status</span><span class='cms-switch'><input type='checkbox' id='edit-company-active-toggle' checked onchange=\"document.getElementById('edit-company-status').value=this.checked?'published':'draft'\"><span class='cms-switch-slider'></span></span></label>\n"
        "      <div class='cms-form-group'><label class='cms-form-label'>Brand Color</label><div class='cms-color-row'><input type='color' class='cms-color-swatch' id='edit-company-color-swatch' oninput=\"document.getElementById('edit-company-color').value=this.value\"><input class='cms-form-control' name='color' id='edit-company-color'></div></div>\n"
        "    </div>\n"
        "    <div class='cms-side-box'>\n"
        "      <h4 class='cms-side-box-title'>Social Links</h4>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-linkedin' style='color:#0a66c2;'></i></span><input class='cms-form-control cms-social-linkedin' id='edit-company-soc-li' placeholder='LinkedIn URL'></div>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-youtube' style='color:#dc2626;'></i></span><input class='cms-form-control cms-social-youtube' id='edit-company-soc-yt' placeholder='YouTube / X URL'></div>\n"
        "      <div class='cms-social-row'><span class='cms-social-icon'><i class='fa-brands fa-facebook' style='color:#1877f2;'></i></span><input class='cms-form-control cms-social-facebook' id='edit-company-soc-fb' placeholder='Facebook URL'></div>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        "</form>\n"
        "<div class='cms-modal-footer'>\n"
        "<div class='cms-footer-left'><button type='button' class='cms-btn cms-btn-cancel' onclick='closeAllModals()'>Cancel</button><button type='button' class='cms-btn cms-btn-archive' onclick=\"submitCmsPublish('admin-edit-company-form','archived')\"><i class='fa-solid fa-box-archive'></i> Archive</button></div>\n"
        "<div class='cms-footer-right'><button type='button' class='cms-btn cms-btn-draft' onclick=\"submitCmsPublish('admin-edit-company-form','draft')\"><i class='fa-regular fa-floppy-disk'></i> Save Draft</button><button type='button' class='cms-btn cms-btn-save' onclick=\"submitCmsPublish('admin-edit-company-form','published')\"><i class='fa-solid fa-check'></i> Save Changes</button></div>\n"
        "</div>\n"
        "</div></div>\n"

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
        "function openCreateModal(modalId) {\n"
        "  var m = document.getElementById(modalId);\n"
        "  if (m) m.classList.add('active');\n"
        "}\n"
        "function openSmartCreateModal() {\n"
        "  var tab = new URLSearchParams(window.location.search).get('tab') || 'overview';\n"
        "  var map = {\n"
        "    'articles': 'create-article-modal',\n"
        "    'videos': 'create-video-modal',\n"
        "    'jobs': 'create-job-modal',\n"
        "    'companies': 'create-company-modal',\n"
        "    'users': 'create-user-modal',\n"
        "    'salaries': 'create-salary-modal',\n"
        "    'courses': 'create-course-modal'\n"
        "  };\n"
        "  var mId = map[tab] || 'create-article-modal';\n"
        "  openCreateModal(mId);\n"
        "}\n"
        "document.querySelectorAll('.admin-modal-backdrop').forEach(function(m) {\n"
        "  m.addEventListener('click', function(e) { if(e.target === this) closeAllModals(); });\n"
        "});\n"
        "document.addEventListener('keydown', function(e) { if(e.key === 'Escape') closeAllModals(); });\n"
        "function convertMarkdownToVisualHtml(text) {\n"
        "  if (!text) return '';\n"
        "  var s = String(text);\n"
        "  s = s.replace(/!\\[(.*?)\\]\\(\\s*<a\\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>.*?<\\/a>([^)]*)\\)/gi, function(m, cap, u1, u2) {\n"
        "    var url = (u1 + (u2 || '')).trim();\n"
        "    var alt = cap ? cap.trim() : 'Article Photo';\n"
        "    return '<figure style=\"margin:24px auto;text-align:center;\"><img src=\"' + url + '\" alt=\"' + alt + '\" style=\"max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;\" /><figcaption style=\"font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;\">' + alt + '</figcaption></figure>';\n"
        "  });\n"
        "  s = s.replace(/!\\[(.*?)\\]\\(\\s*(https?:\\/\\/[^\\s)<>\"]+)\\s*\\)/gi, function(m, cap, url) {\n"
        "    var alt = cap ? cap.trim() : 'Article Photo';\n"
        "    return '<figure style=\"margin:24px auto;text-align:center;\"><img src=\"' + url + '\" alt=\"' + alt + '\" style=\"max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;\" /><figcaption style=\"font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;\">' + alt + '</figcaption></figure>';\n"
        "  });\n"
        "  s = s.replace(/\\[(.*?)\\]\\(\\s*(https?:\\/\\/[^\\s)<>\"]*(?:unsplash\\.com|cloudinary\\.com|\\.(?:png|jpg|jpeg|webp|gif|svg))[^\\s)<>\"]*)\\s*\\)/gi, function(m, cap, url) {\n"
        "    var alt = cap ? cap.trim() : 'Article Photo';\n"
        "    return '<figure style=\"margin:24px auto;text-align:center;\"><img src=\"' + url + '\" alt=\"' + alt + '\" style=\"max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;\" /><figcaption style=\"font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;\">' + alt + '</figcaption></figure>';\n"
        "  });\n"
        "  s = s.replace(/^##\\s+([^<\\n\\r]+)/gm, '<h2 style=\"font-size:22px;font-weight:800;color:#0f172a;margin:28px 0 12px;\">$1</h2>');\n"
        "  s = s.replace(/^###\\s+([^<\\n\\r]+)/gm, '<h3 style=\"font-size:18px;font-weight:700;color:#0f172a;margin:24px 0 10px;\">$1</h3>');\n"
        "  s = s.replace(/^>\\s+([^<\\n\\r]+)/gm, '<blockquote style=\"border-left:4px solid #3874ff;padding:12px 18px;margin:24px 0;background:#f0f7ff;border-radius:0 8px 8px 0;font-style:italic;color:#1e3a8a;\">$1</blockquote>');\n"
        "  if (!/<(?:p|figure|div|h[1-6]|blockquote)\\b/i.test(s)) {\n"
        "    var paras = s.split(/\\n\\s*\\n/);\n"
        "    s = paras.map(function(p) { p = p.trim(); return p ? '<p style=\"margin-bottom:18px;line-height:1.75;font-size:16px;\">' + p + '</p>' : ''; }).join('\\n');\n"
        "  }\n"
        "  return s;\n"
        "}\n"
        "function insertUploadedImageToEditor(fileInput, targetEditorId) {\n"
        "  if (!fileInput.files || !fileInput.files[0]) return;\n"
        "  var file = fileInput.files[0];\n"
        "  var reader = new FileReader();\n"
        "  reader.onload = function(e) {\n"
        "    var img = new Image();\n"
        "    img.onload = function() {\n"
        "      var maxW = 1200, maxH = 900;\n"
        "      var w = img.width, h = img.height;\n"
        "      if (w > maxW || h > maxH) {\n"
        "        if (w / maxW > h / maxH) { h = Math.round(h * (maxW / w)); w = maxW; }\n"
        "        else { w = Math.round(w * (maxH / h)); h = maxH; }\n"
        "      }\n"
        "      var canvas = document.createElement('canvas');\n"
        "      canvas.width = w; canvas.height = h;\n"
        "      var ctx = canvas.getContext('2d');\n"
        "      ctx.drawImage(img, 0, 0, w, h);\n"
        "      var optimized = canvas.toDataURL('image/jpeg', 0.86);\n"
        "      var figureHtml = '<figure style=\"margin:24px auto;text-align:center;\"><img src=\"' + optimized + '\" alt=\"' + file.name + '\" style=\"max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;\" /><figcaption style=\"font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;\">' + file.name + '</figcaption></figure><p>&nbsp;</p>';\n"
        "      var ed = window.tinymce ? tinymce.get(targetEditorId) : null;\n"
        "      if (ed) { ed.insertContent(figureHtml); ed.focus(); }\n"
        "      fileInput.value = '';\n"
        "    };\n"
        "    img.src = e.target.result;\n"
        "  };\n"
        "  reader.readAsDataURL(file);\n"
        "}\n"
        "function _populateChipWrap(wrapId, hiddenId, csvStr, label) {\n"
        "  var wrap = document.getElementById(wrapId);\n"
        "  if (!wrap) return;\n"
        "  wrap.querySelectorAll('.cms-chip-pill').forEach(function(el) { el.remove(); });\n"
        "  var addBtn = wrap.querySelector('.cms-chip-add-btn');\n"
        "  (csvStr || '').split(',').map(function(s){return s.trim();}).filter(Boolean).forEach(function(val) {\n"
        "    var sp = document.createElement('span');\n"
        "    sp.className = 'cms-chip-pill';\n"
        "    sp.setAttribute('data-val', val);\n"
        "    sp.innerHTML = val.replace(/</g,'&lt;') + ' <button type=\"button\" class=\"cms-chip-remove\" onclick=\"removeCmsChip(this, \\'' + wrapId + '\\', \\'' + hiddenId + '\\')\">&times;</button>';\n"
        "    if (addBtn) wrap.insertBefore(sp, addBtn);\n"
        "  });\n"
        "  var hid = document.getElementById(hiddenId);\n"
        "  if (hid) hid.value = csvStr || '';\n"
        "}\n"
        "function openArticleEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-article-id').value = d.id || '';\n"
        "  document.getElementById('edit-article-tab').value = d.tab || 'articles';\n"
        "  document.getElementById('edit-article-slug').value = d.slug || '';\n"
        "  document.getElementById('edit-article-title').value = d.title || '';\n"
        "  document.getElementById('edit-article-category').value = d.category || '';\n"
        "  document.getElementById('edit-article-author').value = d.author || '';\n"
        "  _populateChipWrap('edit-art-tags-wrap', 'edit-article-tag', d.tag || '', 'tag');\n"
        "  document.getElementById('edit-article-read-time').value = d.readTime || '';\n"
        "  document.getElementById('edit-article-guest').value = d.guest || '';\n"
        "  document.getElementById('edit-article-duration').value = d.duration || '';\n"
        "  document.getElementById('edit-article-thumb').value = d.thumb || '';\n"
        "  updateImagePreview(d.thumb, 'edit-article-preview');\n"
        "  document.getElementById('edit-article-excerpt').value = d.excerpt || '';\n"
        "  document.getElementById('edit-article-status').value = d.status || 'published';\n"
        "  document.getElementById('edit-article-published').value = d.published || '';\n"
        "  document.getElementById('edit-article-seo-title').value = d.seoTitle || d.title || '';\n"
        "  document.getElementById('edit-article-seo-description').value = d.seoDescription || d.excerpt || '';\n"
        "  document.getElementById('edit-article-featured').checked = (d.featured === '1');\n"
        "  document.getElementById('edit-article-allow-comments').checked = (d.allowComments !== '0');\n"
        "  var bodyVal = d.body || '';\n"
        "  var visualHtml = convertMarkdownToVisualHtml(bodyVal);\n"
        "  var bodyEl = document.getElementById('edit-article-body');\n"
        "  if (bodyEl) bodyEl.value = visualHtml;\n"
        "  if (window.tinymce && tinymce.get('edit-article-body')) {\n"
        "    tinymce.get('edit-article-body').setContent(visualHtml);\n"
        "  }\n"
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
        "  var ed = window.tinymce ? tinymce.get(targetBodyId) : null;\n"
        "  if (mode === 'gallery2') {\n"
        "    var g2 = '<div style=\"display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin:28px 0;\"><figure style=\"margin:0;\"><img src=\"https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80\" alt=\"Berth Operations &amp; Gantry Crane\" style=\"width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);\" /><figcaption style=\"font-size:12px;color:#64748b;text-align:center;margin-top:4px;\">Berth Operations &amp; Gantry Crane</figcaption></figure><figure style=\"margin:0;\"><img src=\"https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80\" alt=\"Automated Cargo Vessel\" style=\"width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);\" /><figcaption style=\"font-size:12px;color:#64748b;text-align:center;margin-top:4px;\">Automated Cargo Vessel</figcaption></figure></div><p>&nbsp;</p>';\n"
        "    if (ed) { ed.insertContent(g2); ed.focus(); return; }\n"
        "    var txt = document.getElementById(targetBodyId);\n"
        "    if (txt) { txt.value += g2; txt.focus(); }\n"
        "    return;\n"
        "  }\n"
        "  if (mode === 'gallery3') {\n"
        "    var g3 = '<div style=\"display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:16px;margin:28px 0;\"><figure style=\"margin:0;\"><img src=\"https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80\" alt=\"Deepwater Quay\" style=\"width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);\" /><figcaption style=\"font-size:12px;color:#64748b;text-align:center;margin-top:4px;\">Deepwater Quay</figcaption></figure><figure style=\"margin:0;\"><img src=\"https://images.unsplash.com/photo-1542296332-2e4473faf563?auto=format&fit=crop&w=800&q=80\" alt=\"Smart Container Yard\" style=\"width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);\" /><figcaption style=\"font-size:12px;color:#64748b;text-align:center;margin-top:4px;\">Smart Container Yard</figcaption></figure><figure style=\"margin:0;\"><img src=\"https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80\" alt=\"Intermodal Rail Connection\" style=\"width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);\" /><figcaption style=\"font-size:12px;color:#64748b;text-align:center;margin-top:4px;\">Intermodal Rail Connection</figcaption></figure></div><p>&nbsp;</p>';\n"
        "    if (ed) { ed.insertContent(g3); ed.focus(); return; }\n"
        "    var txt = document.getElementById(targetBodyId);\n"
        "    if (txt) { txt.value += g3; txt.focus(); }\n"
        "    return;\n"
        "  }\n"
        "  var url = prompt('Enter Image / Photo URL (e.g. Unsplash, Web URL, or Cloudinary):', 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80');\n"
        "  if (!url) return;\n"
        "  var cap = prompt('Enter caption for this image (optional):', 'Port operations and logistics facility');\n"
        "  var fig = '<figure style=\"margin:24px auto;text-align:center;\"><img src=\"' + url + '\" alt=\"' + (cap || 'Article Photo') + '\" style=\"max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;\" />' + (cap ? '<figcaption style=\"font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;\">' + cap + '</figcaption>' : '') + '</figure><p>&nbsp;</p>';\n"
        "  if (ed) {\n"
        "    ed.insertContent(fig);\n"
        "    ed.focus(); return;\n"
        "  }\n"
        "  var txt = document.getElementById(targetBodyId);\n"
        "  if (txt) { txt.value += fig; txt.focus(); }\n"
        "}\n"
        "function openJobEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-job-id').value = d.id || '';\n"
        "  document.getElementById('edit-job-slug').value = d.slug || '';\n"
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
        "  _populateChipWrap('edit-job-skills-wrap', 'edit-job-skills', d.skills || '', 'skill');\n"
        "  document.getElementById('edit-job-description').value = d.description || '';\n"
        "  document.getElementById('edit-job-apply-url').value = d.applyUrl || '';\n"
        "  document.getElementById('edit-job-apply-email').value = d.applyEmail || '';\n"
        "  document.getElementById('edit-job-status').value = d.status || 'active';\n"
        "  document.getElementById('edit-job-featured').checked = (d.featured === '1');\n"
        "  var av = document.getElementById('edit-job-company-avatar');\n"
        "  if (av) { av.textContent = d.companyInitials || 'CO'; av.style.background = d.companyColor || '#2563eb'; }\n"
        "  var cn = document.getElementById('edit-job-company-name');\n"
        "  if (cn) cn.textContent = d.companyName || 'Company';\n"
        "  var cl = document.getElementById('edit-job-company-loc');\n"
        "  if (cl) cl.textContent = d.location || 'Remote';\n"
        "  document.getElementById('edit-job-modal').classList.add('active');\n"
        "}\n"
        "function openCompanyEditModal(btn) {\n"
        "  var d = btn.dataset;\n"
        "  document.getElementById('edit-company-id').value = d.id || '';\n"
        "  document.getElementById('edit-company-slug').value = d.slug || '';\n"
        "  document.getElementById('edit-company-tab').value = d.tab || 'companies';\n"
        "  document.getElementById('edit-company-name').value = d.name || '';\n"
        "  document.getElementById('edit-company-tagline').value = d.tagline || '';\n"
        "  document.getElementById('edit-company-industries').value = d.industries || '';\n"
        "  document.getElementById('edit-company-location').value = d.location || '';\n"
        "  document.getElementById('edit-company-employees').value = d.employees || '';\n"
        "  var clr = d.color || '#2563eb';\n"
        "  document.getElementById('edit-company-color').value = clr;\n"
        "  document.getElementById('edit-company-color-swatch').value = /^#[0-9A-Fa-f]{6}$/.test(clr) ? clr : '#2563eb';\n"
        "  document.getElementById('edit-company-website').value = d.website || '';\n"
        "  document.getElementById('edit-company-description').value = d.description || '';\n"
        "  document.getElementById('edit-company-benefits').value = d.benefits || '';\n"
        "  document.getElementById('edit-company-offices').value = d.offices || '';\n"
        "  document.getElementById('edit-company-logo-url').value = d.logoUrl || '';\n"
        "  updateCmsImagePreview(d.logoUrl || '/static/images/logo_emblem.png', 'edit-company-logo-prev');\n"
        "  document.getElementById('edit-company-banner-url').value = d.bannerUrl || '';\n"
        "  updateCmsImagePreview(d.bannerUrl || '/static/images/fw_today_1.jpg', 'edit-company-banner-prev');\n"
        "  document.getElementById('edit-company-status').value = d.status || 'published';\n"
        "  document.getElementById('edit-company-active-toggle').checked = ((d.status || 'published') === 'published');\n"
        "  document.getElementById('edit-company-verified').checked = (d.verified !== '0');\n"
        "  document.getElementById('edit-company-featured').checked = (d.featured === '1');\n"
        "  var soc = (d.socialLinks || '').split(',').map(function(s){return s.trim();}).filter(Boolean);\n"
        "  document.getElementById('edit-company-soc-li').value = soc[0] || '';\n"
        "  document.getElementById('edit-company-soc-yt').value = soc[1] || '';\n"
        "  document.getElementById('edit-company-soc-fb').value = soc[2] || '';\n"
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
                "SELECT id, slug, title, company_id, company_slug, company_name, category, level, workplace, location, salary_min, salary_max, salary_display, skills, description, posted_at, COALESCE(featured, 0) AS featured, COALESCE(status, 'active') AS status "
                "FROM jobs WHERE title LIKE ? ESCAPE '\\' OR company_name LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\' "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (like, like, like, j_limit, j_offset)
            ).fetchall()]
        else:
            all_jobs = [dict(r) for r in conn.execute(
                "SELECT id, slug, title, company_id, company_slug, company_name, category, level, workplace, location, salary_min, salary_max, salary_display, skills, description, posted_at, COALESCE(featured, 0) AS featured, COALESCE(status, 'active') AS status "
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
                "SELECT id, slug, name, initials, color, tagline, industries, location, employees, website, description, open_jobs, COALESCE(verified, 1) AS verified "
                "FROM companies WHERE name LIKE ? ESCAPE '\\' OR industries LIKE ? ESCAPE '\\' OR location LIKE ? ESCAPE '\\' "
                "ORDER BY name ASC LIMIT ? OFFSET ?",
                (like, like, like, per_page, offset)
            ).fetchall()]
        else:
            tab_total = counts["companies"]
            all_companies = [dict(r) for r in conn.execute(
                "SELECT id, slug, name, initials, color, tagline, industries, location, employees, website, description, open_jobs, COALESCE(verified, 1) AS verified "
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
            "data-id='" + str(v['id']) + "' data-tab='" + tab_ctx + "' data-slug='" + e(v.get('slug') or '') + "' "
            "data-title='" + e(v['title']) + "' data-category='" + e(v.get('category') or '') + "' "
            "data-author='" + e(v.get('author') or '') + "' data-tag='" + e(v.get('tag') or 'Logistic Waves Today') + "' "
            "data-read-time='" + e(v.get('read_time') or '') + "' data-guest='" + e(v.get('guest') or '') + "' "
            "data-duration='" + e(v.get('duration') or '') + "' data-thumb='" + e(v.get('thumb') or '') + "' "
            "data-excerpt='" + e(v.get('excerpt') or '') + "' data-body='" + e(v.get('body') or '') + "' "
            "data-status='" + e(v.get('status') or 'published') + "' data-published='" + e(v.get('published') or '') + "' "
            "data-seo-title='" + e(v.get('seo_title') or '') + "' data-seo-description='" + e(v.get('seo_description') or '') + "' "
            "data-featured='" + str(v.get('featured') or 0) + "' data-allow-comments='" + str(v.get('allow_comments', 1)) + "' "
            "onclick='openArticleEditModal(this)'><i class='fa-solid fa-pen-to-square'></i></button>"
            "<a href='/articles/" + e(v['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='id' value='" + str(v['id']) + "'>"
            "<input type='hidden' name='tab' value='" + tab_ctx + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    def _excel_input(table, row_id, field, val, placeholder="", input_type="text", extra_style=""):
        return (
            f"<input type='{input_type}' class='excel-cell' value='{e(val)}' placeholder='{e(placeholder)}' "
            f"style='{extra_style}' "
            f"data-orig='{e(val)}' "
            f"onchange=\"saveInlineCell(this, '{table}', {int(row_id)}, '{field}')\" "
            f"onkeydown=\"if(event.key==='Enter'){{event.preventDefault();this.blur();}}\">"
        )

    def _excel_select(table, row_id, field, current, options):
        opts_html = "".join(
            f"<option value='{e(o)}'{' selected' if str(o) == str(current) else ''}>{e(o)}</option>"
            for o in options
        )
        return (
            f"<select class='excel-cell excel-select' "
            f"onchange=\"saveInlineCell(this, '{table}', {int(row_id)}, '{field}')\">{opts_html}</select>"
        )

    def render_job_row(j, tab_ctx):
        is_overview = (tab_ctx == "overview")
        c_clr = e(j.get('company_color') or '#2563eb')
        c_init = e(j.get('company_initials') or 'CO')
        st_val = (j.get('status') or 'active').lower()
        st_pill = "<span class='pill-badge pill-green'>Active</span>" if st_val == "active" else ("<span class='pill-badge pill-amber'>Draft</span>" if st_val == "draft" else "<span class='pill-badge'>Archived</span>")
        title_cell = (
            "<td style='min-width:220px;'><div style='display:flex;align-items:center;gap:10px;'>"
            "<span style='display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:" + c_clr + ";color:#fff;font-weight:800;font-size:11.5px;flex-shrink:0;'>" + c_init + "</span>"
            "<div style='min-width:0;'><div style='font-weight:700;color:#0f172a;line-height:1.3;'>" + e(j['title']) + "</div>"
            "<small style='color:#64748b;'>" + e(j['company_name']) + "</small></div></div></td>"
        )
        cat_td = "<td><div style='font-size:12.5px;font-weight:600;color:#334155;'>" + e(j.get('category') or 'General') + "</div><span class='pill-badge pill-blue' style='margin-top:3px;'>" + e(j.get('workplace') or 'Hybrid') + "</span></td>"
        loc_td = "<td><div style='font-size:12.5px;color:#475569;'>" + e(j.get('location') or 'Remote') + "</div><div style='font-size:12.5px;font-weight:700;color:#0f172a;margin-top:2px;'>" + e(j['salary_display'] or 'Competitive') + "</div></td>"
        feat_td = "" if is_overview else ("<td>" + st_pill + (" <span class='pill-badge pill-amber'>&#9733;</span>" if j.get('featured') else "") + "</td>")
        posted_td = "" if is_overview else "<td style='color:#64748b;font-size:12.5px;white-space:nowrap;'>" + e(j['posted_at']) + "</td>"
        return (
            "<tr>"
            + title_cell + cat_td + loc_td + feat_td + posted_td +
            "<td style='width:140px;text-align:center;'>"
            "<div class='action-btns' style='justify-content:center;'>"
            "<button type='button' class='btn-action-round btn-action-edit' title='Manage Full Details (Wrench)' "
            "data-id='" + str(j['id']) + "' data-tab='" + tab_ctx + "' data-slug='" + e(j.get('slug') or '') + "' "
            "data-title='" + e(j['title']) + "' data-company-slug='" + e(j.get('company_slug') or '') + "' "
            "data-company-name='" + e(j.get('company_name') or '') + "' data-company-color='" + c_clr + "' data-company-initials='" + c_init + "' "
            "data-category='" + e(j.get('category') or '') + "' data-level='" + e(j.get('level') or 'Mid-Senior') + "' "
            "data-workplace='" + e(j.get('workplace') or 'Hybrid') + "' data-location='" + e(j.get('location') or '') + "' "
            "data-salary-min='" + str(j.get('salary_min') or 50000) + "' data-salary-max='" + str(j.get('salary_max') or 85000) + "' "
            "data-salary-display='" + e(j.get('salary_display') or '') + "' data-skills='" + e(j.get('skills') or '') + "' "
            "data-description='" + e(j.get('description') or '') + "' data-status='" + e(j.get('status') or 'active') + "' "
            "data-apply-url='" + e(j.get('apply_url') or '') + "' data-apply-email='" + e(j.get('apply_email') or '') + "' "
            "data-featured='" + str(j.get('featured') or 0) + "' "
            "onclick='openJobEditModal(this)'><i class='fa-solid fa-wrench'></i></button>"
            "<a href='/job/" + e(j['slug']) + "/" + str(j['id']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/jobs/duplicate' style='display:inline;'>"
            f"{_csrf_field()}"
            "<input type='hidden' name='id' value='" + str(j['id']) + "'>"
            "<input type='hidden' name='tab' value='" + tab_ctx + "'>"
            "<button type='submit' class='btn-action-round' title='Duplicate &amp; Edit'><i class='fa-regular fa-copy'></i></button>"
            "</form>"
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
            _empty_row(7, 'No Today episodes yet. Click "Seed Today Videos" on Overview.')
        active_content = (
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-video' style='color:#3874ff;margin-right:8px;'></i> Today Episodes (" + str(len(today_videos)) + ")</h3>"
            "<span style='font-size:13px;color:#64748b;'>Feeds homepage &amp; article-blogs</span></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' onclick=\"openCreateModal('create-video-modal')\"><i class='fa-solid fa-plus'></i> Add Today Video</button>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Thumb</th><th>Title &amp; Slug</th><th>Guest</th><th>Category</th><th>Duration</th><th>Date</th><th>Action</th></tr></thead>"
            "<tbody>" + video_rows + "</tbody>"
            "</table></div>"
        )

    elif tab == "articles":
        def article_row(a):
            today_badge = "<span class='pill-badge pill-blue' style='margin-left:6px;'>Today</span>" if a['is_today'] else ""
            return (
                "<tr>"
                "<td style='min-width:240px;'>" + _excel_input("articles", a['id'], "title", a['title'], "Title", extra_style="font-weight:700;color:#0f172a;") +
                "<small style='color:#64748b;padding-left:6px;'>/" + e(a['slug']) + "</small>" + today_badge + "</td>"
                "<td>" + _excel_input("articles", a['id'], "category", a.get('category') or 'General', "Category") + "</td>"
                "<td>" + _excel_input("articles", a['id'], "tag", a.get('tag') or '', "Tag") + "</td>"
                "<td>" + _excel_input("articles", a['id'], "author", a.get('author') or 'Editorial Staff', "Author") + "</td>"
                "<td style='white-space:nowrap;color:#64748b;'>" + e(a['published']) + "</td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Manage Full Details (Wrench)' "
                "data-id='" + str(a['id']) + "' data-tab='articles' data-slug='" + e(a.get('slug') or '') + "' "
                "data-title='" + e(a['title']) + "' data-category='" + e(a.get('category') or '') + "' "
                "data-author='" + e(a.get('author') or '') + "' data-tag='" + e(a.get('tag') or '') + "' "
                "data-read-time='" + e(a.get('read_time') or '') + "' data-guest='" + e(a.get('guest') or '') + "' "
                "data-duration='" + e(a.get('duration') or '') + "' data-thumb='" + e(a.get('thumb') or '') + "' "
                "data-excerpt='" + e(a.get('excerpt') or '') + "' data-body='" + e(a.get('body') or '') + "' "
                "data-status='" + e(a.get('status') or 'published') + "' data-published='" + e(a.get('published') or '') + "' "
                "data-seo-title='" + e(a.get('seo_title') or '') + "' data-seo-description='" + e(a.get('seo_description') or '') + "' "
                "data-featured='" + str(a.get('featured') or 0) + "' data-allow-comments='" + str(a.get('allow_comments', 1)) + "' "
                "onclick='openArticleEditModal(this)'><i class='fa-solid fa-wrench'></i></button>"
                "<a href='/articles/" + e(a['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
                "<form method='post' action='/admin/articles/duplicate' style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
                "<input type='hidden' name='tab' value='articles'>"
                "<button type='submit' class='btn-action-round' title='Duplicate &amp; Edit'><i class='fa-regular fa-copy'></i></button>"
                "</form>"
                "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
                "<input type='hidden' name='tab' value='articles'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        articles_rows = "".join([article_row(a) for a in all_articles]) or _empty_row(6, "No articles found.")
        active_content = (
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-file-lines' style='color:#3874ff;margin-right:8px;'></i> All Articles &amp; Reports (" + str(tab_total if tab_total is not None else counts['articles']) + ")</h3></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' onclick=\"openCreateModal('create-article-modal')\"><i class='fa-solid fa-plus'></i> Add New Article</button>"
            "<span id='excelSaveStatus' style='font-size:12px;font-weight:700;color:#10b981;display:none;'>Saved ✓</span>"
            "<button type='button' class='btn-ctrl btn-ctrl-light' onclick=\"exportAdminTableCSV(this, 'articles.csv')\" style='padding:6px 12px;font-size:12px;'><i class='fa-solid fa-file-excel' style='color:#10b981;'></i> Export Excel</button>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Title &amp; Slug</th><th>Category</th><th>Tag</th><th>Author</th><th>Date</th><th>Action</th></tr></thead>"
            "<tbody>" + articles_rows + "</tbody>"
            "</table>" + _render_pagination("articles", page, tab_total if tab_total is not None else counts["articles"], per_page, q) + "</div>"
        )

    elif tab == "jobs":
        company_options = "".join([
            "<option value='" + e(c["slug"]) + "'>" + e(c["name"]) + "</option>"
            for c in all_companies
        ])
        jobs_rows = "".join([render_job_row(j, "jobs") for j in all_jobs]) or _empty_row(7, "No jobs found.")
        active_content = (
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-briefcase' style='color:#10b981;margin-right:8px;'></i> Active Job Listings (" + str(total_jobs_count) + ")</h3></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' style='background:#10b981;' onclick=\"openCreateModal('create-job-modal')\"><i class='fa-solid fa-plus'></i> Post New Job</button>"
            "<span id='excelSaveStatus' style='font-size:12px;font-weight:700;color:#10b981;display:none;'>Saved ✓</span>"
            "<button type='button' class='btn-ctrl btn-ctrl-light' onclick=\"exportAdminTableCSV(this, 'jobs.csv')\" style='padding:6px 12px;font-size:12px;'><i class='fa-solid fa-file-excel' style='color:#10b981;'></i> Export Excel</button>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Role &amp; Company</th><th>Category &amp; Type</th><th>Location &amp; Salary</th><th>Status</th><th>Posted</th><th style='text-align:center;'>Action</th></tr></thead>"
            "<tbody>" + jobs_rows + "</tbody>"
            "</table>" + _render_pagination("jobs", page, total_jobs_count, per_page, q) + "</div>"
        )

    elif tab == "companies":
        def company_row(c):
            clr = e(c.get('color') or '#3874ff')
            return (
                "<tr>"
                "<td style='min-width:210px;'><div style='display:flex;align-items:center;gap:10px;'>"
                "<span style='display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:" + clr + ";color:#fff;font-weight:800;font-size:12px;flex-shrink:0;'>" + e(c.get('initials') or 'CO') + "</span>"
                "<div style='flex:1;min-width:0;'>" + _excel_input("companies", c['id'], "name", c.get('name') or '', "Company Name", extra_style="font-weight:700;color:#0f172a;") +
                "<small style='color:#64748b;padding-left:6px;'>" + e(c.get('slug') or '') + "</small></div>"
                "</div></td>"
                "<td>" + _excel_input("companies", c['id'], "industries", c.get('industries') or 'Logistics', "Industry") + "</td>"
                "<td>" + _excel_input("companies", c['id'], "location", c.get('location') or '', "Headquarters") + "</td>"
                "<td style='width:120px;'>" + _excel_input("companies", c['id'], "employees", str(c.get('employees') or 0), "Employees", input_type="number") + "</td>"
                "<td><select class='excel-cell excel-select' style='min-width:105px;' onchange=\"saveInlineCell(this, 'companies', " + str(c['id']) + ", 'verified')\">"
                "<option value='1'" + (" selected" if c.get('verified', 1) else "") + ">&#10003; Verified</option>"
                "<option value='0'" + (" selected" if not c.get('verified', 1) else "") + ">Unverified</option>"
                "</select></td>"
                "<td><span class='pill-badge pill-green'>" + str(c.get('open_jobs') or 0) + " Openings</span></td>"
                "<td><div class='action-btns'>"
                "<button type='button' class='btn-action-round btn-action-edit' title='Manage Full Details (Wrench)' "
                "data-id='" + str(c.get('id') or '') + "' data-tab='companies' data-slug='" + e(c.get('slug') or '') + "' "
                "data-name='" + e(c.get('name') or '') + "' data-tagline='" + e(c.get('tagline') or '') + "' "
                "data-industries='" + e(c.get('industries') or '') + "' data-location='" + e(c.get('location') or '') + "' "
                "data-employees='" + str(c.get('employees') or 1000) + "' data-color='" + e(c.get('color') or '#2563eb') + "' "
                "data-website='" + e(c.get('website') or '') + "' data-description='" + e(c.get('description') or '') + "' "
                "data-logo-url='" + e(c.get('logo_url') or '') + "' data-banner-url='" + e(c.get('banner_url') or '') + "' "
                "data-benefits='" + e(c.get('benefits') or '') + "' data-offices='" + e(c.get('offices') or '') + "' "
                "data-social-links='" + e(c.get('social_links') or '') + "' data-status='" + e(c.get('status') or 'published') + "' "
                "data-verified='" + str(c.get('verified', 1)) + "' data-featured='" + str(c.get('featured') or 0) + "' "
                "onclick='openCompanyEditModal(this)'><i class='fa-solid fa-wrench'></i></button>"
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
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-building' style='color:#8b5cf6;margin-right:8px;'></i> Registered Companies (" + str(tab_total if tab_total is not None else counts['companies']) + ")</h3></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' style='background:#8b5cf6;' onclick=\"openCreateModal('create-company-modal')\"><i class='fa-solid fa-plus'></i> Register Company</button>"
            "<span id='excelSaveStatus' style='font-size:12px;font-weight:700;color:#10b981;display:none;'>Saved ✓</span>"
            "<button type='button' class='btn-ctrl btn-ctrl-light' onclick=\"exportAdminTableCSV(this, 'companies.csv')\" style='padding:6px 12px;font-size:12px;'><i class='fa-solid fa-file-excel' style='color:#10b981;'></i> Export Excel</button>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Team Size</th><th>Verified</th><th>Jobs</th><th>Action</th></tr></thead>"
            "<tbody>" + companies_rows + "</tbody>"
            "</table>" + _render_pagination("companies", page, tab_total if tab_total is not None else counts["companies"], per_page, q) + "</div>"
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
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-users' style='color:#3874ff;margin-right:8px;'></i> Registered Users (" + str(len(all_users)) + ")</h3>"
            "<span style='font-size:13px;color:#64748b;'>Change role via dropdown</span></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' onclick=\"openCreateModal('create-user-modal')\"><i class='fa-solid fa-user-plus'></i> Create User</button>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Name &amp; Email</th><th>Role</th><th>Joined</th><th>Action</th></tr></thead>"
            "<tbody>" + users_rows + "</tbody>"
            "</table></div>"
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
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-envelope' style='color:#10b981;margin-right:8px;'></i> All Subscribers (" + str(len(all_subscribers)) + ")</h3>"
            "<span style='font-size:13px;color:#64748b;'>Total newsletter signups from site footer</span></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<span class='pill-badge pill-green' style='font-size:13px;padding:6px 12px;'><i class='fa-solid fa-circle-check'></i> " + str(subscribers_count) + " Active</span>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Email Address</th><th>Subscribed On</th><th>Action</th></tr></thead>"
            "<tbody>" + subs_rows + "</tbody>"
            "</table></div>"
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
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-chart-bar' style='color:#10b981;margin-right:8px;'></i> Salary Benchmarks (" + str(len(all_salaries)) + ")</h3></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' style='background:#10b981;' onclick=\"openCreateModal('create-salary-modal')\"><i class='fa-solid fa-plus'></i> Add Salary Benchmark</button>"
            "<a href='/salaries' target='_blank' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;margin-left:8px;'>Live Salaries Page &rarr;</a>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Job Title</th><th>Category</th><th>Median</th><th>Range</th><th>Reports</th><th>Trend</th><th>Action</th></tr></thead>"
            "<tbody>" + salaries_rows + "</tbody>"
            "</table></div>"
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
                "<form method='post' action='/admin/courses/duplicate' style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(c['id']) + "'>"
                "<button type='submit' class='btn-action-round' title='Duplicate &amp; Edit'><i class='fa-regular fa-copy'></i></button>"
                "</form>"
                "<form method='post' action='/admin/courses/delete' onsubmit=\"return confirm('Delete this course?');\" style='display:inline;'>"
                f"{_csrf_field()}"
                "<input type='hidden' name='id' value='" + str(c['id']) + "'>"
                "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
                "</form></div></td></tr>"
            )
        courses_rows = "".join([course_row(c) for c in all_courses]) or _empty_row(7, "No courses found.")
        active_content = (
            "<div class='table-card' style='width:100%;'>"
            "<div class='table-header-bar'>"
            "<div><h3 class='table-title'><i class='fa-solid fa-graduation-cap' style='color:#3874ff;margin-right:8px;'></i> Live Courses (" + str(len(all_courses)) + ")</h3></div>"
            "<div style='display:flex;gap:8px;align-items:center;'>"
            "<button type='button' class='btn-add-new' onclick=\"openCreateModal('create-course-modal')\"><i class='fa-solid fa-plus'></i> Publish Course</button>"
            "<a href='/courses' target='_blank' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;margin-left:8px;'>Live Courses Page &rarr;</a>"
            "</div></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Thumb</th><th>Title</th><th>Track</th><th>Instructor</th><th>Duration</th><th>Status</th><th>Action</th></tr></thead>"
            "<tbody>" + courses_rows + "</tbody>"
            "</table></div>"
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

    elif tab == "inbox":
        pending_jobs = [dict(r) for r in conn.execute("SELECT id, title, company_name, location, posted_at FROM jobs WHERE status='pending' ORDER BY id DESC LIMIT 50").fetchall()]
        unverified_cos = [dict(r) for r in conn.execute("SELECT id, name, slug, location, industries FROM companies WHERE COALESCE(verified, 1)=0 ORDER BY id DESC LIMIT 50").fetchall()]
        p_job_rows = "".join(
            "<tr><td><strong>" + e(j['title']) + "</strong><br><small style='color:#64748b;'>" + e(j['company_name']) + " &middot; " + e(j['location']) + "</small></td>"
            "<td><span class='pill-badge pill-amber'>Pending Job</span></td>"
            "<td>" + e(j.get('posted_at') or '') + "</td>"
            "<td><div class='action-btns'>"
            "<form method='post' action='/admin/inbox/action' style='display:inline;'>"
            f"{_csrf_field()}<input type='hidden' name='kind' value='job'><input type='hidden' name='id' value='{j['id']}'>"
            "<button type='submit' name='decision' value='approve' class='btn-ctrl btn-ctrl-success' style='padding:5px 10px;font-size:12px;'>Approve</button> "
            "<button type='submit' name='decision' value='reject' class='btn-ctrl btn-ctrl-light' style='padding:5px 10px;font-size:12px;color:#ef4444;'>Reject</button>"
            "</form></div></td></tr>"
            for j in pending_jobs
        )
        p_co_rows = "".join(
            "<tr><td><strong>" + e(c['name']) + "</strong><br><small style='color:#64748b;'>" + e(c['industries']) + " &middot; " + e(c['location']) + "</small></td>"
            "<td><span class='pill-badge pill-blue'>Unverified Company</span></td>"
            "<td>&mdash;</td>"
            "<td><div class='action-btns'>"
            "<form method='post' action='/admin/inbox/action' style='display:inline;'>"
            f"{_csrf_field()}<input type='hidden' name='kind' value='company'><input type='hidden' name='id' value='{c['id']}'>"
            "<button type='submit' name='decision' value='approve' class='btn-ctrl btn-ctrl-success' style='padding:5px 10px;font-size:12px;'>Verify</button> "
            "<button type='submit' name='decision' value='reject' class='btn-ctrl btn-ctrl-light' style='padding:5px 10px;font-size:12px;'>Keep Unverified</button>"
            "</form></div></td></tr>"
            for c in unverified_cos
        )
        inbox_rows = (p_job_rows + p_co_rows) or _empty_row(4, "All caught up! No pending jobs or unverified companies.")
        active_content = (
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'><i class='fa-solid fa-inbox' style='color:#3874ff;margin-right:8px;'></i> Central Approval Inbox (" + str(len(pending_jobs) + len(unverified_cos)) + ")</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Item</th><th>Type</th><th>Date</th><th>Decision</th></tr></thead>"
            "<tbody>" + inbox_rows + "</tbody></table></div>"
        )

    elif tab == "logs":
        logs = db.list_audit_logs(conn, limit=100)
        log_rows = "".join(
            "<tr><td style='white-space:nowrap;color:#64748b;font-size:12px;'>" + e((l.get('created_at') or '')[:19].replace('T', ' ')) + "</td>"
            "<td><strong>" + e(l.get('actor_email') or 'system') + "</strong></td>"
            "<td><span class='pill-badge pill-blue'>" + e(l.get('action') or '') + "</span></td>"
            "<td><code>" + e(l.get('target_table') or '') + " #" + str(l.get('target_id') or 0) + "</code></td>"
            "<td style='color:#475569;font-size:12.5px;'>" + e(l.get('detail') or '') + "</td></tr>"
            for l in logs
        ) or _empty_row(5, "No audit events recorded yet. Edit any cell or approve an item to see live logs.")
        active_content = (
            "<div class='table-card'>"
            "<div class='table-header-bar'><h3 class='table-title'><i class='fa-solid fa-shield-halved' style='color:#10b981;margin-right:8px;'></i> Admin Audit Logs</h3></div>"
            "<table class='clean-table'>"
            "<thead><tr><th>Timestamp</th><th>Admin</th><th>Action</th><th>Target</th><th>Detail</th></tr></thead>"
            "<tbody>" + log_rows + "</tbody></table></div>"
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
            "<thead><tr><th>Role &amp; Company</th><th>Category &amp; Type</th><th>Location &amp; Salary</th><th style='width:140px;text-align:center;'>Action</th></tr></thead>"
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
        "<link rel='stylesheet' href='/static/cms-editor.css?v=20261128_cms'>\n"
        "<script src='https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.3/tinymce.min.js' referrerpolicy='origin'></script>\n"
        "<script src='/static/cms-editor.js?v=20261128_cms' defer></script>\n"
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
        "<li><a href='/admin?tab=inbox' class='" + nav_active('inbox') + "'><i class='fa-solid fa-inbox'></i> Approval Inbox</a></li>"
        "<li><a href='/admin?tab=logs' class='" + nav_active('logs') + "'><i class='fa-solid fa-shield-halved'></i> Audit Logs</a></li>"
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
        "<button type='button' class='btn-add-new' onclick=\"openSmartCreateModal()\"><i class='fa-solid fa-plus'></i> Add New</button>"
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
        (
            (
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

            ) if tab == "overview" else ""
        )
        + active_content +
        "\n" + render_create_modals(all_companies) +
        "\n" + render_edit_modals(all_companies) +
        "\n<style>"
        ".excel-cell{width:100%;border:1px solid transparent;background:transparent;padding:5px 7px;border-radius:6px;font-size:13px;color:#1e293b;font-family:inherit;transition:border-color .15s,background .15s;box-sizing:border-box;}"
        ".excel-cell:hover{border-color:#cbd5e1;background:#f8fafc;}"
        ".excel-cell:focus{outline:none;border-color:#3874ff;background:#ffffff;box-shadow:0 0 0 3px rgba(56,116,255,0.12);}"
        ".excel-cell.is-saved{border-color:#10b981;background:#ecfdf5;}"
        ".excel-select{cursor:pointer;min-width:110px;}"
        ".tox-tinymce{border-radius:10px !important;border:1px solid #cbd5e1 !important;box-shadow:0 1px 3px rgba(0,0,0,0.04) !important;}"
        ".tox-tinymce-aux, .tox-silver-sink{z-index:10005 !important;}"
        ".tox .tox-toolbar, .tox .tox-toolbar__overflow, .tox .tox-toolbar__primary{background:#f8fafc !important;border-bottom:1px solid #e2e8f0 !important;}"
        "</style>"
        "<script>"
        "function initRichEditors(){"
        "  if(typeof tinymce === 'undefined') return;"
        "  tinymce.init({"
        "    selector: '.rich-editor',"
        "    min_height: 380,"
        "    menubar: false,"
        "    plugins: 'image link lists table code media wordcount autolink',"
        "    toolbar: 'undo redo | blocks | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | image link table | removeformat code',"
        "    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif; font-size: 15px; color: #1e293b; line-height: 1.65; padding: 12px; } img { max-width: 100%; height: auto; border-radius: 8px; cursor: pointer; } mark, span[style*=\"background-color\"] { border-radius: 3px; padding: 1px 4px; }',"
        "    image_advtab: true,"
        "    image_caption: true,"
        "    image_dimensions: true,"
        "    paste_data_images: true,"
        "    automatic_uploads: true,"
        "    images_upload_handler: function(blobInfo, progress){"
        "      return new Promise(function(resolve, reject){"
        "        var reader = new FileReader();"
        "        reader.onload = function(e){"
        "          var img = new Image();"
        "          img.onload = function(){"
        "            var maxW = 1200, maxH = 900;"
        "            var w = img.width, h = img.height;"
        "            if(w > maxW || h > maxH){"
        "              if(w / maxW > h / maxH){ h = Math.round(h * (maxW / w)); w = maxW; }"
        "              else { w = Math.round(w * (maxH / h)); h = maxH; }"
        "            }"
        "            var canvas = document.createElement('canvas');"
        "            canvas.width = w; canvas.height = h;"
        "            var ctx = canvas.getContext('2d');"
        "            ctx.drawImage(img, 0, 0, w, h);"
        "            resolve(canvas.toDataURL('image/jpeg', 0.86));"
        "          };"
        "          img.onerror = function(){ resolve(e.target.result); };"
        "          img.src = e.target.result;"
        "        };"
        "        reader.onerror = function(err){ reject('Upload error: ' + err); };"
        "        reader.readAsDataURL(blobInfo.blob());"
        "      });"
        "    },"
        "    setup: function(editor){"
        "      editor.on('change keyup', function(){ editor.save(); });"
        "    }"
        "  });"
        "}"
        "if(document.readyState === 'loading'){"
        "  document.addEventListener('DOMContentLoaded', initRichEditors);"
        "} else {"
        "  initRichEditors();"
        "}"
        "document.querySelectorAll('form').forEach(function(f){"
        "  f.addEventListener('submit', function(){ if(window.tinymce) tinymce.triggerSave(); });"
        "});"
        "async function saveInlineCell(el, table, id, field){"
        "  var val = el.value;"
        "  var csrfEl = document.querySelector('input[name=_csrf]');"
        "  var csrf = csrfEl ? csrfEl.value : '';"
        "  try{"
        "    var res = await fetch('/admin/api/inline-update', {"
        "      method:'POST',"
        "      headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},"
        "      body:JSON.stringify({table:table,id:id,field:field,value:val,_csrf:csrf})"
        "    });"
        "    var data = await res.json();"
        "    if(data && data.ok){"
        "      el.classList.add('is-saved');"
        "      var st = document.getElementById('excelSaveStatus');"
        "      if(st){ st.style.display='inline'; clearTimeout(window._exTimer); window._exTimer=setTimeout(function(){st.style.display='none';},1800); }"
        "      setTimeout(function(){el.classList.remove('is-saved');},1200);"
        "    } else { alert((data && data.error) || 'Could not save cell'); }"
        "  } catch(err){ alert('Save failed: ' + err); }"
        "}"
        "function exportAdminTableCSV(btn, filename){"
        "  var card = btn.closest('.table-card');"
        "  var table = card ? card.querySelector('table') : null;"
        "  if(!table) return;"
        "  var csv = [];"
        "  table.querySelectorAll('tr').forEach(function(tr){"
        "    var row = [];"
        "    var cells = tr.querySelectorAll('th, td');"
        "    for(var i=0; i<cells.length-1; i++){"
        "      var inp = cells[i].querySelector('input, select');"
        "      var txt = inp ? inp.value : cells[i].innerText;"
        "      txt = String(txt || '').replace(/\\s+/g,' ').trim().replace(/\"/g,'\"\"');"
        "      row.push('\"' + txt + '\"');"
        "    }"
        "    if(row.length) csv.push(row.join(','));"
        "  });"
        "  var blob = new Blob(['\\uFEFF' + csv.join('\\n')], {type:'text/csv;charset=utf-8;'});"
        "  var a = document.createElement('a');"
        "  a.href = URL.createObjectURL(blob);"
        "  a.download = filename || 'export.csv';"
        "  a.click();"
        "}"
        "</script>"
        "\n</div></main></div></body></html>"
    )
