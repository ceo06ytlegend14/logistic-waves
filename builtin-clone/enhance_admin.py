"""
Comprehensive Admin Enhancement Script
- Adds Users, Applications, Subscribers, Salary tabs to admin
- Seeds demo applications and subscribers for testing
- Updates app.py with new POST routes
- Fixes Font Awesome fallback in layout
Run once: python enhance_admin.py
"""
import sys, os, re

def run():
    base = os.path.dirname(os.path.abspath(__file__))

    # 1. Seed demo data
    print("[1] Seeding demo applications & subscribers...")
    import sqlite3
    conn = sqlite3.connect(os.path.join(base, 'data', 'site.db'))
    conn.row_factory = sqlite3.Row

    # Seed applications
    app_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    if app_count == 0:
        jobs = conn.execute("SELECT id, title FROM jobs LIMIT 10").fetchall()
        users = conn.execute("SELECT id, name FROM users").fetchall()
        statuses = ['Applied', 'Reviewing', 'Interview', 'Offer', 'Rejected']
        notes = [
            'Strong candidate with relevant port operations background.',
            'Reviewing CV and cover letter.',
            'Scheduled for technical panel interview.',
            'Offer extended pending background check.',
            'Position filled internally.',
            'Application under consideration.',
            'Requested additional portfolio samples.',
            'Awaiting manager approval.',
        ]
        import random
        random.seed(42)
        inserted = 0
        for job in jobs:
            for user in users:
                status = random.choice(statuses)
                note = random.choice(notes)
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO applications (user_id, job_id, status, note, created_at) VALUES (?,?,?,?,datetime('now','-' || ? || ' days'))",
                        (user['id'], job['id'], status, note, str(random.randint(1, 30)))
                    )
                    inserted += 1
                except Exception:
                    pass
        conn.commit()
        print(f"   Seeded {inserted} demo applications")
    else:
        print(f"   Applications already exist: {app_count}")

    # Seed subscribers
    sub_count = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    if sub_count == 0:
        demo_emails = [
            'nguyen.logistics@gmail.com', 'tran.supply@outlook.com',
            'le.maritime@yahoo.com', 'pham.freight@gmail.com',
            'hoang.port@company.vn', 'minh.shipping@gmail.com',
            'linh.cargo@outlook.com', 'duc.customs@gmail.com',
            'thu.supply@company.vn', 'hung.terminal@gmail.com',
            'mai.logistics@yahoo.com', 'bao.maritime@outlook.com',
        ]
        for em in demo_emails:
            try:
                conn.execute("INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, datetime('now','-' || ? || ' days'))",
                             (em, str(demo_emails.index(em) * 2 + 1)))
            except Exception:
                pass
        conn.commit()
        print(f"   Seeded {len(demo_emails)} demo subscribers")
    else:
        print(f"   Subscribers already exist: {sub_count}")

    conn.close()

    # 2. Write new admin_views.py
    print("[2] Writing enhanced admin_views.py...")
    admin_views_path = os.path.join(base, 'admin_views.py')
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(ADMIN_VIEWS_CONTENT)
    print(f"   Written: {os.path.getsize(admin_views_path):,} bytes")

    # 3. Patch app.py — add new routes
    print("[3] Patching app.py with new routes...")
    app_path = os.path.join(base, 'app.py')
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()

    # Add new POST_PAGE_PATHS entries if not already present
    new_paths = [
        '"/admin/users/delete"', '"/admin/users/create"', '"/admin/users/role"',
        '"/admin/applications/delete"', '"/admin/applications/status"',
        '"/admin/subscribers/delete"',
        '"/admin/salaries/create"', '"/admin/salaries/delete"',
    ]

    for p in new_paths:
        if p not in app_content:
            # Find POST_PAGE_PATHS set and add to it
            app_content = app_content.replace(
                '"/admin/companies/delete",',
                '"/admin/companies/delete",\n    ' + p + ','
            )

    # Add new route handlers before "# --- home ---" marker
    if '/admin/users/delete' not in app_content:
        new_routes = '''
    if path == "/admin/users/create" and method == "POST":
        name = payload.get("name", "").strip()
        email = payload.get("email", "").strip().lower()
        password = payload.get("password", "demo1234").strip() or "demo1234"
        role = payload.get("role", "candidate").strip()
        if name and email:
            try:
                db.create_user(conn, {"name": name, "email": email, "password": password, "role": role})
                conn.commit()
                return redirect("/admin?tab=users&msg=" + urllib.parse.quote(f"User '{name}' created successfully!"))
            except Exception as ex:
                return redirect("/admin?tab=users&err=" + urllib.parse.quote(f"Error: {ex}"))
        return redirect("/admin?tab=users&err=" + urllib.parse.quote("Name and email are required."))

    if path == "/admin/users/delete" and method == "POST":
        uid = get_int(payload.get("id", "0"), 0)
        conn.execute("DELETE FROM sessions WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM saved_jobs WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM follows WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM applications WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM alerts WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
        return redirect("/admin?tab=users&msg=" + urllib.parse.quote("User account deleted."))

    if path == "/admin/users/role" and method == "POST":
        uid = get_int(payload.get("id", "0"), 0)
        new_role = payload.get("role", "candidate").strip()
        if new_role in ("candidate", "employer", "admin"):
            conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
            conn.commit()
        return redirect("/admin?tab=users&msg=" + urllib.parse.quote("User role updated."))

    if path == "/admin/applications/delete" and method == "POST":
        aid = get_int(payload.get("id", "0"), 0)
        conn.execute("DELETE FROM applications WHERE id=?", (aid,))
        conn.commit()
        return redirect("/admin?tab=applications&msg=" + urllib.parse.quote("Application deleted."))

    if path == "/admin/applications/status" and method == "POST":
        aid = get_int(payload.get("id", "0"), 0)
        status = payload.get("status", "Reviewing").strip()
        note = payload.get("note", "").strip()
        conn.execute("UPDATE applications SET status=?, note=? WHERE id=?", (status, note, aid))
        conn.commit()
        return redirect("/admin?tab=applications&msg=" + urllib.parse.quote(f"Application status updated to {status}."))

    if path == "/admin/subscribers/delete" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0)
        conn.execute("DELETE FROM subscribers WHERE id=?", (sid,))
        conn.commit()
        return redirect("/admin?tab=subscribers&msg=" + urllib.parse.quote("Subscriber removed."))

    if path == "/admin/salaries/create" and method == "POST":
        title = payload.get("title", "").strip()
        category = payload.get("category", "Logistics").strip()
        median = get_int(payload.get("median", "80000"), 80000)
        low = get_int(payload.get("low", "60000"), 60000)
        high = get_int(payload.get("high", "110000"), 110000)
        samples = get_int(payload.get("samples", "500"), 500)
        trend = payload.get("trend", "+2.0%").strip() or "+2.0%"
        if title:
            conn.execute(
                "INSERT INTO salaries (title, category, median, low, high, samples, trend) VALUES (?,?,?,?,?,?,?)",
                (title, category, median, low, high, samples, trend)
            )
            conn.commit()
            return redirect("/admin?tab=salaries&msg=" + urllib.parse.quote(f"Salary entry '{title}' added."))
        return redirect("/admin?tab=salaries&err=" + urllib.parse.quote("Title is required."))

    if path == "/admin/salaries/delete" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0)
        conn.execute("DELETE FROM salaries WHERE id=?", (sid,))
        conn.commit()
        return redirect("/admin?tab=salaries&msg=" + urllib.parse.quote("Salary entry deleted."))

'''
        # Insert before the home route
        app_content = app_content.replace(
            '    # ---------- home ----------\n    if path == "/":',
            new_routes + '    # ---------- home ----------\n    if path == "/":',
        )

    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print(f"   app.py updated: {os.path.getsize(app_path):,} bytes")

    # 4. Fix Font Awesome fallback — add local copy reference
    print("[4] Patching views.py for better icon fallback...")
    views_path = os.path.join(base, 'views.py')
    with open(views_path, 'r', encoding='utf-8') as f:
        views_content = f.read()

    # Fix: add crossorigin and integrity hints to FA CDN + add fa-fallback CSS
    old_fa = '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">'
    new_fa = '''  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <style>/* FA icon size safety */svg:not([class]):not([width]):not([height]){max-width:24px!important;max-height:24px!important;}.fa-headset,.fa-globe,.fa-bolt,.fa-shield-halved{font-size:inherit!important;width:auto!important;height:auto!important;}</style>'''

    if old_fa in views_content and new_fa not in views_content:
        views_content = views_content.replace(old_fa, new_fa)
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(views_content)
        print("   views.py patched for FA safety")
    else:
        print("   views.py already patched or pattern not found")

    print("\n[DONE] All enhancements applied!")
    print("  Restart server: Stop and restart python app.py")
    print("  Visit: http://localhost:8000/admin?tab=users")
    print("  Visit: http://localhost:8000/admin?tab=applications")
    print("  Visit: http://localhost:8000/admin?tab=subscribers")
    print("  Visit: http://localhost:8000/admin?tab=salaries")


