"""Full-stack demo clone of a tech job board, served with the Python standard library.

Run:  python3 app.py
Then open the preview URL (port 8000 by default).
"""
import hashlib
import html
import gzip
import hmac
import json
import mimetypes
import os
import re
import secrets
import threading
import traceback
import urllib.parse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime

import db
import seed
import views

# ---------- CSRF protection (stateless HMAC-SHA256 for serverless compatibility) ----------
_CSRF_SECRET = (
    os.environ.get("CSRF_SECRET")
    or os.environ.get("DATABASE_URL")
    or "lw-csrf-fallback-dev-key"
).encode("utf-8")


def get_csrf_token(session_token: str) -> str:
    """Derive a deterministic, unforgeable CSRF token bound to the HttpOnly session token."""
    if not session_token:
        return ""
    return hmac.new(_CSRF_SECRET, session_token.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_csrf(session_token: str, submitted: str) -> bool:
    """Verify the submitted CSRF token matches the session-bound HMAC."""
    if not session_token or not submitted:
        return False
    expected = get_csrf_token(session_token)
    return bool(expected) and hmac.compare_digest(expected, submitted)


# ---------- Login rate limiting ----------
_login_attempts: dict = {}   # ip -> [timestamp, ...]
_login_lock = threading.Lock()
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300   # 5 minutes


def _check_rate_limit(ip: str) -> bool:
    now = datetime.utcnow().timestamp()
    with _login_lock:
        attempts = [t for t in _login_attempts.get(ip, []) if now - t < LOGIN_WINDOW_SECONDS]
        _login_attempts[ip] = attempts
        return len(attempts) >= LOGIN_MAX_ATTEMPTS


def _record_failed_login(ip: str) -> None:
    now = datetime.utcnow().timestamp()
    with _login_lock:
        lst = _login_attempts.get(ip, [])
        lst.append(now)
        _login_attempts[ip] = lst[-20:]


def _clear_login_attempts(ip: str) -> None:
    with _login_lock:
        _login_attempts.pop(ip, None)

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("PORT", "8000"))
SESSION_COOKIE = "bi_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30

mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("image/svg+xml", ".svg")

POST_PAGE_PATHS = {
    "/auth/login", "/auth/signup", "/logout", "/profile", "/alerts",
    "/alerts/delete", "/alerts/update", "/tracker/delete", "/employers/post-job",
    "/employers/jobs/update", "/employers/jobs/archive",
    "/admin/seed", "/admin/videos/create", "/admin/articles/create",
    "/admin/articles/update", "/admin/articles/delete",
    "/admin/jobs/create", "/admin/jobs/update", "/admin/jobs/delete",
    "/admin/companies/create", "/admin/companies/update", "/admin/companies/delete",
    "/admin/users/create", "/admin/users/delete", "/admin/users/role",
    "/admin/applications/delete", "/admin/applications/status",
    "/admin/subscribers/delete",
    "/admin/salaries/create", "/admin/salaries/update", "/admin/salaries/delete",
    "/api/newsletter", "/apply", "/saved/toggle", "/follow/toggle",
}


class Response:
    def __init__(self, body="", status=200, content_type="text/html; charset=utf-8",
                 headers=None, redirect=None, set_cookies=None, clear_cookies=None):
        self.body = body
        self.status = status
        self.content_type = content_type
        self.headers = headers or {}
        self.redirect = redirect
        self.set_cookies = set_cookies or []
        self.clear_cookies = clear_cookies or []


def json_response(data, status=200):
    return Response(json.dumps(data, ensure_ascii=False), status=status,
                    content_type="application/json; charset=utf-8")


def redirect(location, status=303, set_cookies=None, clear_cookies=None):
    return Response("", status=status, content_type="text/plain; charset=utf-8",
                    redirect=location, set_cookies=set_cookies, clear_cookies=clear_cookies)


def not_found(user, path):
    return Response(views.not_found_page(user, path), status=404)


def get_int(value, default, low=1, high=100000):
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return default


def safe_next(value):
    if not value:
        return "/"
    value = urllib.parse.unquote(str(value))
    # Must start with "/" but not "//" or "/\" (open redirect prevention)
    if value.startswith("/") and not value.startswith("//") and not value.startswith("/\\"):
        # Additional check: must not contain a scheme (e.g. javascript:)
        if ":" not in value.split("/")[1] if len(value) > 1 else True:
            return value
    return "/"


def require_login_api(user):
    if user:
        return None
    return json_response({"ok": False, "error": "Login required"}, status=401)


def login_required_page(user, next_path):
    body = views.signin_required(next_path)
    return Response(views.layout("Sign in to continue", body, user,
                                 page_class="narrow-shell",
                                 description="Sign in to use this feature."))


def parse_filters(query):
    return {k: v for k, v in query.items() if v not in (None, "", False, 0)}


def sitemap_xml(conn, host):
    paths = [
        "/", "/jobs", "/jobs/remote", "/companies", "/salaries", "/article-blogs",
        "/courses", "/tech-hubs", "/tech-dictionary", "/awards", "/remote", "/auth/login",
        "/auth/signup", "/employers",
    ]
    for row in conn.execute("SELECT slug FROM companies ORDER BY id"):
        paths.append("/company/" + row["slug"])
    for row in conn.execute("SELECT id,slug FROM jobs WHERE status='active' ORDER BY id"):
        paths.append(f'/job/{row["slug"]}/{row["id"]}')
    for row in conn.execute("SELECT slug FROM articles ORDER BY id"):
        paths.append("/articles/" + row["slug"])
    for row in conn.execute("SELECT title FROM salaries ORDER BY id"):
        paths.append("/salaries/" + views.slugify(row["title"]))
    locs = "".join(
        f'<url><loc>https://{html.escape(host)}{html.escape(p)}</loc></url>' for p in paths
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + locs + "</urlset>")


# ---------- routing ----------

