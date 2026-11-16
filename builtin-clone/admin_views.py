import html
import re
from datetime import datetime
import db

def e(value):
    return html.escape(str(value if value is not None else ""), quote=True)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")

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

def render_admin_dashboard(conn, user, message="", error="", tab="overview"):
    counts = db.counts(conn)
    today_videos_count = conn.execute(
        "SELECT COUNT(*) FROM articles WHERE tag='Logistic Waves Today' OR is_today=1"
    ).fetchone()[0]
    applications_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    subscribers_count  = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    users_count        = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    today_videos = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, author, guest, duration, thumb, published, category "
        "FROM articles WHERE tag='Logistic Waves Today' OR is_today=1 ORDER BY id DESC"
    ).fetchall()]

    all_articles = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, category, tag, author, published, is_today "
        "FROM articles ORDER BY id DESC LIMIT 200"
    ).fetchall()]

    all_jobs = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, company_name, category, workplace, location, salary_display, posted_at "
        "FROM jobs ORDER BY id DESC LIMIT 200"
    ).fetchall()]

    all_companies = [dict(r) for r in conn.execute(
        "SELECT id, slug, name, initials, color, industries, location, employees, open_jobs "
        "FROM companies ORDER BY name ASC"
    ).fetchall()]

    all_users = [dict(r) for r in conn.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY id DESC"
    ).fetchall()]

    all_applications = []
    try:
        all_applications = [dict(r) for r in conn.execute(
            "SELECT a.id, a.status, a.note, a.created_at,"
            " j.title as job_title, j.id as job_id, j.slug as job_slug,"
            " u.name as user_name, u.email as user_email"
            " FROM applications a"
            " JOIN jobs j ON a.job_id=j.id"
            " JOIN users u ON a.user_id=u.id"
            " ORDER BY a.id DESC LIMIT 200"
        ).fetchall()]
    except Exception:
        pass

    all_subscribers = [dict(r) for r in conn.execute(
        "SELECT id, email, created_at FROM subscribers ORDER BY id DESC"
    ).fetchall()]

    all_salaries = [dict(r) for r in conn.execute(
        "SELECT id, title, category, median, low, high, samples, trend "
        "FROM salaries ORDER BY id DESC"
    ).fetchall()]

    # Alert banner
    alert_html = ""
    if message:
        alert_html = '<div class="admin-alert admin-alert-success"><i class="fa-solid fa-circle-check"></i> ' + e(message) + '</div>'
    elif error:
        alert_html = '<div class="admin-alert admin-alert-error"><i class="fa-solid fa-triangle-exclamation"></i> ' + e(error) + '</div>'

    def nav_active(t):
        return "sidebar-link active" if tab == t else "sidebar-link"

    # ======================= OVERVIEW =======================
    def overview_video_row(v):
        thumb = e(v['thumb'] or '/static/images/fw_today_1.jpg')
        return (
            "<tr>"
            "<td style='width:72px;'><img src='" + thumb + "' class='table-thumb' alt='thumb'></td>"
            "<td style='min-width:220px;'><strong>" + e(v['title']) + "</strong><br>"
            "<small style='color:#64748b;'>Guest: " + e(v['guest'] or 'N/A') + "</small></td>"
            "<td><span class='pill-badge pill-blue'>" + e(v['category'] or 'Video') + "</span></td>"
            "<td style='white-space:nowrap;'>" + e(v['duration'] or '15 min') + "</td>"
            "<td style='white-space:nowrap;color:#64748b;'>" + e(v['published']) + "</td>"
            "<td style='width:90px;text-align:center;'>"
            "<div class='action-btns' style='justify-content:center;'>"
            "<a href='/articles/" + e(v['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete this video?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(v['id']) + "'>"
            "<input type='hidden' name='tab' value='overview'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    def overview_job_row(j):
        return (
            "<tr>"
            "<td style='min-width:220px;'><strong>" + e(j['title']) + "</strong><br>"
            "<small style='color:#64748b;'>" + e(j['company_name']) + "</small></td>"
            "<td><span class='pill-badge pill-blue'>" + e(j['category']) + "</span></td>"
            "<td><span class='pill-badge pill-amber'>" + e(j['workplace']) + "</span></td>"
            "<td style='color:#475569;'>" + e(j['location']) + "</td>"
            "<td style='font-weight:700;color:#0f172a;'>" + e(j['salary_display'] or 'Competitive') + "</td>"
            "<td style='width:90px;text-align:center;'>"
            "<div class='action-btns' style='justify-content:center;'>"
            "<a href='/job/" + e(j['slug']) + "/" + str(j['id']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/jobs/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(j['id']) + "'>"
            "<input type='hidden' name='tab' value='overview'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    recent_videos_rows = "".join([overview_video_row(v) for v in today_videos[:5]]) or \
        "<tr><td colspan='6' style='text-align:center;padding:24px;color:#94a3b8;'>No videos yet. Click \"Seed Today Videos\" above.</td></tr>"

    recent_jobs_rows = "".join([overview_job_row(j) for j in all_jobs[:5]]) or \
        "<tr><td colspan='6' style='text-align:center;padding:24px;color:#94a3b8;'>No jobs found.</td></tr>"

    overview_content = (
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
        "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#3874ff;'></span> Editorial Articles</span><strong>54%</strong></div>"
        "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#34d399;'></span> Active Jobs</span><strong>30%</strong></div>"
        "<div class='donut-legend-item'><span><span class='legend-dot' style='background:#f87171;'></span> Today Broadcasts</span><strong>16%</strong></div>"
        "</div></div></div></div>"
        "<div class='table-card'>"
        "<div class='table-header-bar'>"
        "<h3 class='table-title'><i class='fa-solid fa-video' style='color:#3874ff;margin-right:8px;'></i> Live Today Broadcast Episodes</h3>"
        "<a href='/admin?tab=videos' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>View All (" + str(len(today_videos)) + ") &rarr;</a>"
        "</div>"
        "<table class='clean-table'>"
        "<thead><tr><th style='width:72px;'>Thumb</th><th>Title &amp; Guest</th><th>Category</th><th>Duration</th><th>Published</th><th style='width:90px;text-align:center;'>Action</th></tr></thead>"
        "<tbody>" + recent_videos_rows + "</tbody>"
        "</table></div>"
        "<div class='table-card'>"
        "<div class='table-header-bar'>"
        "<h3 class='table-title'><i class='fa-solid fa-briefcase' style='color:#10b981;margin-right:8px;'></i> Active Job Listings</h3>"
        "<a href='/admin?tab=jobs' style='color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;'>View All (" + str(len(all_jobs)) + ") &rarr;</a>"
        "</div>"
        "<table class='clean-table'>"
        "<thead><tr><th>Role &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th style='width:90px;text-align:center;'>Action</th></tr></thead>"
        "<tbody>" + recent_jobs_rows + "</tbody>"
        "</table></div>"
    )

    # ======================= VIDEOS TAB =======================
    def video_row(v):
        thumb = e(v['thumb'] or '/static/images/fw_today_1.jpg')
        return (
            "<tr>"
            "<td><img src='" + thumb + "' class='table-thumb' alt='thumb'></td>"
            "<td><strong>" + e(v['title']) + "</strong><br><small style='color:#64748b;'>/" + e(v['slug']) + "</small></td>"
            "<td><strong style='color:#3874ff;'>" + e(v['guest'] or '—') + "</strong></td>"
            "<td><span class='pill-badge pill-blue'>" + e(v['category'] or 'Maritime') + "</span></td>"
            "<td>" + e(v['duration'] or '15:00 min') + "</td>"
            "<td style='color:#64748b;'>" + e(v['published']) + "</td>"
            "<td><div class='action-btns'>"
            "<a href='/articles/" + e(v['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(v['id']) + "'>"
            "<input type='hidden' name='tab' value='videos'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    video_rows = "".join([video_row(v) for v in today_videos]) or \
        "<tr><td colspan='7' style='text-align:center;padding:32px;color:#94a3b8;'>No Today episodes yet. Click \"Seed Today Videos\" above.</td></tr>"

    videos_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-circle-plus' style='color:#3874ff;'></i> Add New Today Video</h3>"
        "<form method='post' action='/admin/videos/create'>"
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
        "<div class='form-group'><label class='form-label'>Thumbnail Preset</label>"
        "<select class='form-control' name='thumb_preset' onchange=\"if(this.value)document.getElementById('vtinput').value=this.value;\">"
        "<option value='/static/images/fw_today_1.jpg'>Preset 1: Rocket Logistics &amp; Port</option>"
        "<option value='/static/images/fw_today_2.svg'>Preset 2: Electric Aviation</option>"
        "<option value='/static/images/fw_today_3.jpg'>Preset 3: Space Coast Port</option>"
        "<option value='/static/images/fw_today_4.jpg'>Preset 4: Electric Flying Boat</option>"
        "<option value='/static/images/fw_today_5.jpg'>Preset 5: Container Spot Rates</option>"
        "<option value='/static/images/fw_today_6.jpg'>Preset 6: Green Ammonia</option>"
        "</select></div>"
        "<div class='form-group'><label class='form-label'>Custom Image URL</label><input class='form-control' id='vtinput' name='thumb' value='/static/images/fw_today_1.jpg'></div>"
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

    # ======================= ARTICLES TAB =======================
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
            "<a href='/articles/" + e(a['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/articles/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
            "<input type='hidden' name='tab' value='articles'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    articles_rows = "".join([article_row(a) for a in all_articles]) or \
        "<tr><td colspan='6' style='text-align:center;padding:32px;color:#94a3b8;'>No articles found.</td></tr>"

    articles_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-pen-nib' style='color:#3874ff;'></i> Publish New Article</h3>"
        "<form method='post' action='/admin/articles/create'>"
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
        "<div class='form-group'><label class='form-label'>Excerpt / Summary</label><textarea class='form-control' name='excerpt' rows='2' placeholder='Brief summary...'></textarea></div>"
        "<div class='form-group'><label class='form-label'>Article Content *</label><textarea class='form-control' name='body' rows='4' placeholder='Full article body...' required></textarea></div>"
        "<button type='submit' class='btn-submit-clean'><i class='fa-solid fa-upload'></i> Publish Article</button>"
        "</form></div>"
        "<div class='table-card'>"
        "<div class='table-header-bar'><h3 class='table-title'>All Articles &amp; Reports (" + str(len(all_articles)) + ")</h3></div>"
        "<table class='clean-table'>"
        "<thead><tr><th>Title &amp; Slug</th><th>Category</th><th>Tag</th><th>Author</th><th>Date</th><th>Action</th></tr></thead>"
        "<tbody>" + articles_rows + "</tbody>"
        "</table></div></div>"
    )

    # ======================= JOBS TAB =======================
    company_options = "".join([
        "<option value='" + e(c["slug"]) + "'>" + e(c["name"]) + "</option>"
        for c in all_companies
    ])

    def job_row(j):
        return (
            "<tr>"
            "<td><strong>" + e(j['title']) + "</strong><br><small style='color:#64748b;'>" + e(j['company_name']) + "</small></td>"
            "<td>" + e(j['category']) + "</td>"
            "<td><span class='pill-badge pill-blue'>" + e(j['workplace']) + "</span></td>"
            "<td>" + e(j['location']) + "</td>"
            "<td style='font-weight:700;'>" + e(j['salary_display'] or 'Competitive') + "</td>"
            "<td style='color:#64748b;'>" + e(j['posted_at']) + "</td>"
            "<td><div class='action-btns'>"
            "<a href='/job/" + e(j['slug']) + "/" + str(j['id']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/jobs/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(j['id']) + "'>"
            "<input type='hidden' name='tab' value='jobs'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    jobs_rows = "".join([job_row(j) for j in all_jobs]) or \
        "<tr><td colspan='7' style='text-align:center;padding:32px;color:#94a3b8;'>No jobs found.</td></tr>"

    jobs_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-briefcase' style='color:#10b981;'></i> Post New Job</h3>"
        "<form method='post' action='/admin/jobs/create'>"
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
        "<div class='table-header-bar'><h3 class='table-title'>Active Job Listings (" + str(len(all_jobs)) + ")</h3></div>"
        "<table class='clean-table'>"
        "<thead><tr><th>Title &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th>Posted</th><th>Action</th></tr></thead>"
        "<tbody>" + jobs_rows + "</tbody>"
        "</table></div></div>"
    )

    # ======================= COMPANIES TAB =======================
    def company_row(c):
        clr = e(c['color'] or '#3874ff')
        return (
            "<tr>"
            "<td><div style='display:flex;align-items:center;gap:12px;'>"
            "<span style='display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:10px;background:" + clr + ";color:#fff;font-weight:800;font-size:13px;'>" + e(c['initials']) + "</span>"
            "<div><strong>" + e(c['name']) + "</strong><br><small style='color:#64748b;'>" + e(c['slug']) + "</small></div>"
            "</div></td>"
            "<td><span class='pill-badge pill-blue'>" + e(c['industries'] or 'Logistics') + "</span></td>"
            "<td>" + e(c['location']) + "</td>"
            "<td>" + format(c['employees'], ',') + " employees</td>"
            "<td><span class='pill-badge pill-green'>" + str(c['open_jobs']) + " Openings</span></td>"
            "<td><div class='action-btns'>"
            "<a href='/company/" + e(c['slug']) + "' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/companies/delete' onsubmit=\"return confirm('Delete company and all jobs?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(c['id']) + "'>"
            "<input type='hidden' name='tab' value='companies'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    companies_rows = "".join([company_row(c) for c in all_companies]) or \
        "<tr><td colspan='6' style='text-align:center;padding:32px;color:#94a3b8;'>No companies found.</td></tr>"

    companies_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-building' style='color:#8b5cf6;'></i> Register Company</h3>"
        "<form method='post' action='/admin/companies/create'>"
        "<input type='hidden' name='tab' value='companies'>"
        "<div class='form-group'><label class='form-label'>Company Name *</label><input class='form-control' name='name' placeholder='e.g. Saigon Port Authority' required></div>"
        "<div class='form-group'><label class='form-label'>Tagline</label><input class='form-control' name='tagline' placeholder='e.g. Modern Deepwater Port &amp; Logistics Hub'></div>"
        "<div class='form-group'><label class='form-label'>Industries</label><input class='form-control' name='industries' value='Logistics &amp; Maritime Shipping'></div>"
        "<div class='form-group'><label class='form-label'>Headquarters</label><input class='form-control' name='location' value='Ho Chi Minh City, Vietnam'></div>"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>"
        "<div class='form-group'><label class='form-label'>Employees</label><input type='number' class='form-control' name='employees' value='1500'></div>"
        "<div class='form-group'><label class='form-label'>Brand Color</label><input class='form-control' name='color' value='#034f9a'></div>"
        "</div>"
        "<div class='form-group'><label class='form-label'>Website</label><input class='form-control' name='website' value='https://example.com'></div>"
        "<div class='form-group'><label class='form-label'>Description</label><textarea class='form-control' name='description' rows='3' placeholder='Overview...'></textarea></div>"
        "<button type='submit' class='btn-submit-clean' style='background:#8b5cf6;'><i class='fa-solid fa-plus'></i> Register Company</button>"
        "</form></div>"
        "<div class='table-card'>"
        "<div class='table-header-bar'><h3 class='table-title'>Registered Companies (" + str(len(all_companies)) + ")</h3></div>"
        "<table class='clean-table'>"
        "<thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Team Size</th><th>Jobs</th><th>Action</th></tr></thead>"
        "<tbody>" + companies_rows + "</tbody>"
        "</table></div></div>"
    )

    # ======================= USERS TAB =======================
    def user_row(u):
        initial = e((u['name'] or 'U')[0].upper())
        role_opts = ""
        for rv in ["candidate", "employer", "admin"]:
            sel = " selected" if u["role"] == rv else ""
            label = rv.capitalize()
            role_opts += "<option value='" + rv + "'" + sel + ">" + label + "</option>"
        return (
            "<tr>"
            "<td><div style='display:flex;align-items:center;gap:10px;'>"
            "<div style='width:34px;height:34px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0;'>" + initial + "</div>"
            "<div><strong>" + e(u['name']) + "</strong><br><small style='color:#64748b;'>" + e(u['email']) + "</small></div>"
            "</div></td>"
            "<td><form method='post' action='/admin/users/role' style='display:inline-flex;align-items:center;gap:6px;'>"
            "<input type='hidden' name='id' value='" + str(u['id']) + "'>"
            "<select name='role' class='form-control' style='padding:4px 8px;font-size:12px;min-width:110px;' onchange='this.form.submit()'>"
            + role_opts +
            "</select></form></td>"
            "<td style='color:#64748b;font-size:13px;'>" + e((u['created_at'] or '—')[:10]) + "</td>"
            "<td><div class='action-btns'>"
            "<form method='post' action='/admin/users/delete' onsubmit=\"return confirm('Permanently delete this user?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(u['id']) + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    users_rows = "".join([user_row(u) for u in all_users]) or \
        "<tr><td colspan='4' style='text-align:center;padding:32px;color:#94a3b8;'>No users found.</td></tr>"

    users_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-user-plus' style='color:#3874ff;'></i> Create Demo User</h3>"
        "<form method='post' action='/admin/users/create'>"
        "<input type='hidden' name='tab' value='users'>"
        "<div class='form-group'><label class='form-label'>Full Name *</label><input class='form-control' name='name' placeholder='e.g. Nguyen Van A' required></div>"
        "<div class='form-group'><label class='form-label'>Email *</label><input class='form-control' type='email' name='email' placeholder='e.g. user@example.com' required></div>"
        "<div class='form-group'><label class='form-label'>Password</label><input class='form-control' type='password' name='password' placeholder='Set a password' required></div>"
        "<div class='form-group'><label class='form-label'>Role</label>"
        "<select class='form-control' name='role'>"
        "<option value='candidate'>Candidate (Job Seeker)</option>"
        "<option value='employer'>Employer (Company)</option>"
        "<option value='admin'>Admin</option>"
        "</select></div>"
        "<div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px;margin-bottom:12px;font-size:13px;color:#1d4ed8;'>"
        "<i class='fa-solid fa-circle-info'></i> <strong>Demo accounts:</strong><br>"
        "candidate@demo.com / demo1234<br>employer@demo.com / demo1234"
        "</div>"
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

    # ======================= APPLICATIONS TAB =======================
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
            "<input type='hidden' name='id' value='" + str(a['id']) + "'>"
            + status_btns +
            "</form></div></details>"
            "<form method='post' action='/admin/applications/delete' onsubmit=\"return confirm('Delete?');\" style='display:inline;'>"
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
    ]) or "<span style='color:#94a3b8;font-size:13px;'>No applications yet</span>"

    applications_rows = "".join([app_row(a) for a in all_applications]) or \
        "<tr><td colspan='6' style='text-align:center;padding:32px;color:#94a3b8;'>No applications yet. Users apply from individual job pages.</td></tr>"

    applications_content = (
        "<div class='table-card'>"
        "<div class='table-header-bar'>"
        "<h3 class='table-title'><i class='fa-solid fa-file-signature' style='color:#8b5cf6;margin-right:8px;'></i> Job Applications (" + str(len(all_applications)) + ")</h3>"
        "<div>" + status_summary + "</div>"
        "</div>"
        "<div style='padding:0 24px 12px;'><p style='font-size:13px;color:#64748b;margin:0;'>"
        "Applications submitted by candidates. Click <i class='fa-solid fa-pen-to-square'></i> to update status."
        "</p></div>"
        "<table class='clean-table'>"
        "<thead><tr><th>Applicant</th><th>Job Position</th><th>Status</th><th>Notes</th><th>Applied</th><th>Action</th></tr></thead>"
        "<tbody>" + applications_rows + "</tbody>"
        "</table></div>"
    )

    # ======================= SUBSCRIBERS TAB =======================
    def sub_row(s):
        return (
            "<tr>"
            "<td style='font-weight:600;'>" + e(s['email']) + "</td>"
            "<td style='color:#64748b;font-size:13px;'>" + e((s['created_at'] or '')[:10]) + "</td>"
            "<td><div class='action-btns'>"
            "<form method='post' action='/admin/subscribers/delete' onsubmit=\"return confirm('Remove subscriber?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(s['id']) + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    subs_rows = "".join([sub_row(s) for s in all_subscribers]) or \
        "<tr><td colspan='3' style='text-align:center;padding:32px;color:#94a3b8;'>No subscribers yet. Newsletter signups appear here automatically.</td></tr>"

    subscribers_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-envelope' style='color:#3874ff;'></i> Newsletter Info</h3>"
        "<div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:20px;margin-bottom:16px;text-align:center;'>"
        "<div style='font-size:40px;font-weight:800;color:#1d4ed8;'>" + str(len(all_subscribers)) + "</div>"
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
        "<div>&#10003; Total subscribers: <strong>" + str(len(all_subscribers)) + "</strong></div>"
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

    # ======================= SALARIES TAB =======================
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
            "<a href='/salaries' target='_blank' class='btn-action-round'><i class='fa-solid fa-arrow-up-right-from-square'></i></a>"
            "<form method='post' action='/admin/salaries/delete' onsubmit=\"return confirm('Delete salary entry?');\" style='display:inline;'>"
            "<input type='hidden' name='id' value='" + str(s['id']) + "'>"
            "<button type='submit' class='btn-action-delete'><i class='fa-solid fa-trash-can'></i></button>"
            "</form></div></td></tr>"
        )

    salaries_rows = "".join([salary_row(s) for s in all_salaries]) or \
        "<tr><td colspan='7' style='text-align:center;padding:32px;color:#94a3b8;'>No salary data found.</td></tr>"

    salaries_content = (
        "<div class='form-panel-grid'>"
        "<div class='clean-card-form'>"
        "<h3 class='form-title'><i class='fa-solid fa-chart-bar' style='color:#10b981;'></i> Add Salary Benchmark</h3>"
        "<form method='post' action='/admin/salaries/create'>"
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

    # ======================= ASSEMBLE =======================
    tab_bodies = {
        "overview":     overview_content,
        "videos":       videos_content,
        "articles":     articles_content,
        "jobs":         jobs_content,
        "companies":    companies_content,
        "users":        users_content,
        "applications": applications_content,
        "subscribers":  subscribers_content,
        "salaries":     salaries_content,
    }
    active_content = tab_bodies.get(tab, overview_content)

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
        "<aside class='admin-sidebar'>\n"
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
        "</ul>\n"
        "<div class='sidebar-footer'><a href='/' target='_blank'><i class='fa-solid fa-arrow-right-from-bracket'></i> Live Website</a></div>"
        "</aside>\n"

        # --- Main ---
        "<main class='admin-main'>\n"
        "<header class='admin-topbar'>"
        "<div class='topbar-left'>"
        "<a href='/admin?tab=videos' class='btn-add-new'><i class='fa-solid fa-plus'></i> Add New</a>"
        "<div class='search-box'><i class='fa-solid fa-magnifying-glass'></i>"
        "<input type='text' class='search-input' placeholder='Search...' aria-label='Search'></div>"
        "</div>"
        "<div class='topbar-right'>"
        "<div class='topbar-user'>"
        "<div style='width:36px;height:36px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;'>" + e(admin_initial) + "</div>"
        "<div class='topbar-user-info'>"
        "<span class='topbar-user-name'>" + e(admin_name) + "</span>"
        "<span class='topbar-user-role'>Admin</span>"
        "</div>"
        "<i class='fa-solid fa-chevron-down' style='font-size:11px;color:#94a3b8;'></i>"
        "</div>"
        "<a href='#' class='topbar-icon-btn' title='Notifications'><i class='fa-regular fa-bell'></i><span class='notification-dot'></span></a>"
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
        "<input type='hidden' name='tab' value='" + e(tab) + "'>"
        "<button type='submit' name='action' value='seed_videos' class='btn-ctrl btn-ctrl-primary'><i class='fa-solid fa-play'></i> Seed Today Videos (6)</button>"
        "<button type='submit' name='action' value='seed_logistics' class='btn-ctrl btn-ctrl-success'><i class='fa-solid fa-truck-fast'></i> Seed Logistics &amp; Jobs</button>"
        "<button type='submit' name='action' value='reseed_all' class='btn-ctrl btn-ctrl-purple'><i class='fa-solid fa-database'></i> Reseed Full System</button>"
        "<button type='submit' name='action' value='clear_videos' class='btn-ctrl btn-ctrl-light' onclick=\"return confirm('Reset all Today videos?');\"><i class='fa-solid fa-trash-can'></i> Reset Videos</button>"
        "</form></div>\n"

        # Stat cards
        "<div class='stat-cards-grid'>"
        "<div class='stat-card'><div class='stat-card-left'>"
        + circular_gauge_svg(pct_videos, "#3874ff") +
        "<div class='stat-card-info'><h4>Today<br>Videos</h4><div class='stat-number'>" + str(today_videos_count) + "</div>"
        "<div class='stat-card-trend trend-up'>Live " + mini_wave_svg("#3874ff") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card'><div class='stat-card-left'>"
        + circular_gauge_svg(pct_arts, "#10b981") +
        "<div class='stat-card-info'><h4>Editorial<br>Articles</h4><div class='stat-number'>" + str(counts['articles']) + "</div>"
        "<div class='stat-card-trend trend-up'>16% &uarr; " + mini_wave_svg("#10b981") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card'><div class='stat-card-left'>"
        + circular_gauge_svg(pct_jobs, "#06b6d4") +
        "<div class='stat-card-info'><h4>Active<br>Jobs</h4><div class='stat-number'>" + str(counts['jobs']) + "</div>"
        "<div class='stat-card-trend trend-up'>12% &uarr; " + mini_wave_svg("#06b6d4") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"

        "<div class='stat-card'><div class='stat-card-left'>"
        + circular_gauge_svg(pct_users, "#8b5cf6") +
        "<div class='stat-card-info'><h4>Users &amp;<br>Members</h4><div class='stat-number'>" + str(users_count) + "</div>"
        "<div class='stat-card-trend trend-up'>" + str(applications_count) + " apps " + mini_wave_svg("#8b5cf6") + "</div>"
        "</div></div><i class='fa-solid fa-ellipsis stat-card-menu'></i></div>"
        "</div>\n"

        + active_content +
        "\n</div></main></div></body></html>"
    )