ADMIN_VIEWS_CONTENT = r'''import html
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
    return f'''
    <div class="stat-gauge-wrap">
      <svg class="stat-gauge-svg" viewBox="0 0 72 72">
        <circle class="stat-gauge-bg" cx="36" cy="36" r="28"></circle>
        <circle class="stat-gauge-fill" cx="36" cy="36" r="28"
          stroke="{color}"
          stroke-dasharray="{circ:.2f}"
          stroke-dashoffset="{offset:.2f}"></circle>
      </svg>
      <span class="stat-gauge-val">{percent}%</span>
    </div>'''

def mini_wave_svg(color="#10b981"):
    return f'''
    <svg class="trend-wave" viewBox="0 0 50 18" fill="none">
      <path d="M1 14 C 10 16, 15 4, 25 10 C 35 15, 40 2, 49 4" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
    </svg>'''

def status_pill(status):
    colors = {
        "Applied": ("pill-blue", "fa-clock"),
        "Reviewing": ("pill-amber", "fa-eye"),
        "Interview": ("pill-purple", "fa-calendar-check"),
        "Offer": ("pill-green", "fa-circle-check"),
        "Rejected": ("pill-red", "fa-xmark"),
    }
    cls, ico = colors.get(status, ("pill-blue", "fa-circle"))
    return f'<span class="pill-badge {cls}"><i class="fa-solid {ico}"></i> {e(status)}</span>'

def render_admin_dashboard(conn, user, message="", error="", tab="overview"):
    counts = db.counts(conn)
    today_videos_count = conn.execute("SELECT COUNT(*) FROM articles WHERE tag=\'Logistic Waves Today\' OR is_today=1").fetchone()[0]
    remote_jobs_count = conn.execute("SELECT COUNT(*) FROM jobs WHERE is_remote=1 OR workplace=\'Fully Remote\' OR workplace=\'Remote\'").fetchone()[0]
    applications_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    subscribers_count = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    today_videos = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, author, guest, duration, thumb, published, category FROM articles WHERE tag=\'Logistic Waves Today\' OR is_today=1 ORDER BY id DESC"
    ).fetchall()]

    all_articles = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, category, tag, author, published, is_today FROM articles ORDER BY id DESC LIMIT 200"
    ).fetchall()]

    all_jobs = [dict(r) for r in conn.execute(
        "SELECT id, slug, title, company_name, category, workplace, location, salary_display, posted_at FROM jobs ORDER BY id DESC LIMIT 200"
    ).fetchall()]

    all_companies = [dict(r) for r in conn.execute(
        "SELECT id, slug, name, initials, color, industries, location, employees, open_jobs FROM companies ORDER BY name ASC"
    ).fetchall()]

    all_users = [dict(r) for r in conn.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY id DESC"
    ).fetchall()]

    all_applications = []
    try:
        all_applications = [dict(r) for r in conn.execute(
            """SELECT a.id, a.status, a.note, a.created_at,
                      j.title as job_title, j.id as job_id, j.slug as job_slug,
                      u.name as user_name, u.email as user_email
               FROM applications a
               JOIN jobs j ON a.job_id=j.id
               JOIN users u ON a.user_id=u.id
               ORDER BY a.id DESC LIMIT 200"""
        ).fetchall()]
    except Exception:
        pass

    all_subscribers = [dict(r) for r in conn.execute(
        "SELECT id, email, created_at FROM subscribers ORDER BY id DESC"
    ).fetchall()]

    all_salaries = [dict(r) for r in conn.execute(
        "SELECT id, title, category, median, low, high, samples, trend FROM salaries ORDER BY id DESC"
    ).fetchall()]

    alert_html = ""
    if message:
        alert_html = f'<div class="admin-alert admin-alert-success"><i class="fa-solid fa-circle-check"></i> {e(message)}</div>'
    elif error:
        alert_html = f'<div class="admin-alert admin-alert-error"><i class="fa-solid fa-triangle-exclamation"></i> {e(error)}</div>'

    def nav_active(t):
        return "sidebar-link active" if tab == t else "sidebar-link"

    # ======================= OVERVIEW TAB =======================
    recent_videos_rows = "".join([
        f"""<tr>
          <td style="width:72px;"><img src="{e(v['thumb'] or '/static/images/fw_today_1.jpg')}" class="table-thumb" alt="thumb"></td>
          <td style="min-width:240px;"><strong>{e(v['title'])}</strong><br><small style="color:#64748b;">Guest: {e(v['guest'] or 'N/A')}</small></td>
          <td><span class="pill-badge pill-blue">{e(v['category'] or 'Video')}</span></td>
          <td style="white-space:nowrap;">{e(v['duration'] or '15 min')}</td>
          <td style="white-space:nowrap;color:#64748b;">{e(v['published'])}</td>
          <td style="width:90px;text-align:center;">
            <div class="action-btns" style="justify-content:center;">
              <a href="/articles/{e(v['slug'])}" target="_blank" class="btn-action-round" title="Live Preview"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/articles/delete" onsubmit="return confirm(\'Delete this video?\');" style="display:inline;">
                <input type="hidden" name="id" value="{v['id']}">
                <input type="hidden" name="tab" value="overview">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for v in today_videos[:5]
    ]) or '<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8;">No videos yet — click "Seed Today Videos" above.</td></tr>'

    recent_jobs_rows = "".join([
        f"""<tr>
          <td style="min-width:240px;"><strong>{e(j['title'])}</strong><br><small style="color:#64748b;">{e(j['company_name'])}</small></td>
          <td><span class="pill-badge pill-blue">{e(j['category'])}</span></td>
          <td><span class="pill-badge pill-amber">{e(j['workplace'])}</span></td>
          <td style="color:#475569;">{e(j['location'])}</td>
          <td style="font-weight:700;color:#0f172a;">{e(j['salary_display'] or 'Competitive')}</td>
          <td style="width:90px;text-align:center;">
            <div class="action-btns" style="justify-content:center;">
              <a href="/job/{e(j['slug'])}/{j['id']}" target="_blank" class="btn-action-round"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/jobs/delete" onsubmit="return confirm(\'Delete this job?\');" style="display:inline;">
                <input type="hidden" name="id" value="{j['id']}">
                <input type="hidden" name="tab" value="overview">
                <button type="submit" class="btn-action-delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for j in all_jobs[:5]
    ]) or '<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8;">No jobs found.</td></tr>'

    overview_content = f"""
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Platform Activity per Month (2026)</h3>
          <div class="chart-legend">
            <span><span class="legend-dot" style="background:#3874ff;"></span> Broadcast Videos</span>
            <span><span class="legend-dot" style="background:#60a5fa;"></span> Jobs &amp; Reports</span>
          </div>
        </div>
        <div class="bar-chart-container">
          <svg viewBox="0 0 650 200" style="width:100%;height:100%;">
            <line x1="40" y1="20" x2="630" y2="20" stroke="#f1f5f9" stroke-width="1" />
            <line x1="40" y1="60" x2="630" y2="60" stroke="#f1f5f9" stroke-width="1" />
            <line x1="40" y1="100" x2="630" y2="100" stroke="#f1f5f9" stroke-width="1" />
            <line x1="40" y1="140" x2="630" y2="140" stroke="#f1f5f9" stroke-width="1" />
            <line x1="40" y1="180" x2="630" y2="180" stroke="#e2e8f0" stroke-width="1" />
            <text x="25" y="24" fill="#94a3b8" font-size="10" text-anchor="end">25</text>
            <text x="25" y="64" fill="#94a3b8" font-size="10" text-anchor="end">20</text>
            <text x="25" y="104" fill="#94a3b8" font-size="10" text-anchor="end">15</text>
            <text x="25" y="144" fill="#94a3b8" font-size="10" text-anchor="end">10</text>
            <text x="25" y="184" fill="#94a3b8" font-size="10" text-anchor="end">5</text>
            <rect x="58" y="70" width="5" height="110" rx="2.5" fill="#3874ff" /><rect x="66" y="90" width="5" height="90" rx="2.5" fill="#93c5fd" /><text x="64" y="196" fill="#64748b" font-size="10" text-anchor="middle">Jan</text>
            <rect x="110" y="80" width="5" height="100" rx="2.5" fill="#3874ff" /><rect x="118" y="125" width="5" height="55" rx="2.5" fill="#93c5fd" /><text x="116" y="196" fill="#64748b" font-size="10" text-anchor="middle">Feb</text>
            <rect x="162" y="30" width="5" height="150" rx="2.5" fill="#3874ff" /><rect x="170" y="95" width="5" height="85" rx="2.5" fill="#93c5fd" /><text x="168" y="196" fill="#64748b" font-size="10" text-anchor="middle">Mar</text>
            <rect x="214" y="130" width="5" height="50" rx="2.5" fill="#3874ff" /><rect x="222" y="145" width="5" height="35" rx="2.5" fill="#93c5fd" /><text x="220" y="196" fill="#64748b" font-size="10" text-anchor="middle">Apr</text>
            <rect x="266" y="115" width="5" height="65" rx="2.5" fill="#3874ff" /><rect x="274" y="135" width="5" height="45" rx="2.5" fill="#93c5fd" /><text x="272" y="196" fill="#64748b" font-size="10" text-anchor="middle">May</text>
            <rect x="318" y="120" width="5" height="60" rx="2.5" fill="#3874ff" /><rect x="326" y="155" width="5" height="25" rx="2.5" fill="#93c5fd" /><text x="324" y="196" fill="#64748b" font-size="10" text-anchor="middle">Jun</text>
            <rect x="370" y="75" width="5" height="105" rx="2.5" fill="#3874ff" /><rect x="378" y="90" width="5" height="90" rx="2.5" fill="#93c5fd" /><text x="376" y="196" fill="#64748b" font-size="10" text-anchor="middle">Jul</text>
            <rect x="422" y="65" width="5" height="115" rx="2.5" fill="#3874ff" /><rect x="430" y="100" width="5" height="80" rx="2.5" fill="#93c5fd" /><text x="428" y="196" fill="#64748b" font-size="10" text-anchor="middle">Sep</text>
            <rect x="474" y="105" width="5" height="75" rx="2.5" fill="#3874ff" /><rect x="482" y="115" width="5" height="65" rx="2.5" fill="#93c5fd" /><text x="480" y="196" fill="#64748b" font-size="10" text-anchor="middle">Oct</text>
            <rect x="526" y="80" width="5" height="100" rx="2.5" fill="#3874ff" /><rect x="534" y="130" width="5" height="50" rx="2.5" fill="#93c5fd" /><text x="532" y="196" fill="#64748b" font-size="10" text-anchor="middle">Nov</text>
            <rect x="578" y="45" width="5" height="135" rx="2.5" fill="#3874ff" /><rect x="586" y="95" width="5" height="85" rx="2.5" fill="#93c5fd" /><text x="584" y="196" fill="#64748b" font-size="10" text-anchor="middle">Dec</text>
          </svg>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Platform Entities</h3>
          <span style="color:#94a3b8;font-size:13px;font-weight:600;">Distribution</span>
        </div>
        <div class="donut-chart-container">
          <svg width="150" height="150" viewBox="0 0 42 42">
            <circle cx="21" cy="21" r="15.91549430918954" fill="#ffffff"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#3874ff" stroke-width="5" stroke-dasharray="54 46" stroke-dashoffset="25"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#34d399" stroke-width="5" stroke-dasharray="30 70" stroke-dashoffset="71"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#f87171" stroke-width="5" stroke-dasharray="16 84" stroke-dashoffset="41"></circle>
            <text x="21" y="22" font-size="7" font-weight="800" text-anchor="middle" fill="#202224" dy=".3em">100%</text>
          </svg>
          <div class="donut-legend-list">
            <div class="donut-legend-item"><span><span class="legend-dot" style="background:#3874ff;"></span> Editorial Articles</span><strong>54%</strong></div>
            <div class="donut-legend-item"><span><span class="legend-dot" style="background:#34d399;"></span> Active Jobs</span><strong>30%</strong></div>
            <div class="donut-legend-item"><span><span class="legend-dot" style="background:#f87171;"></span> Today Broadcasts</span><strong>16%</strong></div>
          </div>
        </div>
      </div>
    </div>
    <div class="table-card">
      <div class="table-header-bar">
        <h3 class="table-title"><i class="fa-solid fa-video" style="color:#3874ff;margin-right:8px;"></i> Live Today Broadcast Episodes</h3>
        <a href="/admin?tab=videos" style="color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;">View All ({len(today_videos)}) &rarr;</a>
      </div>
      <table class="clean-table">
        <thead><tr><th style="width:72px;">Thumb</th><th>Title &amp; Guest</th><th>Category</th><th>Duration</th><th>Published</th><th style="width:90px;text-align:center;">Action</th></tr></thead>
        <tbody>{recent_videos_rows}</tbody>
      </table>
    </div>
    <div class="table-card">
      <div class="table-header-bar">
        <h3 class="table-title"><i class="fa-solid fa-briefcase" style="color:#10b981;margin-right:8px;"></i> Active Job Listings</h3>
        <a href="/admin?tab=jobs" style="color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;">View All ({len(all_jobs)}) &rarr;</a>
      </div>
      <table class="clean-table">
        <thead><tr><th>Role &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th style="width:90px;text-align:center;">Action</th></tr></thead>
        <tbody>{recent_jobs_rows}</tbody>
      </table>
    </div>"""

    # ======================= VIDEOS TAB =======================
    video_rows = "".join([
        f"""<tr>
          <td><img src="{e(v['thumb'] or '/static/images/fw_today_1.jpg')}" class="table-thumb" alt="thumb"></td>
          <td><strong>{e(v['title'])}</strong><br><small style="color:#64748b;">/{e(v['slug'])}</small></td>
          <td><strong style="color:#3874ff;">{e(v['guest'] or '—')}</strong></td>
          <td><span class="pill-badge pill-blue">{e(v['category'] or 'Maritime')}</span></td>
          <td>{e(v['duration'] or '15:00 min')}</td>
          <td style="color:#64748b;">{e(v['published'])}</td>
          <td>
            <div class="action-btns">
              <a href="/articles/{e(v['slug'])}" target="_blank" class="btn-action-round" title="Live Preview"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/articles/delete" onsubmit="return confirm(\'Delete this episode?\');" style="display:inline;">
                <input type="hidden" name="id" value="{v['id']}">
                <input type="hidden" name="tab" value="videos">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for v in today_videos
    ]) or '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94a3b8;">No Today episodes found. Click "Seed Today Videos" above.</td></tr>'

    videos_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-circle-plus" style="color:#3874ff;"></i> Add New Today Video</h3>
        <form method="post" action="/admin/videos/create">
          <input type="hidden" name="tab" value="videos">
          <div class="form-group"><label class="form-label">Episode Title *</label><input class="form-control" name="title" placeholder="e.g. Next-Gen Port Automation at Cai Mep" required></div>
          <div class="form-group"><label class="form-label">Featured Guest / Speaker</label><input class="form-control" name="guest" placeholder="e.g. Capt. Nguyen Van A"></div>
          <div class="form-group"><label class="form-label">Video Duration</label><input class="form-control" name="duration" placeholder="e.g. 15:30 min" value="14:20 min"></div>
          <div class="form-group"><label class="form-label">Category</label>
            <select class="form-control" name="category">
              <option value="Maritime &amp; Tech">Maritime &amp; Tech</option>
              <option value="Port Automation">Port Automation</option>
              <option value="Air Cargo">Air Cargo</option>
              <option value="Container Shipping">Container Shipping</option>
              <option value="Clean Freight">Clean Freight</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Thumbnail Preset</label>
            <select class="form-control" name="thumb_preset" onchange="if(this.value) document.getElementById('vid-thumb-input').value=this.value;">
              <option value="/static/images/fw_today_1.jpg">Preset 1: Rocket Logistics &amp; Port</option>
              <option value="/static/images/fw_today_2.svg">Preset 2: Electric Aviation &amp; Air Cargo</option>
              <option value="/static/images/fw_today_3.jpg">Preset 3: Space Coast Port Boom</option>
              <option value="/static/images/fw_today_4.jpg">Preset 4: Electric Flying Boat</option>
              <option value="/static/images/fw_today_5.jpg">Preset 5: Container Spot Rates &amp; AI</option>
              <option value="/static/images/fw_today_6.jpg">Preset 6: Green Ammonia</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Custom Image URL (Optional)</label><input class="form-control" id="vid-thumb-input" name="thumb" value="/static/images/fw_today_1.jpg"></div>
          <div class="form-group"><label class="form-label">Short Summary</label><textarea class="form-control" name="excerpt" rows="2" placeholder="Brief hook for the card..."></textarea></div>
          <div class="form-group"><label class="form-label">Video Notes &amp; Transcript</label><textarea class="form-control" name="body" rows="3" placeholder="Full transcript notes, timestamps..."></textarea></div>
          <button type="submit" class="btn-submit-clean"><i class="fa-solid fa-upload"></i> Publish Episode</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar">
          <h3 class="table-title">Logistic Waves Today Episodes ({len(today_videos)})</h3>
          <span style="font-size:13px;color:#64748b;">Feeds homepage &amp; article-blogs</span>
        </div>
        <table class="clean-table">
          <thead><tr><th>Thumb</th><th>Title &amp; Slug</th><th>Guest</th><th>Category</th><th>Duration</th><th>Date</th><th>Action</th></tr></thead>
          <tbody>{video_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= ARTICLES TAB =======================
    articles_rows = "".join([
        f"""<tr>
          <td><strong>{e(a['title'])}</strong><br><small style="color:#64748b;">/{e(a['slug'])}</small> {('<span class="pill-badge pill-blue" style="margin-left:6px;">Today</span>' if a['is_today'] else '')}</td>
          <td><span class="pill-badge pill-amber">{e(a['category'] or 'General')}</span></td>
          <td>{e(a['tag'] or '—')}</td>
          <td>{e(a['author'] or 'Editorial Staff')}</td>
          <td style="white-space:nowrap;color:#64748b;">{e(a['published'])}</td>
          <td>
            <div class="action-btns">
              <a href="/articles/{e(a['slug'])}" target="_blank" class="btn-action-round" title="Live Preview"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/articles/delete" onsubmit="return confirm(\'Delete this article?\');" style="display:inline;">
                <input type="hidden" name="id" value="{a['id']}">
                <input type="hidden" name="tab" value="articles">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for a in all_articles
    ]) or '<tr><td colspan="6" style="text-align:center;padding:32px;color:#94a3b8;">No articles found.</td></tr>'

    articles_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-pen-nib" style="color:#3874ff;"></i> Publish New Article</h3>
        <form method="post" action="/admin/articles/create">
          <input type="hidden" name="tab" value="articles">
          <div class="form-group"><label class="form-label">Article Title *</label><input class="form-control" name="title" placeholder="e.g. 2027 Maritime Freight Trends in SE Asia" required></div>
          <div class="form-group"><label class="form-label">Category</label>
            <select class="form-control" name="category">
              <option value="Maritime &amp; Supply Chain">Maritime &amp; Supply Chain</option>
              <option value="Logistics Tech">Logistics Tech</option>
              <option value="Port Infrastructure">Port Infrastructure</option>
              <option value="Freight Rates">Freight Rates</option>
              <option value="Technology">Technology</option>
              <option value="Career &amp; Talent">Career &amp; Talent</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Author Name</label><input class="form-control" name="author" value="Editorial Staff"></div>
          <div class="form-group"><label class="form-label">Tag / Theme</label><input class="form-control" name="tag" value="Maritime Insights" placeholder="e.g. Maritime Insights, Tech Trends"></div>
          <div class="form-group"><label class="form-label">Read Time</label><input class="form-control" name="read_time" value="6 min read"></div>
          <div class="form-group"><label class="form-label">Summary / Excerpt</label><textarea class="form-control" name="excerpt" rows="2" placeholder="Brief summary for listings and cards..."></textarea></div>
          <div class="form-group"><label class="form-label">Article Content *</label><textarea class="form-control" name="body" rows="4" placeholder="Full article body paragraphs..." required></textarea></div>
          <button type="submit" class="btn-submit-clean"><i class="fa-solid fa-upload"></i> Publish Article</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar">
          <h3 class="table-title">All Articles &amp; Reports ({len(all_articles)})</h3>
        </div>
        <table class="clean-table">
          <thead><tr><th>Title &amp; Slug</th><th>Category</th><th>Tag</th><th>Author</th><th>Date</th><th>Action</th></tr></thead>
          <tbody>{articles_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= JOBS TAB =======================
    company_options = "".join([f'<option value="{e(c["slug"])}">{e(c["name"])}</option>' for c in all_companies])
    jobs_rows = "".join([
        f"""<tr>
          <td><strong>{e(j['title'])}</strong><br><small style="color:#64748b;">{e(j['company_name'])}</small></td>
          <td>{e(j['category'])}</td>
          <td><span class="pill-badge pill-blue">{e(j['workplace'])}</span></td>
          <td>{e(j['location'])}</td>
          <td style="font-weight:700;">{e(j['salary_display'] or 'Competitive')}</td>
          <td style="color:#64748b;">{e(j['posted_at'])}</td>
          <td>
            <div class="action-btns">
              <a href="/job/{e(j['slug'])}/{j['id']}" target="_blank" class="btn-action-round"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/jobs/delete" onsubmit="return confirm(\'Delete this job?\');" style="display:inline;">
                <input type="hidden" name="id" value="{j['id']}">
                <input type="hidden" name="tab" value="jobs">
                <button type="submit" class="btn-action-delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for j in all_jobs
    ]) or '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94a3b8;">No jobs found.</td></tr>'

    jobs_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-briefcase" style="color:#10b981;"></i> Post New Job</h3>
        <form method="post" action="/admin/jobs/create">
          <input type="hidden" name="tab" value="jobs">
          <div class="form-group"><label class="form-label">Job Title *</label><input class="form-control" name="title" placeholder="e.g. Port Terminal Automation Specialist" required></div>
          <div class="form-group"><label class="form-label">Company *</label><select class="form-control" name="company_slug" required>{company_options}</select></div>
          <div class="form-group"><label class="form-label">Category</label>
            <select class="form-control" name="category">
              <option value="Engineering &amp; Architecture">Engineering &amp; Architecture</option>
              <option value="Operations &amp; Robotics">Operations &amp; Robotics</option>
              <option value="Data &amp; AI">Data &amp; AI</option>
              <option value="Product Management">Product Management</option>
              <option value="Supply Chain Solutions">Supply Chain Solutions</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Workplace Policy</label>
            <select class="form-control" name="workplace">
              <option value="Hybrid">Hybrid</option>
              <option value="Fully Remote">Fully Remote</option>
              <option value="On Site">On Site</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Location</label><input class="form-control" name="location" value="Haiphong / Da Nang / Remote"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label class="form-label">Min Salary ($)</label><input type="number" class="form-control" name="salary_min" value="50000"></div>
            <div class="form-group"><label class="form-label">Max Salary ($)</label><input type="number" class="form-control" name="salary_max" value="85000"></div>
          </div>
          <div class="form-group"><label class="form-label">Skills &amp; Tech Stack</label><input class="form-control" name="skills" placeholder="e.g. SCADA, TOS, Python, IoT, Kafka"></div>
          <div class="form-group"><label class="form-label">Role Description</label><textarea class="form-control" name="description" rows="3" placeholder="Core responsibilities, qualifications..."></textarea></div>
          <button type="submit" class="btn-submit-clean" style="background:#10b981;"><i class="fa-solid fa-plus"></i> Publish Job Listing</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar"><h3 class="table-title">Active Job Listings ({len(all_jobs)})</h3></div>
        <table class="clean-table">
          <thead><tr><th>Title &amp; Company</th><th>Category</th><th>Workplace</th><th>Location</th><th>Salary</th><th>Posted</th><th>Action</th></tr></thead>
          <tbody>{jobs_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= COMPANIES TAB =======================
    companies_rows = "".join([
        f"""<tr>
          <td>
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:10px;background:{e(c['color'] or '#3874ff')};color:#fff;font-weight:800;font-size:13px;">{e(c['initials'])}</span>
              <div><strong>{e(c['name'])}</strong><br><small style="color:#64748b;">{e(c['slug'])}</small></div>
            </div>
          </td>
          <td><span class="pill-badge pill-blue">{e(c['industries'] or 'Logistics')}</span></td>
          <td>{e(c['location'])}</td>
          <td>{c['employees']:,} employees</td>
          <td><span class="pill-badge pill-green">{c['open_jobs']} Openings</span></td>
          <td>
            <div class="action-btns">
              <a href="/company/{e(c['slug'])}" target="_blank" class="btn-action-round" title="Company Profile"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/companies/delete" onsubmit="return confirm(\'Delete company and all associated jobs?\');" style="display:inline;">
                <input type="hidden" name="id" value="{c['id']}">
                <input type="hidden" name="tab" value="companies">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for c in all_companies
    ]) or '<tr><td colspan="6" style="text-align:center;padding:32px;color:#94a3b8;">No companies found.</td></tr>'

    companies_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-building" style="color:#8b5cf6;"></i> Register Company</h3>
        <form method="post" action="/admin/companies/create">
          <input type="hidden" name="tab" value="companies">
          <div class="form-group"><label class="form-label">Company Name *</label><input class="form-control" name="name" placeholder="e.g. Saigon Port Authority" required></div>
          <div class="form-group"><label class="form-label">Tagline</label><input class="form-control" name="tagline" placeholder="e.g. Modern Deepwater Port &amp; Logistics Hub"></div>
          <div class="form-group"><label class="form-label">Industries</label><input class="form-control" name="industries" value="Logistics &amp; Maritime Shipping"></div>
          <div class="form-group"><label class="form-label">Headquarters / Location</label><input class="form-control" name="location" value="Ho Chi Minh City, Vietnam"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label class="form-label">Employees</label><input type="number" class="form-control" name="employees" value="1500"></div>
            <div class="form-group"><label class="form-label">Brand Color</label><input class="form-control" name="color" value="#034f9a" placeholder="#034f9a"></div>
          </div>
          <div class="form-group"><label class="form-label">Website</label><input class="form-control" name="website" value="https://example.com"></div>
          <div class="form-group"><label class="form-label">Description</label><textarea class="form-control" name="description" rows="3" placeholder="Overview of terminal assets, logistics infrastructure..."></textarea></div>
          <button type="submit" class="btn-submit-clean" style="background:#8b5cf6;"><i class="fa-solid fa-plus"></i> Register Company</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar"><h3 class="table-title">Registered Companies ({len(all_companies)})</h3></div>
        <table class="clean-table">
          <thead><tr><th>Company</th><th>Industry</th><th>Headquarters</th><th>Team Size</th><th>Jobs</th><th>Action</th></tr></thead>
          <tbody>{companies_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= USERS TAB =======================
    users_rows = "".join([
        f"""<tr>
          <td>
            <div style="display:flex;align-items:center;gap:10px;">
              <div style="width:34px;height:34px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0;">{e((u['name'] or 'U')[0].upper())}</div>
              <div><strong>{e(u['name'])}</strong><br><small style="color:#64748b;">{e(u['email'])}</small></div>
            </div>
          </td>
          <td>
            <form method="post" action="/admin/users/role" style="display:inline-flex;align-items:center;gap:6px;">
              <input type="hidden" name="id" value="{u['id']}">
              <select name="role" class="form-control" style="padding:4px 8px;font-size:12px;min-width:110px;" onchange="this.form.submit()">
                <option value="candidate" {"selected" if u["role"]=="candidate" else ""}>Candidate</option>
                <option value="employer" {"selected" if u["role"]=="employer" else ""}>Employer</option>
                <option value="admin" {"selected" if u["role"]=="admin" else ""}>Admin</option>
              </select>
            </form>
          </td>
          <td style="color:#64748b;font-size:13px;">{e(u['created_at'] or '—')}</td>
          <td>
            <div class="action-btns">
              <form method="post" action="/admin/users/delete" onsubmit="return confirm(\'Permanently delete this user and all their data?\');" style="display:inline;">
                <input type="hidden" name="id" value="{u['id']}">
                <button type="submit" class="btn-action-delete" title="Delete User"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for u in all_users
    ]) or '<tr><td colspan="4" style="text-align:center;padding:32px;color:#94a3b8;">No registered users found.</td></tr>'

    users_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-user-plus" style="color:#3874ff;"></i> Create Demo User</h3>
        <form method="post" action="/admin/users/create">
          <input type="hidden" name="tab" value="users">
          <div class="form-group"><label class="form-label">Full Name *</label><input class="form-control" name="name" placeholder="e.g. Nguyen Van A" required></div>
          <div class="form-group"><label class="form-label">Email *</label><input class="form-control" type="email" name="email" placeholder="e.g. user@example.com" required></div>
          <div class="form-group"><label class="form-label">Password</label><input class="form-control" type="password" name="password" value="demo1234" placeholder="default: demo1234"></div>
          <div class="form-group"><label class="form-label">Role</label>
            <select class="form-control" name="role">
              <option value="candidate">Candidate (Job Seeker)</option>
              <option value="employer">Employer (Company)</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px;margin-bottom:12px;font-size:13px;color:#1d4ed8;">
            <i class="fa-solid fa-circle-info"></i> <strong>Demo accounts:</strong><br>
            candidate@demo.com / demo1234<br>
            employer@demo.com / demo1234
          </div>
          <button type="submit" class="btn-submit-clean"><i class="fa-solid fa-plus"></i> Create User</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar"><h3 class="table-title">Registered Users ({len(all_users)})</h3><span style="font-size:13px;color:#64748b;">Click role to change instantly</span></div>
        <table class="clean-table">
          <thead><tr><th>Name &amp; Email</th><th>Role</th><th>Joined</th><th>Action</th></tr></thead>
          <tbody>{users_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= APPLICATIONS TAB =======================
    app_statuses = ["Applied", "Reviewing", "Interview", "Offer", "Rejected"]
    applications_rows = "".join([
        f"""<tr>
          <td><strong>{e(a['user_name'])}</strong><br><small style="color:#64748b;">{e(a['user_email'])}</small></td>
          <td><a href="/job/{e(a['job_slug'])}/{a['job_id']}" target="_blank" style="color:#3874ff;font-weight:700;text-decoration:none;">{e(a['job_title'])}</a></td>
          <td>{status_pill(a['status'])}</td>
          <td style="max-width:180px;font-size:13px;color:#475569;">{e((a['note'] or '')[:60])}{"..." if len(a['note'] or "") > 60 else ""}</td>
          <td style="color:#64748b;font-size:13px;white-space:nowrap;">{e((a['created_at'] or '')[:10])}</td>
          <td>
            <div class="action-btns">
              <details style="position:relative;">
                <summary class="btn-action-round" style="list-style:none;cursor:pointer;" title="Update Status"><i class="fa-solid fa-pen-to-square"></i></summary>
                <div style="position:absolute;right:0;top:30px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:8px;z-index:50;min-width:140px;box-shadow:0 4px 20px rgba(0,0,0,.12);">
                  <form method="post" action="/admin/applications/status">
                    <input type="hidden" name="id" value="{a['id']}">
                    {"".join([f'<button type="submit" name="status" value="{s}" style="display:block;width:100%;text-align:left;padding:5px 8px;border:none;background:none;cursor:pointer;font-size:13px;border-radius:6px;" onmouseover="this.style.background=\'#f1f5f9\'" onmouseout="this.style.background=\'none\'">{s}</button>' for s in app_statuses])}
                  </form>
                </div>
              </details>
              <form method="post" action="/admin/applications/delete" onsubmit="return confirm(\'Delete this application?\');" style="display:inline;">
                <input type="hidden" name="id" value="{a['id']}">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for a in all_applications
    ]) or '<tr><td colspan="6" style="text-align:center;padding:32px;color:#94a3b8;">No applications yet. Users apply from job pages.</td></tr>'

    # Application status summary
    status_counts = {}
    for a in all_applications:
        status_counts[a['status']] = status_counts.get(a['status'], 0) + 1

    status_summary_pills = "".join([
        f'<span class="pill-badge pill-blue" style="margin-right:6px;">{s}: <strong>{c}</strong></span>'
        for s, c in status_counts.items()
    ]) or '<span style="color:#94a3b8;font-size:13px;">No applications yet</span>'

    applications_content = f"""
    <div class="table-card">
      <div class="table-header-bar">
        <h3 class="table-title"><i class="fa-solid fa-file-signature" style="color:#8b5cf6;margin-right:8px;"></i> Job Applications ({len(all_applications)})</h3>
        <div>{status_summary_pills}</div>
      </div>
      <div style="padding:0 24px 12px;">
        <p style="font-size:13px;color:#64748b;margin:0;">Applications submitted by candidates. Click the edit icon to update status. Candidates apply from individual job pages.</p>
      </div>
      <table class="clean-table">
        <thead><tr><th>Applicant</th><th>Job Position</th><th>Status</th><th>Notes</th><th>Applied</th><th>Action</th></tr></thead>
        <tbody>{applications_rows}</tbody>
      </table>
    </div>"""

    # ======================= SUBSCRIBERS TAB =======================
    subscribers_rows = "".join([
        f"""<tr>
          <td style="font-weight:600;">{e(s['email'])}</td>
          <td style="color:#64748b;font-size:13px;">{e((s['created_at'] or '')[:10])}</td>
          <td>
            <div class="action-btns">
              <form method="post" action="/admin/subscribers/delete" onsubmit="return confirm(\'Remove this subscriber?\');" style="display:inline;">
                <input type="hidden" name="id" value="{s['id']}">
                <button type="submit" class="btn-action-delete" title="Remove"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for s in all_subscribers
    ]) or '<tr><td colspan="3" style="text-align:center;padding:32px;color:#94a3b8;">No subscribers yet. Newsletter signups appear here.</td></tr>'

    subscribers_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-envelope" style="color:#3874ff;"></i> Newsletter Subscribers</h3>
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;margin-bottom:16px;">
          <div style="font-size:32px;font-weight:800;color:#1d4ed8;">{len(all_subscribers)}</div>
          <div style="font-size:14px;color:#3b82f6;font-weight:600;">Total Subscribers</div>
        </div>
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px;">
          <p style="font-size:13px;color:#166534;margin:0;">
            <i class="fa-solid fa-circle-info"></i> Subscribers sign up via the newsletter form in the site footer. 
            Their emails appear here automatically. You can remove subscribers individually.
          </p>
        </div>
        <div style="margin-top:16px;padding:14px;background:#fafafa;border:1px solid #e2e8f0;border-radius:10px;">
          <h4 style="font-size:14px;font-weight:700;margin:0 0 8px;">Quick Stats</h4>
          <div style="font-size:13px;color:#475569;line-height:1.8;">
            <div>&#10003; Total subscribers: <strong>{len(all_subscribers)}</strong></div>
            <div>&#10003; Newsletter form: <strong>/</strong> (homepage footer)</div>
            <div>&#10003; API endpoint: <strong>POST /api/newsletter</strong></div>
          </div>
        </div>
      </div>
      <div class="table-card">
        <div class="table-header-bar"><h3 class="table-title">All Subscribers ({len(all_subscribers)})</h3></div>
        <table class="clean-table">
          <thead><tr><th>Email Address</th><th>Subscribed On</th><th>Action</th></tr></thead>
          <tbody>{subscribers_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= SALARIES TAB =======================
    salaries_rows = "".join([
        f"""<tr>
          <td><strong>{e(s['title'])}</strong></td>
          <td><span class="pill-badge pill-amber">{e(s['category'])}</span></td>
          <td style="font-weight:700;color:#0f172a;">${s['median']:,}</td>
          <td style="color:#64748b;">${s['low']:,} &ndash; ${s['high']:,}</td>
          <td style="color:#64748b;">{s['samples']:,} samples</td>
          <td style="color:#10b981;font-weight:700;">{e(s['trend'])}</td>
          <td>
            <div class="action-btns">
              <a href="/salaries" target="_blank" class="btn-action-round" title="View Salaries Page"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
              <form method="post" action="/admin/salaries/delete" onsubmit="return confirm(\'Delete this salary entry?\');" style="display:inline;">
                <input type="hidden" name="id" value="{s['id']}">
                <button type="submit" class="btn-action-delete" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
              </form>
            </div>
          </td>
        </tr>"""
        for s in all_salaries
    ]) or '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94a3b8;">No salary data found.</td></tr>'

    salaries_content = f"""
    <div class="form-panel-grid">
      <div class="clean-card-form">
        <h3 class="form-title"><i class="fa-solid fa-chart-bar" style="color:#10b981;"></i> Add Salary Benchmark</h3>
        <form method="post" action="/admin/salaries/create">
          <input type="hidden" name="tab" value="salaries">
          <div class="form-group"><label class="form-label">Job Title *</label><input class="form-control" name="title" placeholder="e.g. Logistics Software Engineer" required></div>
          <div class="form-group"><label class="form-label">Category</label>
            <select class="form-control" name="category">
              <option value="Logistics &amp; Supply Chain">Logistics &amp; Supply Chain</option>
              <option value="Engineering">Engineering</option>
              <option value="Data &amp; Analytics">Data &amp; Analytics</option>
              <option value="Operations">Operations</option>
              <option value="Product Management">Product Management</option>
              <option value="Sales">Sales</option>
            </select>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
            <div class="form-group"><label class="form-label">Median ($)</label><input type="number" class="form-control" name="median" value="85000"></div>
            <div class="form-group"><label class="form-label">Low ($)</label><input type="number" class="form-control" name="low" value="62000"></div>
            <div class="form-group"><label class="form-label">High ($)</label><input type="number" class="form-control" name="high" value="118000"></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label class="form-label">Samples (reports)</label><input type="number" class="form-control" name="samples" value="1200"></div>
            <div class="form-group"><label class="form-label">Trend</label><input class="form-control" name="trend" value="+3.1%" placeholder="e.g. +3.1%"></div>
          </div>
          <button type="submit" class="btn-submit-clean" style="background:#10b981;"><i class="fa-solid fa-plus"></i> Add Salary Entry</button>
        </form>
      </div>
      <div class="table-card">
        <div class="table-header-bar"><h3 class="table-title">Salary Benchmarks ({len(all_salaries)})</h3><a href="/salaries" target="_blank" style="color:#3874ff;font-size:13px;font-weight:700;text-decoration:none;">Live Salaries Page &rarr;</a></div>
        <table class="clean-table">
          <thead><tr><th>Job Title</th><th>Category</th><th>Median</th><th>Range</th><th>Reports</th><th>Trend</th><th>Action</th></tr></thead>
          <tbody>{salaries_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ======================= ASSEMBLE =======================
    tab_bodies = {
        "overview": overview_content,
        "videos": videos_content,
        "articles": articles_content,
        "jobs": jobs_content,
        "companies": companies_content,
        "users": users_content,
        "applications": applications_content,
        "subscribers": subscribers_content,
        "salaries": salaries_content,
    }
    active_content = tab_bodies.get(tab, overview_content)

    admin_name = (user["name"] if user else "Admin") if user else "Admin"
    admin_initial = (admin_name[0].upper() if admin_name else "A")

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Admin Dashboard | Logistic Waves</title>
  <link rel="icon" type="image/png" href="/static/favicon.png">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="/static/admin.css?v=20261112_03">
</head>
<body class="admin-body">
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-brand-icon"><i class="fa-solid fa-shapes"></i></div>
        <a href="/admin" class="sidebar-brand-title">Dashboard</a>
      </div>
      <ul class="sidebar-menu">
        <li><a href="/admin?tab=overview" class="{nav_active('overview')}"><i class="fa-solid fa-house"></i> Overview</a></li>
        <li><a href="/admin?tab=videos" class="{nav_active('videos')}"><i class="fa-solid fa-video"></i> Videos / Today</a></li>
        <li><a href="/admin?tab=articles" class="{nav_active('articles')}"><i class="fa-solid fa-file-lines"></i> Articles</a></li>
        <li><a href="/admin?tab=jobs" class="{nav_active('jobs')}"><i class="fa-solid fa-briefcase"></i> Jobs &amp; Careers</a></li>
        <li><a href="/admin?tab=companies" class="{nav_active('companies')}"><i class="fa-solid fa-building"></i> Companies</a></li>
        <li class="sidebar-divider"></li>
        <li><a href="/admin?tab=users" class="{nav_active('users')}"><i class="fa-solid fa-users"></i> Users</a></li>
        <li><a href="/admin?tab=applications" class="{nav_active('applications')}"><i class="fa-solid fa-file-signature"></i> Applications</a></li>
        <li><a href="/admin?tab=subscribers" class="{nav_active('subscribers')}"><i class="fa-solid fa-envelope"></i> Subscribers</a></li>
        <li><a href="/admin?tab=salaries" class="{nav_active('salaries')}"><i class="fa-solid fa-chart-bar"></i> Salary Data</a></li>
      </ul>
      <div class="sidebar-footer">
        <a href="/" target="_blank"><i class="fa-solid fa-arrow-right-from-bracket"></i> Live Website</a>
      </div>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar">
        <div class="topbar-left">
          <a href="/admin?tab=videos" class="btn-add-new"><i class="fa-solid fa-plus"></i> Add New</a>
          <div class="search-box">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input type="text" class="search-input" placeholder="Search..." aria-label="Search">
          </div>
        </div>
        <div class="topbar-right">
          <div class="topbar-user">
            <div style="width:36px;height:36px;border-radius:50%;background:#3874ff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;">{e(admin_initial)}</div>
            <div class="topbar-user-info">
              <span class="topbar-user-name">{e(admin_name)}</span>
              <span class="topbar-user-role">Admin</span>
            </div>
            <i class="fa-solid fa-chevron-down" style="font-size:11px;color:#94a3b8;"></i>
          </div>
          <a href="#" class="topbar-icon-btn" title="Notifications">
            <i class="fa-regular fa-bell"></i>
            <span class="notification-dot"></span>
          </a>
          <a href="/" class="topbar-icon-btn" title="Exit to Site">
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
          </a>
        </div>
      </header>

      <div class="admin-container">
        {alert_html}

        <div class="admin-seed-control-card">
          <div class="seed-control-info">
            <div class="seed-control-icon"><i class="fa-solid fa-bolt"></i></div>
            <div class="seed-control-text">
              <h3>Fast Data Controls &amp; Seeders</h3>
              <p>One-click population of Logistic Waves Today videos, companies, and jobs.</p>
            </div>
          </div>
          <form method="post" action="/admin/seed" class="seed-control-buttons">
            <input type="hidden" name="tab" value="{e(tab)}">
            <button type="submit" name="action" value="seed_videos" class="btn-ctrl btn-ctrl-primary">
              <i class="fa-solid fa-play"></i> Seed Today Videos (6)
            </button>
            <button type="submit" name="action" value="seed_logistics" class="btn-ctrl btn-ctrl-success">
              <i class="fa-solid fa-truck-fast"></i> Seed Logistics &amp; Jobs
            </button>
            <button type="submit" name="action" value="reseed_all" class="btn-ctrl btn-ctrl-purple">
              <i class="fa-solid fa-database"></i> Reseed Full System
            </button>
            <button type="submit" name="action" value="clear_videos" class="btn-ctrl btn-ctrl-light" onclick="return confirm(\'Reset all Today videos?\');">
              <i class="fa-solid fa-trash-can"></i> Reset Videos
            </button>
          </form>
        </div>

        <div class="stat-cards-grid">
          <div class="stat-card">
            <div class="stat-card-left">
              {circular_gauge_svg(min(99, max(1, today_videos_count * 8)), "#3874ff")}
              <div class="stat-card-info">
                <h4>Today<br>Videos</h4>
                <div class="stat-number">{today_videos_count}</div>
                <div class="stat-card-trend trend-up">Live {mini_wave_svg("#3874ff")}</div>
              </div>
            </div>
            <i class="fa-solid fa-ellipsis stat-card-menu"></i>
          </div>
          <div class="stat-card">
            <div class="stat-card-left">
              {circular_gauge_svg(min(99, 40 + counts['articles'] // 3), "#10b981")}
              <div class="stat-card-info">
                <h4>Editorial<br>Articles</h4>
                <div class="stat-number">{counts['articles']}</div>
                <div class="stat-card-trend trend-up">16% &uarr; {mini_wave_svg("#10b981")}</div>
              </div>
            </div>
            <i class="fa-solid fa-ellipsis stat-card-menu"></i>
          </div>
          <div class="stat-card">
            <div class="stat-card-left">
              {circular_gauge_svg(min(99, 30 + counts['jobs'] // 4), "#06b6d4")}
              <div class="stat-card-info">
                <h4>Active<br>Jobs</h4>
                <div class="stat-number">{counts['jobs']}</div>
                <div class="stat-card-trend trend-up">12% &uarr; {mini_wave_svg("#06b6d4")}</div>
              </div>
            </div>
            <i class="fa-solid fa-ellipsis stat-card-menu"></i>
          </div>
          <div class="stat-card">
            <div class="stat-card-left">
              {circular_gauge_svg(min(99, 50 + users_count * 5), "#8b5cf6")}
              <div class="stat-card-info">
                <h4>Registered<br>Users</h4>
                <div class="stat-number">{users_count}</div>
                <div class="stat-card-trend trend-up">{applications_count} apps {mini_wave_svg("#8b5cf6")}</div>
              </div>
            </div>
            <i class="fa-solid fa-ellipsis stat-card-menu"></i>
          </div>
        </div>

        {active_content}
      </div>
    </main>
  </div>
</body>
</html>'''
'''


if __name__ == '__main__':
    run()