def route(conn, method, path, query, payload, user, token, host, client_ip=""):
    # Static assets
    if path.startswith("/static/"):
        if method not in ("GET", "HEAD"):
            return Response("Method not allowed", status=405, content_type="text/plain; charset=utf-8")
        rel = urllib.parse.unquote(path[len("/static/"):])
        target = (STATIC / rel).resolve()
        try:
            if STATIC.resolve() not in target.parents and target != STATIC.resolve():
                raise ValueError("outside static root")
        except ValueError:
            return Response("Forbidden", status=403, content_type="text/plain; charset=utf-8")
        if not target.is_file():
            return Response("Not found", status=404, content_type="text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        cache_ctrl = "public, max-age=31536000, immutable" if ctype and ("javascript" in ctype or "css" in ctype) else "public, max-age=86400"
        return Response(target.read_bytes(), content_type=ctype,
                        headers={"Cache-Control": cache_ctrl})

    if path.startswith("/assets/"):
        if method not in ("GET", "HEAD"):
            return Response("Method not allowed", status=405, content_type="text/plain; charset=utf-8")
        rel = urllib.parse.unquote(path[len("/assets/"):])
        target = (STATIC / "assets" / rel).resolve()
        try:
            if (STATIC / "assets").resolve() not in target.parents and target != (STATIC / "assets").resolve():
                raise ValueError("outside static assets root")
        except ValueError:
            return Response("Forbidden", status=403, content_type="text/plain; charset=utf-8")
        if not target.is_file():
            return Response("Not found", status=404, content_type="text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        cache_ctrl = "public, max-age=31536000, immutable" if ctype and ("javascript" in ctype or "css" in ctype) else "public, max-age=86400"
        return Response(target.read_bytes(), content_type=ctype,
                        headers={"Cache-Control": cache_ctrl})

    if path.startswith("/images/"):
        if method not in ("GET", "HEAD"):
            return Response("Method not allowed", status=405, content_type="text/plain; charset=utf-8")
        rel = urllib.parse.unquote(path[len("/images/"):])
        target = (STATIC / "images" / rel).resolve()
        try:
            if (STATIC / "images").resolve() not in target.parents and target != (STATIC / "images").resolve():
                raise ValueError("outside static images root")
        except ValueError:
            return Response("Forbidden", status=403, content_type="text/plain; charset=utf-8")
        if not target.is_file():
            return Response("Not found", status=404, content_type="text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        return Response(target.read_bytes(), content_type=ctype,
                        headers={"Cache-Control": "public, max-age=86400"})

    if path == "/favicon.ico":
        return Response("", status=204, content_type="image/x-icon")

    if path == "/health":
        return json_response({"ok": True, "service": "builtin-demo-clone", "stats": db.counts(conn)})

    if path == "/robots.txt":
        return Response("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n",
                        content_type="text/plain; charset=utf-8")

    if path == "/sitemap.xml":
        return Response(sitemap_xml(conn, host), content_type="application/xml; charset=utf-8")

    # ---------- JSON API ----------
    if path.startswith("/api/"):
        if path == "/api/me":
            if not user:
                return json_response({"ok": True, "logged_in": False})
            return json_response({"ok": True, "logged_in": True, "user": user,
                                  "stats": db.user_stats(conn, user["id"])})
        if path == "/api/search":
            q = query.get("q", "")
            data = db.global_search(conn, q, 8)
            data["ok"] = True
            data["query"] = q
            return json_response(data)
        if path == "/api/jobs":
            f = parse_filters(query)
            limit = get_int(query.get("limit", "12"), 12, 1, 50)
            page = get_int(query.get("page", "1"), 1, 1, 10000)
            items, total = db.list_jobs(conn, f, limit, (page - 1) * limit, user["id"] if user else None)
            return json_response({"ok": True, "jobs": items, "total": total, "page": page, "limit": limit})

        m = re.match(r"^/api/saved/(\d+)/toggle$", path)
        if m and method in ("POST", "GET"):
            guard = require_login_api(user)
            if guard:
                return guard
            job_id = int(m.group(1))
            if not db.get_job(conn, job_id):
                return json_response({"ok": False, "error": "Job not found."}, status=404)
            state = db.toggle_saved(conn, user["id"], job_id)
            return json_response({"ok": True, "saved": state, "job_id": job_id})

        m = re.match(r"^/api/follow/(\d+)/toggle$", path)
        if m and method in ("POST", "GET"):
            guard = require_login_api(user)
            if guard:
                return guard
            company_id = int(m.group(1))
            if not conn.execute("SELECT 1 FROM companies WHERE id=?", (company_id,)).fetchone():
                return json_response({"ok": False, "error": "Company not found."}, status=404)
            state = db.toggle_follow(conn, user["id"], company_id)
            return json_response({"ok": True, "followed": state, "company_id": company_id})

        m = re.match(r"^/api/apply/(\d+)$", path)
        if m and method == "POST":
            guard = require_login_api(user)
            if guard:
                return guard
            job_id = int(m.group(1))
            if not db.get_job(conn, job_id):
                return json_response({"ok": False, "error": "Job not found."}, status=404)
            ok, message = db.apply_job(conn, user["id"], job_id, payload.get("note", ""))
            return json_response({"ok": True, "already": not ok, "message": message})

        m = re.match(r"^/api/applications/(\d+)$", path)
        if m and method == "DELETE":
            guard = require_login_api(user)
            if guard:
                return guard
            if not db.delete_application(conn, user["id"], int(m.group(1))):
                return json_response({"ok": False, "error": "Application not found."}, status=404)
            return json_response({"ok": True, "message": "Application withdrawn."})

        if path == "/api/alerts":
            guard = require_login_api(user)
            if guard:
                return guard
            if method == "GET":
                return json_response({"ok": True, "alerts": db.list_alerts(conn, user["id"])})
            if method == "POST":
                filters = payload.get("filters") or {}
                if isinstance(filters, str):
                    try:
                        filters = json.loads(filters)
                    except (ValueError, TypeError):
                        filters = {}
                alert_id = db.create_alert(conn, user["id"], payload.get("query", ""),
                                           filters, payload.get("frequency", "Daily"))
                if not alert_id:
                    return json_response({"ok": False, "error": "Enter an alert name and valid frequency."}, status=400)
                return json_response({"ok": True, "id": alert_id, "message": "Job alert created."})

        m = re.match(r"^/api/alerts/(\d+)$", path)
        if m and method in ("PATCH", "DELETE"):
            guard = require_login_api(user)
            if guard:
                return guard
            if method == "PATCH":
                if not db.update_alert(conn, user["id"], int(m.group(1)),
                                       payload.get("query", ""),
                                       payload.get("frequency", "Daily")):
                    return json_response({"ok": False, "error": "Enter a name and a valid frequency."}, status=400)
                return json_response({"ok": True, "message": "Alert updated."})
            db.delete_alert(conn, user["id"], int(m.group(1)))
            return json_response({"ok": True, "message": "Alert deleted."})

        m = re.match(r"^/api/employer/jobs/(\d+)$", path)
        if m and method in ("PUT", "DELETE"):
            guard = require_login_api(user)
            if guard:
                return guard
            if user.get("role") != "employer":
                return json_response({"ok": False, "error": "Employer access required."}, status=403)
            job_id = int(m.group(1))
            if method == "PUT":
                ok, error = db.update_employer_job(conn, user["id"], job_id, payload)
                if not ok:
                    return json_response({"ok": False, "error": error}, status=400)
                job = conn.execute("SELECT slug FROM jobs WHERE id=?", (job_id,)).fetchone()
                return json_response({"ok": True, "message": "Job updated.",
                                      "slug": job["slug"] if job else ""})
            if not db.archive_employer_job(conn, user["id"], job_id):
                return json_response({"ok": False, "error": "Job not found."}, status=404)
            return json_response({"ok": True, "message": "Job archived."})

        if path == "/api/newsletter" and method == "POST":
            email = (payload.get("email") or "").strip()
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                return json_response({"ok": False, "error": "Enter a valid email address."}, status=400)
            _, message = db.subscribe(conn, email)
            return json_response({"ok": True, "message": message})

        return json_response({"ok": False, "error": "API endpoint not found."}, status=404)

    # Everything after this point is HTML. Only known POST endpoints accept POST.
    if method not in ("GET", "HEAD") and path not in POST_PAGE_PATHS:
        return Response("Method not allowed", status=405, content_type="text/plain; charset=utf-8")

    # ---------- authentication ----------
    # Friendly aliases for /signin and /signup
    if path == "/signin":
        return redirect("/auth/login" + ("?" + urllib.parse.urlencode(query) if query else ""), status=301)
    if path == "/signup":
        return redirect("/auth/signup" + ("?" + urllib.parse.urlencode(query) if query else ""), status=301)
    if path in ("/auth/login", "/auth/signup"):
        kind = "login" if path.endswith("login") else "signup"
        next_path = query.get("next", "") if method in ("GET", "HEAD") else payload.get("next", "")
        if method in ("GET", "HEAD"):
            return Response(views.auth_page(kind, next_path, preset_role=query.get("role", "candidate")))
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""
        if kind == "login":
            # Rate limit: block after 5 failed attempts within 5 minutes
            if _check_rate_limit(client_ip):
                return Response(views.auth_page(kind, next_path,
                                                error="Too many failed login attempts. Please wait 5 minutes and try again."))
            account = db.authenticate(conn, email, password)
            if not account:
                _record_failed_login(client_ip)
                return Response(views.auth_page(kind, next_path,
                                                error="That email or password doesn't match an account."))
            _clear_login_attempts(client_ip)
            new_token = db.create_session(conn, account["id"])
            destination = safe_next(next_path) if next_path else (
                "/employers" if account.get("role") == "employer" else "/profile"
            )
            return redirect(destination,
                            set_cookies=[(SESSION_COOKIE, new_token, SESSION_MAX_AGE)])
        role = payload.get("role", "candidate")
        if role not in ("candidate", "employer"):
            role = "candidate"
        uid, err = db.create_user(conn, payload.get("name", ""), email, password, role)
        if err:
            return Response(views.auth_page(kind, next_path, error=err, preset_role=role))
        new_token = db.create_session(conn, uid)
        destination = safe_next(next_path) if next_path else (
            "/employers" if role == "employer" else "/profile"
        )
        return redirect(destination,
                        set_cookies=[(SESSION_COOKIE, new_token, SESSION_MAX_AGE)])

    if path == "/logout":
        if token:
            db.delete_session(conn, token)
        return redirect("/", clear_cookies=[SESSION_COOKIE])

    # CSRF verification for all authenticated state-changing POST requests (skip API and login/signup/logout)
    if method == "POST" and user and path not in ("/auth/login", "/auth/signup", "/logout") and not path.startswith("/api/"):
        submitted_csrf = payload.get("_csrf", "")
        if not verify_csrf(token, submitted_csrf):
            body = ("<div style='text-align:center;padding:60px 20px'>"
                    "<h2>Invalid Request</h2>"
                    "<p>Your form submission could not be verified (CSRF token mismatch). "
                    "Please go back and try again.</p>"
                    "<a href='/'>← Back to Home</a></div>")
            return Response(views.layout("Invalid Request", body, user), status=403)

    # ---------- account pages ----------
    if path in (
        "/tracker", "/saved", "/alerts", "/profile", "/employers/post-job",
        "/alerts/delete", "/alerts/update", "/tracker/delete",
        "/employers/jobs/update", "/employers/jobs/archive",
    ) and not user:
        return login_required_page(user, path + ("?" + urllib.parse.urlencode(query) if query else ""))

    if path == "/profile":
        if method == "POST":
            db.update_profile(conn, user["id"], payload.get("name", ""),
                              payload.get("headline", ""), payload.get("location", ""))
            user = db.current_user(conn, token) or user
            return Response(views.profile_page(conn, user, db.user_stats(conn, user["id"]),
                                               message="Profile updated."))
        stats = db.user_stats(conn, user["id"])
        saved = db.list_saved_jobs(conn, user["id"])
        applications = db.list_applications(conn, user["id"])
        alerts = db.list_alerts(conn, user["id"])
        followed = db.list_followed_companies(conn, user["id"])
        return Response(views.dashboard_page(conn, user, saved, applications, alerts, followed, stats,
                                             title="Your Dashboard"))

    if path == "/saved":
        saved = db.list_saved_jobs(conn, user["id"])
        followed = db.list_followed_companies(conn, user["id"])
        return Response(views.saved_page(conn, user, saved, followed))

    if path == "/tracker":
        return Response(views.tracker_page(
            conn, user, db.list_applications(conn, user["id"]),
            message=query.get("message", ""),
        ))

    if path == "/tracker/delete" and method == "POST":
        db.delete_application(conn, user["id"], get_int(payload.get("id"), 0, 0, 10**9))
        return redirect("/tracker?" + urllib.parse.urlencode({"message": "Application withdrawn."}))

    if path == "/alerts":
        if method == "POST":
            alert_id = db.create_alert(conn, user["id"], payload.get("query", "My job search"),
                                       {}, payload.get("frequency", "Daily"))
            if not alert_id:
                return Response(views.alerts_page(
                    conn, user, db.list_alerts(conn, user["id"]),
                    error="Enter an alert name and choose a valid frequency.",
                ), status=400)
            return redirect("/alerts?" + urllib.parse.urlencode({"message": "Job alert created."}))
        return Response(views.alerts_page(conn, user, db.list_alerts(conn, user["id"]),
                                          company_slug=query.get("company", ""),
                                          message=query.get("message", ""),
                                          error=query.get("error", "")))

    if path == "/alerts/update" and method == "POST":
        updated = db.update_alert(
            conn, user["id"], get_int(payload.get("id"), 0, 0, 10**9),
            payload.get("query", ""), payload.get("frequency", "Daily"),
        )
        key = "message" if updated else "error"
        message = "Job alert updated." if updated else "Please enter an alert name and valid frequency."
        return redirect("/alerts?" + urllib.parse.urlencode({key: message}))

    if path == "/alerts/delete" and method == "POST":
        db.delete_alert(conn, user["id"], get_int(payload.get("id"), 0, 0, 10**9))
        return redirect("/alerts?" + urllib.parse.urlencode({"message": "Job alert deleted."}))

    if path == "/employers":
        if user and user.get("role") != "employer":
            return Response(views.employers_page(conn, None))
        posted = db.employer_jobs(conn, user["id"]) if user else []
        return Response(views.employers_page(conn, user, posted,
                                             message=query.get("message", ""),
                                             error=query.get("error", "")))

    if path == "/employers/post-job":
        if user.get("role") != "employer":
            return Response(views.employers_page(conn, None), status=403)
        if method == "POST":
            _, err = db.create_job(conn, payload, user["id"])
            if err:
                posted = db.employer_jobs(conn, user["id"])
                return Response(views.employers_page(conn, user, posted, error=err))
            return redirect("/employers?" + urllib.parse.urlencode(
                {"message": "Job published — it now appears in search."}))
        return redirect("/employers#post")

    if path == "/employers/jobs/update" and method == "POST":
        if user.get("role") != "employer":
            return Response("Employer access required.", status=403)
        ok, error = db.update_employer_job(
            conn, user["id"], get_int(payload.get("id"), 0, 0, 10**9), payload,
        )
        if not ok:
            return redirect("/employers?" + urllib.parse.urlencode({"error": error}))
        return redirect("/employers?" + urllib.parse.urlencode({"message": "Job updated."}))

    if path == "/employers/jobs/archive" and method == "POST":
        if user.get("role") != "employer":
            return Response("Employer access required.", status=403)
        if not db.archive_employer_job(conn, user["id"], get_int(payload.get("id"), 0, 0, 10**9)):
            return redirect("/employers?" + urllib.parse.urlencode({"error": "Job not found."}))
        return redirect("/employers?" + urllib.parse.urlencode({"message": "Job archived."}))

    # ---------- admin dashboard & data seeder ----------
    # SECURITY: All /admin routes require a logged-in admin user (admin role only)
    if path.startswith("/admin"):
        if not user:
            return redirect("/auth/login?next=" + urllib.parse.quote(path, safe=""))
        if user.get("role") != "admin":
            body = ("<div style='text-align:center;padding:60px 20px'>"
                    "<h2>Access Denied</h2>"
                    "<p>Admin privileges are required to access this area.</p>"
                    "<a href='/'>← Back to Home</a></div>")
            return Response(views.layout("Access Denied", body, user), status=403)

    if path in ("/admin", "/admin/dashboard"):
        msg = query.get("msg") or query.get("message", "")
        err = query.get("err") or query.get("error", "")
        tab = query.get("tab", "overview")
        page = get_int(query.get("page", "1"), 1, 1, 10000)
        q = query.get("q", "").strip()
        return Response(views.admin_dashboard_page(conn, user, message=msg, error=err, tab=tab, page=page, q=q))

    if path == "/admin/seed" and method == "POST":
        action = payload.get("action", "")
        tab = payload.get("tab", "overview")
        import admin_seed_helpers
        if action == "seed_videos":
            total, added = admin_seed_helpers.seed_sample_today_videos(conn)
            return redirect(f"/admin?tab=videos&msg=" + urllib.parse.quote(f"Successfully seeded {total} Logistic Waves Today broadcast episodes."))
        elif action == "seed_logistics":
            comps, jobs = admin_seed_helpers.seed_sample_logistics_companies_and_jobs(conn)
            return redirect(f"/admin?tab=overview&msg=" + urllib.parse.quote(f"Successfully seeded logistics entities: {comps} companies, {jobs} open jobs."))
        elif action == "reseed_all":
            seed.seed(conn)
            admin_seed_helpers.seed_sample_today_videos(conn)
            admin_seed_helpers.seed_sample_logistics_companies_and_jobs(conn)
            return redirect("/admin?tab=overview&msg=" + urllib.parse.quote("Database successfully reset and reseeded with default + logistics data."))
        elif action == "clear_videos":
            conn.execute("DELETE FROM articles WHERE tag='Logistic Waves Today' OR is_today=1")
            conn.commit()
            return redirect("/admin?tab=videos&msg=" + urllib.parse.quote("Logistic Waves Today video episodes reset."))
        return redirect(f"/admin?tab={tab}")

    if path == "/admin/videos/create" and method == "POST":
        title = payload.get("title", "").strip()
        guest = payload.get("guest", "").strip()
        duration = payload.get("duration", "15:00 min").strip()
        category = payload.get("category", "Maritime & Tech").strip()
        thumb = payload.get("thumb", "").strip() or payload.get("thumb_preset", "/static/images/fw_today_1.jpg")
        excerpt = payload.get("excerpt", "").strip() or f"Exclusive Logistic Waves Today broadcast examining {title}."
        body = payload.get("body", "").strip() or f"Full broadcast editorial analysis for {title} with featured guest {guest}."
        slug = views.slugify(title)
        
        ex = conn.execute("SELECT id FROM articles WHERE slug=?", (slug,)).fetchone()
        now_str = datetime.utcnow().strftime("%b %d, %Y")
        if ex:
            conn.execute(
                """UPDATE articles SET title=?, guest=?, duration=?, category=?, thumb=?, excerpt=?, body=?, is_today=1, tag='Logistic Waves Today' WHERE id=?""",
                (title, guest, duration, category, thumb, excerpt, body, ex[0])
            )
        else:
            conn.execute(
                """INSERT INTO articles (slug, title, excerpt, body, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (slug, title, excerpt, body, guest or "Editorial Desk", now_str, category, "Logistic Waves Today", f"{duration.split(':')[0]} min watch", "#0084ff", thumb, 1, duration, guest)
            )
        conn.commit()
        return redirect("/admin?tab=videos&msg=" + urllib.parse.quote(f"Video episode '{title}' published successfully!"))

    if path == "/admin/articles/create" and method == "POST":
        title = payload.get("title", "").strip()
        if not title or len(title) > 300:
            return redirect("/admin?tab=articles&err=" + urllib.parse.quote("Article title is required (max 300 characters)."))
        category = payload.get("category", "Maritime & Supply Chain").strip()
        author = payload.get("author", "Editorial Staff").strip()
        tag = payload.get("tag", "Maritime Insights").strip()
        read_time = payload.get("read_time", "6 min read").strip()
        thumb = payload.get("thumb", "").strip() or "/static/images/fw_today_1.jpg"
        excerpt = payload.get("excerpt", "").strip()
        body = payload.get("body", "").strip()
        slug = views.slugify(title)
        now_str = datetime.utcnow().strftime("%b %d, %Y")
        ex = conn.execute("SELECT id FROM articles WHERE slug=?", (slug,)).fetchone()
        if ex:
            conn.execute(
                """UPDATE articles SET title=?, category=?, author=?, tag=?, read_time=?, thumb=?, excerpt=?, body=? WHERE id=?""",
                (title, category, author, tag, read_time, thumb, excerpt, body, ex[0])
            )
        else:
            conn.execute(
                """INSERT INTO articles (slug, title, excerpt, body, author, published, category, tag, read_time, accent, thumb, is_today)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,0)""",
                (slug, title, excerpt, body, author, now_str, category, tag, read_time, "#034f9a", thumb)
            )
        conn.commit()
        return redirect("/admin?tab=articles&msg=" + urllib.parse.quote(f"Article '{title}' published successfully!"))

    if path == "/admin/articles/delete" and method == "POST":
        art_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "articles")
        conn.execute("DELETE FROM articles WHERE id=?", (art_id,))
        conn.commit()
        return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote("Item deleted successfully."))

    if path == "/admin/articles/update" and method == "POST":
        art_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "articles")
        title = payload.get("title", "").strip()
        category = payload.get("category", "Maritime & Supply Chain").strip()
        author = payload.get("author", "Editorial Staff").strip()
        tag = payload.get("tag", "Maritime Insights").strip()
        read_time = payload.get("read_time", "6 min read").strip()
        guest = payload.get("guest", "").strip()
        duration = payload.get("duration", "15:00 min").strip()
        thumb = payload.get("thumb", "").strip()
        excerpt = payload.get("excerpt", "").strip()
        body = payload.get("body", "").strip()
        if art_id:
            conn.execute(
                """UPDATE articles SET title=?, category=?, author=?, tag=?, read_time=?, guest=?, duration=?, thumb=?, excerpt=?, body=? WHERE id=?""",
                (title, category, author, tag, read_time, guest, duration, thumb, excerpt, body, art_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Article '{title}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Article ID not found."))

    if path == "/admin/jobs/create" and method == "POST":
        title = payload.get("title", "").strip()
        if not title or len(title) > 300:
            return redirect("/admin?tab=jobs&err=" + urllib.parse.quote("Job title is required (max 300 characters)."))
        comp_slug = payload.get("company_slug", "").strip()
        category = payload.get("category", "Engineering & Architecture").strip()
        workplace = payload.get("workplace", "Hybrid").strip()
        location = payload.get("location", "Vietnam").strip()
        salary_min = get_int(payload.get("salary_min", "50000"), 50000)
        salary_max = get_int(payload.get("salary_max", "85000"), 85000)
        skills = payload.get("skills", "").strip()
        description = payload.get("description", "").strip()
        slug = views.slugify(title)
        
        comp = conn.execute("SELECT id, name, initials, color FROM companies WHERE slug=?", (comp_slug,)).fetchone()
        if comp:
            cid, cname, cinit, ccolor = comp
            now_date = datetime.utcnow().strftime("%Y-%m-%d")
            conn.execute(
                """INSERT INTO jobs (slug, title, company_id, company_slug, company_name, company_initials, company_color,
                   category, level, workplace, location, salary_min, salary_max, salary_display, industries, skills, description,
                   posted_at, posted_label, is_remote, accent, status)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (slug, title, cid, comp_slug, cname, cinit, ccolor, category, "Mid-Senior", workplace, location,
                 salary_min, salary_max, f"${salary_min:,} - ${salary_max:,}", "Logistics & Technology", skills, description,
                 now_date, "Just now", 1 if "Remote" in workplace else 0, ccolor, "active")
            )
            conn.commit()
            return redirect("/admin?tab=jobs&msg=" + urllib.parse.quote(f"Job listing '{title}' published!"))
        else:
            return redirect("/admin?tab=jobs&err=" + urllib.parse.quote("Selected company not found."))

    if path == "/admin/jobs/delete" and method == "POST":
        job_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "jobs")
        conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        conn.commit()
        return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote("Job listing deleted."))

    if path == "/admin/jobs/update" and method == "POST":
        job_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "jobs")
        title = payload.get("title", "").strip()
        comp_slug = payload.get("company_slug", "").strip()
        category = payload.get("category", "Engineering & Architecture").strip()
        workplace = payload.get("workplace", "Hybrid").strip()
        location = payload.get("location", "Vietnam").strip()
        salary_min = get_int(payload.get("salary_min", "50000"), 50000)
        salary_max = get_int(payload.get("salary_max", "85000"), 85000)
        salary_display = payload.get("salary_display", "").strip()
        if not salary_display:
            salary_display = f"${salary_min:,} - ${salary_max:,}"
        skills = payload.get("skills", "").strip()
        description = payload.get("description", "").strip()
        level = payload.get("level", "Mid-Senior").strip()
        
        comp = conn.execute("SELECT id, name, initials, color FROM companies WHERE slug=?", (comp_slug,)).fetchone()
        if comp and job_id:
            cid, cname, cinit, ccolor = comp
            conn.execute(
                """UPDATE jobs SET title=?, company_id=?, company_slug=?, company_name=?, company_initials=?, company_color=?,
                   category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?, skills=?, description=?,
                   is_remote=?, accent=? WHERE id=?""",
                (title, cid, comp_slug, cname, cinit, ccolor, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 1 if "Remote" in workplace else 0, ccolor, job_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Job '{title}' updated successfully!"))
        elif job_id:
            conn.execute(
                """UPDATE jobs SET title=?, category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?, skills=?, description=?,
                   is_remote=? WHERE id=?""",
                (title, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 1 if "Remote" in workplace else 0, job_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Job '{title}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Job ID not found."))

    if path == "/admin/companies/create" and method == "POST":
        name = payload.get("name", "").strip()
        tagline = payload.get("tagline", "").strip()
        industries = payload.get("industries", "Logistics & Maritime").strip()
        location = payload.get("location", "Vietnam").strip()
        employees = get_int(payload.get("employees", "1000"), 1000)
        color = payload.get("color", "#034f9a").strip() or "#034f9a"
        website = payload.get("website", "https://example.com").strip()
        description = payload.get("description", "").strip()
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "CO"
        slug = views.slugify(name)
        
        ex = conn.execute("SELECT id FROM companies WHERE slug=?", (slug,)).fetchone()
        if ex:
            conn.execute(
                """UPDATE companies SET name=?, tagline=?, industries=?, location=?, employees=?, color=?, website=?, description=? WHERE id=?""",
                (name, tagline, industries, location, employees, color, website, description, ex[0])
            )
        else:
            conn.execute(
                """INSERT INTO companies (slug, name, initials, color, tagline, industries, description, location, employees, website, open_jobs, hiring_now)
                   VALUES (?,?,?,?,?,?,?,?,?,?,0,1)""",
                (slug, name, initials, color, tagline, industries, description, location, employees, website)
            )
        conn.commit()
        return redirect("/admin?tab=companies&msg=" + urllib.parse.quote(f"Company '{name}' registered successfully!"))

    if path == "/admin/companies/delete" and method == "POST":
        comp_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "companies")
        conn.execute("DELETE FROM jobs WHERE company_id=?", (comp_id,))
        conn.execute("DELETE FROM companies WHERE id=?", (comp_id,))
        conn.commit()
        return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote("Company and its listings deleted."))

    if path == "/admin/companies/update" and method == "POST":
        comp_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "companies")
        name = payload.get("name", "").strip()
        tagline = payload.get("tagline", "").strip()
        industries = payload.get("industries", "Logistics & Maritime").strip()
        location = payload.get("location", "Vietnam").strip()
        employees = get_int(payload.get("employees", "1000"), 1000)
        color = payload.get("color", "#034f9a").strip() or "#034f9a"
        website = payload.get("website", "https://example.com").strip()
        description = payload.get("description", "").strip()
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "CO"
        
        if comp_id and name:
            conn.execute(
                """UPDATE companies SET name=?, initials=?, tagline=?, industries=?, location=?, employees=?, color=?, website=?, description=? WHERE id=?""",
                (name, initials, tagline, industries, location, employees, color, website, description, comp_id)
            )
            conn.execute(
                """UPDATE jobs SET company_name=?, company_initials=?, company_color=?, accent=? WHERE company_id=?""",
                (name, initials, color, color, comp_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Company '{name}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Company ID and name are required."))

    # ---------- admin: users ----------
    if path == "/admin/users/create" and method == "POST":
        name = payload.get("name", "").strip()
        email = payload.get("email", "").strip().lower()
        password = payload.get("password", "").strip()
        role = payload.get("role", "candidate").strip()
        if role not in ("candidate", "employer", "admin"):
            role = "candidate"
        if name and email and password:
            uid, err = db.create_user(conn, name, email, password, role)
            if err:
                return redirect("/admin?tab=users&err=" + urllib.parse.quote(f"Error: {err}"))
            return redirect("/admin?tab=users&msg=" + urllib.parse.quote(f"User '{name}' created successfully!"))
        return redirect("/admin?tab=users&err=" + urllib.parse.quote("Name, email, and password are required."))

    if path == "/admin/users/delete" and method == "POST":
        uid = get_int(payload.get("id", "0"), 0, low=0)
        if uid == user["id"]:
            return redirect("/admin?tab=users&err=" + urllib.parse.quote("You cannot delete your own currently signed-in admin account."))
        conn.execute("DELETE FROM sessions WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM saved_jobs WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM follows WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM applications WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM alerts WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
        return redirect("/admin?tab=users&msg=" + urllib.parse.quote("User account deleted."))

    if path == "/admin/users/role" and method == "POST":
        uid = get_int(payload.get("id", "0"), 0, low=0)
        new_role = payload.get("role", "candidate").strip()
        if uid == user["id"] and new_role != "admin":
            return redirect("/admin?tab=users&err=" + urllib.parse.quote("You cannot remove admin privileges from your own account."))
        if new_role in ("candidate", "employer", "admin"):
            conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
            conn.commit()
        return redirect("/admin?tab=users&msg=" + urllib.parse.quote("User role updated."))

    # ---------- admin: applications ----------
    if path == "/admin/applications/delete" and method == "POST":
        aid = get_int(payload.get("id", "0"), 0, low=0)
        conn.execute("DELETE FROM applications WHERE id=?", (aid,))
        conn.commit()
        return redirect("/admin?tab=applications&msg=" + urllib.parse.quote("Application deleted."))

    if path == "/admin/applications/status" and method == "POST":
        aid = get_int(payload.get("id", "0"), 0, low=0)
        status = payload.get("status", "Reviewing").strip()
        note = payload.get("note", "").strip()
        conn.execute("UPDATE applications SET status=?, note=? WHERE id=?", (status, note, aid))
        conn.commit()
        return redirect("/admin?tab=applications&msg=" + urllib.parse.quote(f"Status updated to {status}."))

    # ---------- admin: subscribers ----------
    if path == "/admin/subscribers/delete" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0, low=0)
        conn.execute("DELETE FROM subscribers WHERE id=?", (sid,))
        conn.commit()
        return redirect("/admin?tab=subscribers&msg=" + urllib.parse.quote("Subscriber removed."))

    # ---------- admin: salaries ----------
    if path == "/admin/salaries/create" and method == "POST":
        title    = payload.get("title", "").strip()
        category = payload.get("category", "Logistics").strip()
        median   = get_int(payload.get("median", "80000"), 80000)
        low      = get_int(payload.get("low", "60000"), 60000)
        high     = get_int(payload.get("high", "110000"), 110000)
        samples  = get_int(payload.get("samples", "500"), 500)
        trend    = payload.get("trend", "+2.0%").strip() or "+2.0%"
        if title:
            conn.execute(
                "INSERT INTO salaries (title, category, median, low, high, samples, trend) VALUES (?,?,?,?,?,?,?)",
                (title, category, median, low, high, samples, trend)
            )
            conn.commit()
            return redirect("/admin?tab=salaries&msg=" + urllib.parse.quote(f"Salary entry '{title}' added."))
        return redirect("/admin?tab=salaries&err=" + urllib.parse.quote("Title is required."))

    if path == "/admin/salaries/delete" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0, low=0)
        conn.execute("DELETE FROM salaries WHERE id=?", (sid,))
        conn.commit()
        return redirect("/admin?tab=salaries&msg=" + urllib.parse.quote("Salary entry deleted."))

    if path == "/admin/salaries/update" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "salaries")
        title = payload.get("title", "").strip()
        category = payload.get("category", "Logistics").strip()
        median = get_int(payload.get("median", "80000"), 80000)
        low = get_int(payload.get("low", "60000"), 60000)
        high = get_int(payload.get("high", "110000"), 110000)
        samples = get_int(payload.get("samples", "500"), 500)
        trend = payload.get("trend", "+2.0%").strip() or "+2.0%"
        
        if sid and title:
            conn.execute(
                "UPDATE salaries SET title=?, category=?, median=?, low=?, high=?, samples=?, trend=? WHERE id=?",
                (title, category, median, low, high, samples, trend, sid)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Salary entry '{title}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Title and ID are required."))

    # ---------- home ----------
    if path == "/":
        return Response(views.home_page(conn, user))

    # ---------- jobs ----------
    if path == "/jobs/remote":
        f = parse_filters(query)
        f["remote"] = "1"
        page = get_int(query.get("page", "1"), 1)
        jobs, total = db.list_jobs(conn, f, 12, (page - 1) * 12, user["id"] if user else None)
        return Response(views.jobs_page(conn, user, f, jobs, total, page,
                                        max(1, (total + 11) // 12), heading="Remote Tech Jobs"))

    m = re.match(r"^/jobs/([^/]+)$", path)
    if m:
        category = views.CATEGORY_BY_SLUG.get(m.group(1))
        if not category:
            return not_found(user, path)
        f = parse_filters(query)
        f["category"] = category
        page = get_int(query.get("page", "1"), 1)
        jobs, total = db.list_jobs(conn, f, 12, (page - 1) * 12, user["id"] if user else None)
        return Response(views.jobs_page(conn, user, f, jobs, total, page,
                                        max(1, (total + 11) // 12), heading=f"{category} Jobs"))

    if path == "/jobs":
        f = parse_filters(query)
        page = get_int(query.get("page", "1"), 1)
        jobs, total = db.list_jobs(conn, f, 12, (page - 1) * 12, user["id"] if user else None)
        return Response(views.jobs_page(conn, user, f, jobs, total, page,
                                        max(1, (total + 11) // 12)))

    if path == "/job-detail.html" or path == "/job-detail":
        jid_str = query.get("id") or query.get("jobId") or "1"
        if str(jid_str).startswith("job-"):
            try:
                job_id = int(str(jid_str).replace("job-", ""))
            except ValueError:
                job_id = 1
        else:
            try:
                job_id = int(jid_str)
            except ValueError:
                job_id = 1
        job = db.get_job(conn, job_id) or db.get_job(conn, 1)
        if not job:
            return not_found(user, path)
        return Response(views.linkedin_job_detail_page(conn, user, job, db.similar_jobs(conn, job, 4)))

    m = re.match(r"^/job/([^/]+)/(\d+)$", path) or re.match(r"^/job/(\d+)$", path) or re.match(r"^/job/job-(\d+)$", path)
    if m:
        job_id = int(m.group(2) if m.lastindex == 2 else m.group(1))
        job = db.get_job(conn, job_id)
        if not job:
            return not_found(user, path)
        return Response(views.linkedin_job_detail_page(conn, user, job, db.similar_jobs(conn, job, 4)))

    # ---------- companies ----------
    if path == "/companies/hiring/remote":
        f = parse_filters(query)
        f["remote"] = "1"
        f["hiring"] = "1"
        page = get_int(query.get("page", "1"), 1)
        companies, total = db.list_companies(conn, f, 8, (page - 1) * 8, user["id"] if user else None)
        return Response(views.companies_page(conn, user, f, companies, total, page,
                                             max(1, (total + 7) // 8),
                                             heading="Companies Hiring Remotely"))

    if path == "/companies/location/fully-remote":
        f = parse_filters(query)
        f["office_type"] = "Fully Remote"
        f["remote"] = "1"
        page = get_int(query.get("page", "1"), 1)
        companies, total = db.list_companies(conn, f, 8, (page - 1) * 8, user["id"] if user else None)
        return Response(views.companies_page(conn, user, f, companies, total, page,
                                             max(1, (total + 7) // 8),
                                             heading="Fully Remote Companies"))

    m = re.match(r"^/companies/type/([^/]+)$", path)
    if m:
        slug = m.group(1).replace("-companies", "")
        industry = slug.replace("-", " ").title()
        f = parse_filters(query)
        f["industry"] = industry
        page = get_int(query.get("page", "1"), 1)
        companies, total = db.list_companies(conn, f, 8, (page - 1) * 8, user["id"] if user else None)
        return Response(views.companies_page(conn, user, f, companies, total, page,
                                             max(1, (total + 7) // 8),
                                             heading=f"Top {industry} Companies"))

    if path == "/companies":
        f = parse_filters(query)
        page = get_int(query.get("page", "1"), 1)
        companies, total = db.list_companies(conn, f, 8, (page - 1) * 8, user["id"] if user else None)
        return Response(views.companies_page(conn, user, f, companies, total, page,
                                             max(1, (total + 7) // 8)))

    m = re.match(r"^/company/([^/]+)(?:/(.+))?$", path)
    if m:
        company = db.get_company(conn, m.group(1))
        if not company:
            return not_found(user, path)
        tab = m.group(2) or ""
        allowed = {key for _, key in views.TABS}
        if tab and tab not in allowed and not tab.startswith("faq/"):
            return not_found(user, path)
        jobs = db.jobs_for_company(conn, company["slug"], 12)
        related = db.list_articles(conn, limit=3)
        return Response(views.linkedin_company_detail_page(conn, user, company, tab, jobs, related))

    # ---------- salaries ----------
    if path == "/salaries":
        return Response(views.salaries_page(conn, user, query.get("q", ""), query.get("category", "")))

    m = re.match(r"^/salaries/([^/]+)$", path)
    if m:
        preset = views.SALARY_BY_SLUG.get(m.group(1))
        if not preset:
            return not_found(user, path)
        rows = [r for r in db.list_salaries(conn, "", "") if r["title"] == preset["title"]]
        if not rows:
            return not_found(user, path)
        related, _ = db.list_jobs(conn, {"q": preset["title"]}, 4)
        if not related:
            related, _ = db.list_jobs(conn, {"category": preset["category"]}, 4)
        return Response(views.salary_detail_page(conn, user, rows[0], related))

    # ---------- articles ----------
    if path in ("/tech-topics", "/articles"):
        return redirect("/article-blogs", status=301)
    if path == "/article-blogs":
        return Response(views.articles_page(conn, user, query.get("q", ""),
                                            query.get("category", ""), query.get("tag", "")))

    m = re.match(r"^/tag/([^/]+)$", path)
    if m:
        slug = m.group(1)
        tag = "" if slug == "all" else views.TAG_BY_SLUG.get(slug, slug.replace("-", " ").title())
        return Response(views.articles_page(conn, user, query.get("q", ""), "", tag))

    m = re.match(r"^/articles/([^/]+)$", path)
    if m:
        article = db.get_article(conn, m.group(1))
        if not article:
            return not_found(user, path)
        related = [a for a in db.list_articles(conn, category=article["category"], limit=5)
                   if a["id"] != article["id"]][:4]
        return Response(views.article_detail_page(conn, user, article, related))

    # ---------- discovery ----------
    if path == "/tech-hubs":
        return Response(views.tech_hubs_page(conn, user))
    m = re.match(r"^/tech-hubs/([^/]+)$", path)
    if m:
        hub = views.HUB_BY_SLUG.get(m.group(1))
        if not hub:
            return not_found(user, path)
        return Response(views.tech_hubs_page(conn, user, hub))

    if path == "/tech-dictionary":
        return Response(views.dictionary_page(conn, user, query.get("q", "")))

    if path == "/courses":
        return Response(views.courses_page(conn, user, query))

    if path == "/awards":
        return Response(views.awards_page(conn, user))
    m = re.match(r"^/awards/([^/]+)/current/best-places-to-work$", path)
    if m:
        city = None if m.group(1) in ("us", "current") else m.group(1)
        return Response(views.awards_page(conn, user, city))

    if path == "/remote":
        return Response(views.remote_page(conn, user))

    if path == "/search":
        return Response(views.search_page(conn, user, query.get("q", "")))

    # ---------- static informational pages ----------
    if path == "/about":
        return Response(views.simple_page(
            "About This Demo", "Project overview",
            "A self-contained, full-stack clone built for learning and rapid prototyping.",
            [
                ("What is this?", "This is an independent demo inspired by the public layout and information architecture of a tech job board. It is not affiliated with, endorsed by, or connected to the original site."),
                ("What works", "Job and company search, filters, pagination, account sign-up and login, saved jobs, followed companies, applications, a tracker, job alerts, salary pages, articles and an employer portal that publishes new jobs into a SQLite database."),
                ("What is placeholder", "Company logos are generated as colored initial tiles, photos are inline SVG illustrations, and all copy is sample content. Add your own assets in static/ and your own content in seed.py."),
                ("Tech stack", "Python standard library HTTP server, SQLite, server-rendered HTML, vanilla CSS and JavaScript. No build step and no external runtime dependencies."),
            ], user))
    if path == "/contact":
        return Response(views.simple_page(
            "Contact", "Say hello",
            "This is a demo workspace, so there is no live support inbox.",
            [
                ("Customize the clone", "Edit files in /home/user/builtin-clone. Replace seed.py content, static assets and styles to match your own brand."),
                ("Report a bug", "Use the chat to describe the page and behavior you expected; the code can be adjusted in the workspace."),
                ("Assets", "Drop your own logos, photos and favicon into static/ and update the references in views.py and styles.css."),
            ], user))
    if path == "/privacy":
        return Response(views.simple_page(
            "Privacy Policy", "Demo notice",
            "A sample policy page for this workspace clone.",
            [
                ("Demo data", "Accounts, applications and alerts are stored locally in a SQLite file inside this workspace. Do not enter real personal information."),
                ("Cookies", "One HttpOnly session cookie keeps you signed in. No analytics or advertising trackers are used."),
                ("Production use", "Replace this page with a reviewed policy before deploying a real product."),
            ], user))
    if path == "/terms":
        return Response(views.simple_page(
            "Terms of Use", "Demo notice",
            "A sample terms page for this workspace clone.",
            [
                ("Purpose", "This project demonstrates a full-stack website clone for learning and prototyping only."),
                ("No affiliation", "It is not affiliated with the original website. Trademarks, logos and editorial content are represented by placeholders."),
                ("No warranty", "Sample data and demo accounts are provided as-is and may be reset at any time."),
            ], user))

    if path == "/node/add/company":
        return redirect("/employers/post-job")

    return not_found(user, path)


class Handler(BaseHTTPRequestHandler):
    server_version = "BuiltInDemo/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def _cookie_token(self):
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", "") or "")
        except Exception:
            return None
        item = jar.get(SESSION_COOKIE)
        return item.value if item else None

    def _payload(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length > 0 else b""
        ctype = (self.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
                return data if isinstance(data, dict) else {}
            except (ValueError, UnicodeDecodeError):
                return {}
        parsed = urllib.parse.parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True)
        return {k: (v[-1] if v else "") for k, v in parsed.items()}

    def _send(self, resp):
        try:
            if isinstance(resp.body, str):
                data = resp.body.encode("utf-8")
            elif isinstance(resp.body, bytes):
                data = resp.body
            else:
                data = str(resp.body).encode("utf-8")
            # Gzip compress HTML and JSON responses when client supports it
            accept_enc = self.headers.get("Accept-Encoding", "")
            use_gzip = "gzip" in accept_enc and len(data) > 1024 and (
                resp.content_type.startswith("text/html") or
                resp.content_type.startswith("application/json") or
                resp.content_type.startswith("text/css") or
                "javascript" in resp.content_type
            )
            if use_gzip:
                data = gzip.compress(data, compresslevel=6)
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.content_type)
            self.send_header("Content-Length", str(len(data)))
            if use_gzip:
                self.send_header("Content-Encoding", "gzip")
            if resp.redirect:
                self.send_header("Location", resp.redirect)
            if resp.content_type.startswith("text/html") or resp.content_type.startswith("application/json"):
                self.send_header("Cache-Control", "no-store")
            for key, value in resp.headers.items():
                self.send_header(key, value)
            for name, value, max_age in resp.set_cookies:
                self.send_header("Set-Cookie", f"{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}")
            for name in resp.clear_cookies:
                self.send_header("Set-Cookie", f"{name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
            # Security headers
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.send_header("X-XSS-Protection", "1; mode=block")
            self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), browsing-topics=()")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; img-src 'self' data: https: blob:; connect-src 'self' https:; frame-src 'self' https://www.youtube-nocookie.com https://www.youtube.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self';")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def _dispatch(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query_pairs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        query = {k: (v[-1] if v else "") for k, v in query_pairs.items()}
        payload = self._payload() if self.command in ("POST", "PUT", "PATCH", "DELETE") else {}
        token = self._cookie_token()
        conn = db.connect()
        try:
            user = db.current_user(conn, token)
            host = self.headers.get("Host", "localhost")
            client_ip = (self.client_address[0] if self.client_address else "") or ""
            # Set the per-request CSRF token so views can embed it in forms
            views._set_csrf(get_csrf_token(token))
            resp = route(conn, self.command, path, query, payload, user, token, host, client_ip)
            self._send(resp)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                body = views.layout("Something went wrong",
                                    '<section class="container narrow-page"><div class="empty-state"><h1>Something went wrong</h1><p>The demo server hit an unexpected error. Check the server log in the terminal/preview panel.</p><a class="btn btn-primary" href="/">Back to home</a></div></section>',
                                    None)
                self._send(Response(body, status=500))
            except Exception:
                pass
        finally:
            conn.close()

    def do_GET(self):
        self._dispatch()

    def do_HEAD(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch()

    def do_DELETE(self):
        self._dispatch()

    def do_PUT(self):
        self._dispatch()

    def do_PATCH(self):
        self._dispatch()


class Server(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


def main():
    db.init_db()
    server = Server(("0.0.0.0", PORT), Handler)
    print(f"Built In demo clone running at http://0.0.0.0:{PORT}", flush=True)
    print("Demo accounts: candidate@demo.com / demo1234  |  employer@demo.com / demo1234", flush=True)
    while True:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            break
        except Exception as ex:
            traceback.print_exc()
            print(f"Server warning: {ex}", flush=True)
            import time
            time.sleep(0.5)
        except BaseException as be:
            traceback.print_exc()
            print(f"Server critical: {be}", flush=True)
            break
    server.server_close()


if __name__ == "__main__":
    main()
