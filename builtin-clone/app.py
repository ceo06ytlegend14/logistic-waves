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
import cloudinary_helper

# ---------- CSRF protection (stateless HMAC-SHA256 for serverless compatibility) ----------
def _resolve_csrf_secret() -> bytes:
    env_secret = os.environ.get("CSRF_SECRET")
    if env_secret:
        return env_secret.encode("utf-8")
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if db_url:
        return hmac.new(db_url.encode("utf-8"), b"logistic-waves-csrf-v1", hashlib.sha256).digest()
    secret_file = Path(__file__).resolve().parent / "data" / ".csrf_secret"
    if secret_file.is_file():
        return secret_file.read_bytes().strip()
    raw = secrets.token_hex(32).encode("utf-8")
    try:
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        secret_file.write_bytes(raw)
    except Exception:
        pass
    return raw


_CSRF_SECRET = _resolve_csrf_secret()


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


# ---------- Rate limiting & Input validation constants ----------
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300   # 5 minutes
SIGNUP_MAX_ATTEMPTS = 5
SIGNUP_WINDOW_SECONDS = 600  # 10 minutes
MAX_BODY_BYTES = 4 * 1024 * 1024
ALLOWED_APP_STATUSES = {"Applied", "Reviewing", "Interview", "Offer", "Rejected"}
_DATA_IMG_RE = re.compile(
    r"^data:image/(png|jpeg|jpg|webp|gif);base64,[A-Za-z0-9+/=\s]+$",
    re.IGNORECASE,
)


class PayloadTooLargeError(ValueError):
    pass


class BadRequestError(ValueError):
    pass


def _clip(value, max_len: int) -> str:
    return (value or "").strip()[:max_len]


def _is_valid_email(email: str) -> bool:
    return bool(email and len(email) <= 254 and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def _safe_http_url(url: str, max_len: int = 500) -> str:
    val = _clip(url, max_len)
    if not val or any(c in val for c in ("\r", "\n", "\x00")):
        return ""
    parsed = urllib.parse.urlparse(val)
    return val if parsed.scheme.lower() in ("http", "https") and parsed.netloc else ""


def _safe_media_url(url: str, default: str = "") -> str:
    val = (url or "").strip()
    if not val or any(c in val for c in ("\r", "\n", "\x00")):
        return default
    if val.startswith("/") and not val.startswith("//"):
        return val if len(val) <= 500 else default
    if _DATA_IMG_RE.match(val) and len(val) <= 3_000_000:
        return val
    return _safe_http_url(val, max_len=1000) or default


def _resolve_client_ip(headers, direct_ip: str) -> str:
    if os.environ.get("VERCEL") or os.environ.get("TRUST_PROXY") == "1":
        real_ip = (headers.get("X-Real-IP") or "").strip()
        if real_ip:
            return real_ip[:64]
        xff = (headers.get("X-Forwarded-For") or "").split(",")[0].strip()
        if xff:
            return xff[:64]
    return (direct_ip or "unknown")[:64]

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
    "/employers/jobs/update", "/employers/jobs/archive", "/employers/applications/status",
    "/admin/seed", "/admin/videos/create", "/admin/articles/create",
    "/admin/articles/update", "/admin/articles/delete", "/admin/articles/duplicate",
    "/admin/jobs/create", "/admin/jobs/update", "/admin/jobs/delete", "/admin/jobs/duplicate",
    "/admin/companies/create", "/admin/companies/update", "/admin/companies/delete",
    "/admin/users/create", "/admin/users/delete", "/admin/users/role",
    "/admin/applications/delete", "/admin/applications/status",
    "/admin/subscribers/delete",
    "/admin/salaries/create", "/admin/salaries/update", "/admin/salaries/delete",
    "/admin/api/inline-update", "/admin/inbox/action",
    "/admin/settings/save", "/admin/courses/create", "/admin/courses/update", "/admin/courses/delete", "/admin/courses/duplicate",
    "/cms/article/update", "/cms/company/update", "/cms/job/update",
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

def route(conn, method, path, query, payload, user, token, host, client_ip="", csrf_header=""):
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
        cache_ctrl = "public, max-age=31536000, immutable" if ctype and ("javascript" in ctype or "css" in ctype) else "public, max-age=604800"
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
        cache_ctrl = "public, max-age=31536000, immutable" if ctype and ("javascript" in ctype or "css" in ctype) else "public, max-age=604800"
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
                        headers={"Cache-Control": "public, max-age=604800"})

    if path == "/favicon.ico":
        return Response("", status=204, content_type="image/x-icon")

    if path == "/health":
        return json_response({"ok": True, "service": "logistic-waves", "stats": db.counts(conn)})

    if path == "/robots.txt":
        return Response("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n",
                        content_type="text/plain; charset=utf-8")

    if path == "/sitemap.xml":
        return Response(sitemap_xml(conn, host), content_type="application/xml; charset=utf-8")

    # ---------- JSON API ----------
    if path.startswith("/api/"):
        if method in ("POST", "PUT", "PATCH", "DELETE") and user:
            submitted_csrf = csrf_header or (payload.get("_csrf", "") if isinstance(payload, dict) else "")
            if not verify_csrf(token, submitted_csrf):
                return json_response({"ok": False, "error": "Invalid or missing CSRF token."}, status=403)
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
        if m and method == "POST":
            guard = require_login_api(user)
            if guard:
                return guard
            job_id = int(m.group(1))
            if not db.get_job(conn, job_id):
                return json_response({"ok": False, "error": "Job not found."}, status=404)
            state = db.toggle_saved(conn, user["id"], job_id)
            return json_response({"ok": True, "saved": state, "job_id": job_id})

        m = re.match(r"^/api/follow/(\d+)/toggle$", path)
        if m and method == "POST":
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
            if db.consume_rate_limit(conn, f"apply:{user['id']}", 20, 300):
                return json_response({"ok": False, "error": "Too many applications submitted. Please wait a few minutes."}, status=429)
            job_id = int(m.group(1))
            if not db.get_job(conn, job_id):
                return json_response({"ok": False, "error": "Job not found."}, status=404)
            ok, message = db.apply_job(conn, user["id"], job_id, _clip(payload.get("note", ""), 2000))
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
                if db.consume_rate_limit(conn, f"alert:{user['id']}", 20, 300):
                    return json_response({"ok": False, "error": "Too many requests. Please wait a few minutes."}, status=429)
                filters = payload.get("filters") or {}
                if isinstance(filters, str):
                    try:
                        filters = json.loads(filters)
                    except (ValueError, TypeError):
                        filters = {}
                if not isinstance(filters, dict):
                    filters = {}
                alert_id = db.create_alert(conn, user["id"], _clip(payload.get("query", ""), 200),
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
            if db.consume_rate_limit(conn, f"news:{client_ip}", 10, 300):
                return json_response({"ok": False, "error": "Too many requests. Please try again shortly."}, status=429)
            email = _clip(payload.get("email", ""), 254).lower()
            if not _is_valid_email(email):
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
            rl_key = f"login:{client_ip}"
            if db.check_rate_limit(conn, rl_key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS):
                return Response(views.auth_page(kind, next_path,
                                                error="Too many failed login attempts. Please wait 5 minutes and try again."), status=429)
            account = db.authenticate(conn, email, password)
            if not account:
                db.record_rate_limit(conn, rl_key, LOGIN_WINDOW_SECONDS)
                return Response(views.auth_page(kind, next_path,
                                                error="That email or password doesn't match an account."))
            db.clear_rate_limit(conn, rl_key)
            new_token = db.create_session(conn, account["id"])
            destination = safe_next(next_path) if next_path else (
                "/employers" if account.get("role") == "employer" else "/profile"
            )
            return redirect(destination,
                            set_cookies=[(SESSION_COOKIE, new_token, SESSION_MAX_AGE)])
        if db.consume_rate_limit(conn, f"signup:{client_ip}", SIGNUP_MAX_ATTEMPTS, SIGNUP_WINDOW_SECONDS):
            return Response(views.auth_page(kind, next_path,
                                            error="Too many signup attempts. Please wait a few minutes and try again."), status=429)
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

    # CSRF verification for all authenticated state-changing form requests (including /logout)
    if method in ("POST", "PUT", "PATCH", "DELETE") and user and path not in ("/auth/login", "/auth/signup"):
        submitted_csrf = csrf_header or payload.get("_csrf", "")
        if not verify_csrf(token, submitted_csrf):
            body = ("<div style='text-align:center;padding:60px 20px'>"
                    "<h2>Invalid Request</h2>"
                    "<p>Your form submission could not be verified (CSRF token mismatch). "
                    "Please go back and try again.</p>"
                    "<a href='/'>← Back to Home</a></div>")
            return Response(views.layout("Invalid Request", body, user), status=403)

    if path == "/logout":
        if method != "POST":
            return Response("Method not allowed", status=405, content_type="text/plain; charset=utf-8")
        if token:
            db.delete_session(conn, token)
        return redirect("/", clear_cookies=[SESSION_COOKIE])

    # ---------- account pages ----------
    if path in (
        "/tracker", "/saved", "/alerts", "/profile", "/employers/post-job",
        "/alerts/delete", "/alerts/update", "/tracker/delete",
        "/employers/jobs/update", "/employers/jobs/archive", "/employers/applications/status",
    ) and not user:
        return login_required_page(user, path + ("?" + urllib.parse.urlencode(query) if query else ""))

    if path == "/profile":
        if method == "POST":
            db.update_profile(conn, user["id"], _clip(payload.get("name", ""), 120),
                              _clip(payload.get("headline", ""), 160), _clip(payload.get("location", ""), 120))
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
        applicants = db.employer_applications(conn, user["id"]) if user else []
        return Response(views.employers_page(conn, user, posted,
                                             message=query.get("message", ""),
                                             error=query.get("error", ""),
                                             applicants=applicants))

    if path == "/employers/post-job":
        if user.get("role") != "employer":
            return Response(views.employers_page(conn, None), status=403)
        if method == "POST":
            _, err = db.create_job(conn, payload, user["id"])
            if err:
                posted = db.employer_jobs(conn, user["id"])
                applicants = db.employer_applications(conn, user["id"])
                return Response(views.employers_page(conn, user, posted, error=err, applicants=applicants))
            return redirect("/employers?" + urllib.parse.urlencode(
                {"message": "Job published — it now appears in search."}))
        return redirect("/employers#post")

    if path == "/employers/applications/status" and method == "POST":
        if user.get("role") != "employer":
            return Response("Employer access required.", status=403)
        app_id = get_int(payload.get("id"), 0, 0, 10**9)
        status = _clip(payload.get("status", ""), 40)
        if status not in ALLOWED_APP_STATUSES or not db.update_employer_application_status(conn, user["id"], app_id, status):
            return redirect("/employers?" + urllib.parse.urlencode({"error": "Could not update applicant status."}))
        return redirect("/employers?" + urllib.parse.urlencode({"message": f"Applicant updated to {status}."}))

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

    # ---------- frontend CMS inline-modal updates (role-based permissions) ----------
    if path == "/cms/article/update" and method == "POST":
        if not user:
            return Response("Authentication required.", status=403)
        art_id = get_int(payload.get("id", "0"), 0, low=0)
        art_row = conn.execute("SELECT * FROM articles WHERE id=?", (art_id,)).fetchone()
        if not art_row:
            return Response("Article not found.", status=404)
        art_dict = db.as_dict(art_row)
        if not db.can_edit_article(user, art_dict):
            return Response("Forbidden: You do not have permission to edit articles.", status=403)
        slug = art_dict.get("slug") or "article"
        redir = safe_next(payload.get("redirect_to", "")) or f"/articles/{slug}"
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect(redir + ("&" if "?" in redir else "?") + "err=" + urllib.parse.quote("Article title is required (max 300 characters)."))
        category = _clip(payload.get("category", "Maritime & Supply Chain"), 120) or "Maritime & Supply Chain"
        author = _clip(payload.get("author", "Editorial Staff"), 120) or "Editorial Staff"
        tag = _clip(payload.get("tag", "Maritime Insights"), 120) or "Maritime Insights"
        read_time = _clip(payload.get("read_time", "6 min read"), 40) or "6 min read"
        guest = _clip(payload.get("guest", ""), 120)
        duration = _clip(payload.get("duration", ""), 40)
        thumb = _safe_media_url(payload.get("thumb", ""), art_dict.get("thumb") or "")
        excerpt = _clip(payload.get("excerpt", ""), 1000)
        body = _clip(payload.get("body", ""), 200000)
        status = (payload.get("status") or art_dict.get("status") or "published").strip().lower()
        if status not in ("published", "draft", "archived"):
            status = "published"
        conn.execute(
            """UPDATE articles SET title=?, category=?, author=?, tag=?, read_time=?, guest=?, duration=?, thumb=?, excerpt=?, body=?, status=? WHERE id=?""",
            (title, category, author, tag, read_time, guest, duration, thumb, excerpt, body, status, art_id)
        )
        conn.commit()
        status_label = {"published": "published", "draft": "saved as draft", "archived": "archived"}.get(status, "updated")
        return redirect(redir + ("&" if "?" in redir else "?") + "msg=" + urllib.parse.quote(f"Article '{title}' {status_label}!"))

    if path == "/cms/company/update" and method == "POST":
        if not user:
            return Response("Authentication required.", status=403)
        comp_id = get_int(payload.get("id", "0"), 0, low=0)
        comp_row = conn.execute("SELECT * FROM companies WHERE id=?", (comp_id,)).fetchone()
        if not comp_row:
            return Response("Company not found.", status=404)
        comp_dict = db.as_dict(comp_row)
        if not db.can_edit_company(user, comp_dict):
            return Response("Forbidden: You do not have permission to edit this company.", status=403)
        slug = comp_dict.get("slug") or "company"
        redir = safe_next(payload.get("redirect_to", "")) or f"/company/{slug}"
        name = _clip(payload.get("name", ""), 160)
        if not name:
            return redirect(redir + ("&" if "?" in redir else "?") + "err=" + urllib.parse.quote("Company name is required."))
        tagline = _clip(payload.get("tagline", ""), 240)
        industries = _clip(payload.get("industries", "Logistics & Maritime"), 200) or "Logistics & Maritime"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        employees = get_int(payload.get("employees", "1000"), 1000, low=1, high=5000000)
        raw_color = _clip(payload.get("color", "#034f9a"), 20)
        color = raw_color if re.match(r"^#[0-9A-Fa-f]{3,8}$", raw_color) else "#034f9a"
        website = _safe_http_url(payload.get("website", ""))
        description = _clip(payload.get("description", ""), 10000)
        logo_url = _safe_media_url(payload.get("logo_url", ""), "")
        banner_url = _safe_media_url(payload.get("banner_url", ""), "")
        benefits = _clip(payload.get("benefits", str(comp_dict.get("benefits") or "")), 2000)
        offices = _clip(payload.get("offices", str(comp_dict.get("offices") or "")), 2000)
        social_links = _clip(payload.get("social_links", ""), 2000)
        status = (payload.get("status") or comp_dict.get("status") or "published").strip().lower()
        if status not in ("published", "draft", "archived"):
            status = "published"
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "CO"
        conn.execute(
            """UPDATE companies SET name=?, initials=?, tagline=?, industries=?, location=?, employees=?, color=?, website=?, description=?, logo_url=?, banner_url=?, benefits=?, offices=?, social_links=?, status=? WHERE id=?""",
            (name, initials, tagline, industries, location, employees, color, website, description, logo_url, banner_url, benefits, offices, social_links, status, comp_id)
        )
        conn.execute(
            """UPDATE jobs SET company_name=?, company_initials=?, company_color=?, accent=? WHERE company_id=?""",
            (name, initials, color, color, comp_id)
        )
        conn.commit()
        status_label = {"published": "published", "draft": "saved as draft", "archived": "archived"}.get(status, "updated")
        return redirect(redir + ("&" if "?" in redir else "?") + "msg=" + urllib.parse.quote(f"Company '{name}' {status_label}!"))

    if path == "/cms/job/update" and method == "POST":
        if not user:
            return Response("Authentication required.", status=403)
        job_id = get_int(payload.get("id", "0"), 0, low=0)
        job_row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not job_row:
            return Response("Job listing not found.", status=404)
        job_dict = db.as_dict(job_row)
        if not db.can_edit_job(user, job_dict):
            return Response("Forbidden: You do not have permission to edit this job listing.", status=403)
        slug = job_dict.get("slug") or "job"
        redir = safe_next(payload.get("redirect_to", "")) or f"/job/{slug}/{job_id}"
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect(redir + ("&" if "?" in redir else "?") + "err=" + urllib.parse.quote("Job title is required (max 300 characters)."))
        comp_slug = _clip(payload.get("company_slug", job_dict.get("company_slug") or ""), 120)
        category = _clip(payload.get("category", "Engineering & Architecture"), 120) or "Engineering & Architecture"
        workplace = _clip(payload.get("workplace", "Hybrid"), 60) or "Hybrid"
        level = _clip(payload.get("level", "Mid-Senior"), 60) or "Mid-Senior"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        salary_min = get_int(payload.get("salary_min", "50000"), 50000, low=0, high=10000000)
        salary_max = get_int(payload.get("salary_max", "85000"), 85000, low=0, high=10000000)
        if salary_min > salary_max:
            salary_min, salary_max = salary_max, salary_min
        salary_display = _clip(payload.get("salary_display", ""), 80) or f"${salary_min:,} - ${salary_max:,}"
        skills = _clip(payload.get("skills", ""), 500)
        description = _clip(payload.get("description", ""), 20000)
        apply_url = _safe_http_url(payload.get("apply_url", ""))
        apply_email = _clip(payload.get("apply_email", ""), 160)
        raw_status = (payload.get("status") or job_dict.get("status") or "active").strip().lower()
        if raw_status == "published":
            raw_status = "active"
        if raw_status not in ("active", "draft", "archived"):
            raw_status = "active"
        old_cid = job_dict.get("company_id")
        comp = conn.execute("SELECT id, name, initials, color FROM companies WHERE slug=?", (comp_slug,)).fetchone()
        if comp:
            cid, cname, cinit, ccolor = comp
            conn.execute(
                """UPDATE jobs SET title=?, company_id=?, company_slug=?, company_name=?, company_initials=?, company_color=?,
                   category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?, skills=?, description=?,
                   apply_url=?, apply_email=?, is_remote=?, accent=?, status=? WHERE id=?""",
                (title, cid, comp_slug, cname, cinit, ccolor, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 apply_url, apply_email, 1 if "Remote" in workplace else 0, ccolor, raw_status, job_id)
            )
            conn.commit()
            db.sync_company_open_jobs(conn, cid)
            if old_cid and old_cid != cid:
                db.sync_company_open_jobs(conn, old_cid)
        else:
            conn.execute(
                """UPDATE jobs SET title=?, category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?,
                   skills=?, description=?, apply_url=?, apply_email=?, is_remote=?, status=? WHERE id=?""",
                (title, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 apply_url, apply_email, 1 if "Remote" in workplace else 0, raw_status, job_id)
            )
            conn.commit()
        status_label = {"active": "published", "draft": "saved as draft", "archived": "archived"}.get(raw_status, "updated")
        return redirect(redir + ("&" if "?" in redir else "?") + "msg=" + urllib.parse.quote(f"Job '{title}' {status_label}!"))

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

    if path == "/admin/api/inline-update" and method == "POST":
        table = _clip(payload.get("table", ""), 30)
        row_id = get_int(payload.get("id", "0"), 0, low=1)
        field = _clip(payload.get("field", ""), 40)
        val = (payload.get("value") or "").strip()
        allowed = {
            "jobs": {"title": 300, "category": 120, "workplace": 60, "location": 160, "salary_display": 80, "featured": 2, "status": 20},
            "companies": {"name": 160, "industries": 200, "location": 160, "employees": 12, "verified": 2},
            "articles": {"title": 300, "category": 120, "tag": 120, "author": 120},
        }
        if table not in allowed or field not in allowed[table] or not row_id:
            return json_response({"ok": False, "error": "Invalid table, field, or id."}, status=400)
        if field in ("title", "name") and not val:
            return json_response({"ok": False, "error": "Value cannot be empty."}, status=400)
        val = val[:allowed[table][field]]
        if table == "companies" and field == "employees":
            val = get_int(val, 0, low=0, high=10_000_000)
        elif field in ("featured", "verified"):
            val = 1 if str(val) in ("1", "true", "True", "yes") else 0
        elif table == "jobs" and field == "status" and val not in ("active", "pending", "archived", "rejected"):
            return json_response({"ok": False, "error": "Invalid job status."}, status=400)
        if table == "jobs" and field == "workplace":
            conn.execute("UPDATE jobs SET workplace=?, is_remote=? WHERE id=?", (val, 1 if "remote" in val.lower() else 0, row_id))
        else:
            conn.execute(f"UPDATE {table} SET {field}=? WHERE id=?", (val, row_id))
        conn.commit()
        db.log_audit(conn, user.get("email"), f"inline_update:{field}", table, row_id, str(val))
        return json_response({"ok": True})

    if path == "/admin/inbox/action" and method == "POST":
        kind = _clip(payload.get("kind", ""), 20)
        row_id = get_int(payload.get("id", "0"), 0, low=1)
        decision = _clip(payload.get("decision", ""), 20)
        if kind == "job" and row_id and decision in ("approve", "reject"):
            new_st = "active" if decision == "approve" else "rejected"
            conn.execute("UPDATE jobs SET status=? WHERE id=?", (new_st, row_id))
            conn.commit()
            db.log_audit(conn, user.get("email"), f"inbox_{decision}_job", "jobs", row_id, f"status={new_st}")
            return redirect("/admin?tab=inbox&msg=" + urllib.parse.quote(f"Job #{row_id} marked {new_st}."))
        if kind == "company" and row_id and decision in ("approve", "reject"):
            new_ver = 1 if decision == "approve" else 0
            conn.execute("UPDATE companies SET verified=? WHERE id=?", (new_ver, row_id))
            conn.commit()
            db.log_audit(conn, user.get("email"), f"inbox_{decision}_company", "companies", row_id, f"verified={new_ver}")
            return redirect("/admin?tab=inbox&msg=" + urllib.parse.quote(f"Company #{row_id} verification updated."))
        return redirect("/admin?tab=inbox&err=" + urllib.parse.quote("Invalid inbox action."))

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
        title = _clip(payload.get("title", ""), 300)
        if not title:
            return redirect("/admin?tab=videos&err=" + urllib.parse.quote("Episode title is required (max 300 characters)."))
        guest = _clip(payload.get("guest", ""), 120)
        duration = _clip(payload.get("duration", "15:00 min"), 40) or "15:00 min"
        category = _clip(payload.get("category", "Maritime & Tech"), 120) or "Maritime & Tech"
        thumb = _safe_media_url(payload.get("thumb", "") or payload.get("thumb_preset", ""), "/static/images/fw_today_1.jpg")
        excerpt = _clip(payload.get("excerpt", ""), 1000) or f"Exclusive Logistic Waves Today broadcast examining {title}."
        body = _clip(payload.get("body", ""), 200000) or f"Full broadcast editorial analysis for {title} with featured guest {guest}."
        slug = views.slugify(title) or "episode"
        
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
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect("/admin?tab=articles&err=" + urllib.parse.quote("Article title is required (max 300 characters)."))
        category = _clip(payload.get("category", "Maritime & Supply Chain"), 120) or "Maritime & Supply Chain"
        author = _clip(payload.get("author", "Editorial Staff"), 120) or "Editorial Staff"
        tag = _clip(payload.get("tag", "Maritime Insights"), 120) or "Maritime Insights"
        read_time = _clip(payload.get("read_time", "6 min read"), 40) or "6 min read"
        thumb = _safe_media_url(payload.get("thumb", ""), "/static/images/fw_today_1.jpg")
        excerpt = _clip(payload.get("excerpt", ""), 1000)
        body = _clip(payload.get("body", ""), 200000)
        slug = views.slugify(title) or "article"
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
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Article title is required (max 300 characters)."))
        category = _clip(payload.get("category", "Maritime & Supply Chain"), 120) or "Maritime & Supply Chain"
        author = _clip(payload.get("author", "Editorial Staff"), 120) or "Editorial Staff"
        tag = _clip(payload.get("tag", "Maritime Insights"), 120) or "Maritime Insights"
        read_time = _clip(payload.get("read_time", "6 min read"), 40) or "6 min read"
        guest = _clip(payload.get("guest", ""), 120)
        duration = _clip(payload.get("duration", "15:00 min"), 40)
        thumb = _safe_media_url(payload.get("thumb", ""), "")
        excerpt = _clip(payload.get("excerpt", ""), 1000)
        body = _clip(payload.get("body", ""), 200000)
        status = (payload.get("status") or "published").strip().lower()
        if status not in ("published", "draft", "archived"):
            status = "published"
        if art_id:
            conn.execute(
                """UPDATE articles SET title=?, category=?, author=?, tag=?, read_time=?, guest=?, duration=?, thumb=?, excerpt=?, body=?, status=? WHERE id=?""",
                (title, category, author, tag, read_time, guest, duration, thumb, excerpt, body, status, art_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Article '{title}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Article ID not found."))

    if path == "/admin/jobs/create" and method == "POST":
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect("/admin?tab=jobs&err=" + urllib.parse.quote("Job title is required (max 300 characters)."))
        comp_slug = _clip(payload.get("company_slug", ""), 120)
        category = _clip(payload.get("category", "Engineering & Architecture"), 120) or "Engineering & Architecture"
        workplace = _clip(payload.get("workplace", "Hybrid"), 60) or "Hybrid"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        salary_min = get_int(payload.get("salary_min", "50000"), 50000, low=0, high=10000000)
        salary_max = get_int(payload.get("salary_max", "85000"), 85000, low=0, high=10000000)
        if salary_min > salary_max:
            salary_min, salary_max = salary_max, salary_min
        skills = _clip(payload.get("skills", ""), 500)
        description = _clip(payload.get("description", ""), 20000)
        slug = views.slugify(title) or "job"
        
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
            db.sync_company_open_jobs(conn, cid)
            return redirect("/admin?tab=jobs&msg=" + urllib.parse.quote(f"Job listing '{title}' published!"))
        else:
            return redirect("/admin?tab=jobs&err=" + urllib.parse.quote("Selected company not found."))

    if path == "/admin/jobs/delete" and method == "POST":
        job_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "jobs")
        old_row = conn.execute("SELECT company_id FROM jobs WHERE id=?", (job_id,)).fetchone()
        conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        conn.commit()
        if old_row and old_row[0]:
            db.sync_company_open_jobs(conn, old_row[0])
        return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote("Job listing deleted."))

    if path == "/admin/jobs/update" and method == "POST":
        job_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "jobs")
        title = (payload.get("title") or "").strip()
        if not title or len(title) > 300:
            return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Job title is required (max 300 characters)."))
        comp_slug = _clip(payload.get("company_slug", ""), 120)
        category = _clip(payload.get("category", "Engineering & Architecture"), 120) or "Engineering & Architecture"
        workplace = _clip(payload.get("workplace", "Hybrid"), 60) or "Hybrid"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        salary_min = get_int(payload.get("salary_min", "50000"), 50000, low=0, high=10000000)
        salary_max = get_int(payload.get("salary_max", "85000"), 85000, low=0, high=10000000)
        if salary_min > salary_max:
            salary_min, salary_max = salary_max, salary_min
        salary_display = _clip(payload.get("salary_display", ""), 80)
        if not salary_display:
            salary_display = f"${salary_min:,} - ${salary_max:,}"
        skills = _clip(payload.get("skills", ""), 500)
        description = _clip(payload.get("description", ""), 20000)
        level = _clip(payload.get("level", "Mid-Senior"), 60) or "Mid-Senior"
        apply_url = _safe_http_url(payload.get("apply_url", ""))
        apply_email = _clip(payload.get("apply_email", ""), 160)
        raw_status = (payload.get("status") or "active").strip().lower()
        if raw_status == "published":
            raw_status = "active"
        if raw_status not in ("active", "draft", "archived"):
            raw_status = "active"
        
        old_row = conn.execute("SELECT company_id FROM jobs WHERE id=?", (job_id,)).fetchone()
        comp = conn.execute("SELECT id, name, initials, color FROM companies WHERE slug=?", (comp_slug,)).fetchone()
        if comp and job_id:
            cid, cname, cinit, ccolor = comp
            conn.execute(
                """UPDATE jobs SET title=?, company_id=?, company_slug=?, company_name=?, company_initials=?, company_color=?,
                   category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?, skills=?, description=?,
                   apply_url=?, apply_email=?, is_remote=?, accent=?, status=? WHERE id=?""",
                (title, cid, comp_slug, cname, cinit, ccolor, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 apply_url, apply_email, 1 if "Remote" in workplace else 0, ccolor, raw_status, job_id)
            )
            conn.commit()
            db.sync_company_open_jobs(conn, cid)
            if old_row and old_row[0] and old_row[0] != cid:
                db.sync_company_open_jobs(conn, old_row[0])
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Job '{title}' updated successfully!"))
        elif job_id:
            conn.execute(
                """UPDATE jobs SET title=?, category=?, level=?, workplace=?, location=?, salary_min=?, salary_max=?, salary_display=?, skills=?, description=?,
                   apply_url=?, apply_email=?, is_remote=?, status=? WHERE id=?""",
                (title, category, level, workplace, location,
                 salary_min, salary_max, salary_display, skills, description,
                 apply_url, apply_email, 1 if "Remote" in workplace else 0, raw_status, job_id)
            )
            conn.commit()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Job '{title}' updated successfully!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Job ID not found."))

    if path == "/admin/companies/create" and method == "POST":
        name = _clip(payload.get("name", ""), 160)
        if not name:
            return redirect("/admin?tab=companies&err=" + urllib.parse.quote("Company name is required."))
        tagline = _clip(payload.get("tagline", ""), 240)
        industries = _clip(payload.get("industries", "Logistics & Maritime"), 200) or "Logistics & Maritime"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        employees = get_int(payload.get("employees", "1000"), 1000, low=1, high=5000000)
        raw_color = _clip(payload.get("color", "#034f9a"), 20)
        color = raw_color if re.match(r"^#[0-9A-Fa-f]{3,8}$", raw_color) else "#034f9a"
        website = _safe_http_url(payload.get("website", ""))
        description = _clip(payload.get("description", ""), 10000)
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "CO"
        slug = views.slugify(name) or "company"
        
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
        db.delete_company_cascade(conn, comp_id)
        return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote("Company and its listings deleted."))

    if path == "/admin/companies/update" and method == "POST":
        comp_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "companies")
        name = _clip(payload.get("name", ""), 160)
        tagline = _clip(payload.get("tagline", ""), 240)
        industries = _clip(payload.get("industries", "Logistics & Maritime"), 200) or "Logistics & Maritime"
        location = _clip(payload.get("location", "Vietnam"), 160) or "Vietnam"
        employees = get_int(payload.get("employees", "1000"), 1000, low=1, high=5000000)
        raw_color = _clip(payload.get("color", "#034f9a"), 20)
        color = raw_color if re.match(r"^#[0-9A-Fa-f]{3,8}$", raw_color) else "#034f9a"
        website = _safe_http_url(payload.get("website", ""))
        description = _clip(payload.get("description", ""), 10000)
        logo_url = _safe_media_url(payload.get("logo_url", ""), "")
        banner_url = _safe_media_url(payload.get("banner_url", ""), "")
        benefits = _clip(payload.get("benefits", ""), 2000)
        offices = _clip(payload.get("offices", ""), 2000)
        social_links = _clip(payload.get("social_links", ""), 2000)
        status = (payload.get("status") or "published").strip().lower()
        if status not in ("published", "draft", "archived"):
            status = "published"
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "CO"
        
        if comp_id and name:
            conn.execute(
                """UPDATE companies SET name=?, initials=?, tagline=?, industries=?, location=?, employees=?, color=?, website=?, description=?,
                   logo_url=COALESCE(NULLIF(?, ''), logo_url), banner_url=COALESCE(NULLIF(?, ''), banner_url),
                   benefits=COALESCE(NULLIF(?, ''), benefits), offices=COALESCE(NULLIF(?, ''), offices),
                   social_links=COALESCE(NULLIF(?, ''), social_links), status=? WHERE id=?""",
                (name, initials, tagline, industries, location, employees, color, website, description,
                 logo_url, banner_url, benefits, offices, social_links, status, comp_id)
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
        db.delete_user_cascade(conn, uid)
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
        status = _clip(payload.get("status", "Reviewing"), 40)
        if status not in ALLOWED_APP_STATUSES:
            return redirect("/admin?tab=applications&err=" + urllib.parse.quote("Invalid application status."))
        note = _clip(payload.get("note", ""), 2000)
        conn.execute("UPDATE applications SET status=?, note=? WHERE id=?", (status, note, aid))
        conn.commit()
        return redirect("/admin?tab=applications&msg=" + urllib.parse.quote(f"Status updated to {status}."))

    # ---------- admin: subscribers ----------
    if path == "/admin/subscribers/delete" and method == "POST":
        sid = get_int(payload.get("id", "0"), 0, low=0)
        conn.execute("DELETE FROM subscribers WHERE id=?", (sid,))
        conn.commit()
        return redirect("/admin?tab=subscribers&msg=" + urllib.parse.quote("Subscriber removed."))

    # ---------- admin: site settings & hero CMS ----------
    if path == "/admin/settings/save" and method == "POST":
        raw_imgs = payload.get("hero_images_text", "")
        img_list = [ln.strip() for ln in raw_imgs.splitlines() if ln.strip()]
        # Also pick up individual hero_img_1..4 inputs if provided
        slot_imgs = [
            (payload.get(f"hero_img_{i}") or "").strip()
            for i in range(1, 7)
        ]
        slot_imgs = [u for u in slot_imgs if u]
        final_imgs = slot_imgs if slot_imgs else img_list
        if not final_imgs:
            final_imgs = json.loads(db.DEFAULT_SITE_SETTINGS["hero_images"])
        updates = {
            "hero_title_prefix": _clip(payload.get("hero_title_prefix", "Insights for"), 120),
            "hero_title_highlight": _clip(payload.get("hero_title_highlight", "Smarter"), 120),
            "hero_title_suffix": _clip(payload.get("hero_title_suffix", "Logistics"), 120),
            "hero_subtitle": _clip(payload.get("hero_subtitle", ""), 600),
            "hero_primary_label": _clip(payload.get("hero_primary_label", "Explore Insights"), 80),
            "hero_primary_href": _clip(payload.get("hero_primary_href", "/article-blogs"), 200),
            "hero_secondary_label": _clip(payload.get("hero_secondary_label", "Watch Overview"), 80),
            "hero_images": json.dumps(final_imgs),
            "hero_interval_sec": str(get_int(payload.get("hero_interval_sec", "10"), 10, low=3, high=60)),
            "promo_ticker_text": _clip(payload.get("promo_ticker_text", ""), 300),
            "promo_ticker_href": _clip(payload.get("promo_ticker_href", "/jobs"), 200),
            "footer_tagline": _clip(payload.get("footer_tagline", ""), 400),
        }
        db.save_site_settings(conn, updates)
        return redirect("/admin?tab=settings&msg=" + urllib.parse.quote("Live site settings & hero banner saved to database!"))

    # ---------- admin: courses ----------
    if path == "/admin/courses/create" and method == "POST":
        cid = db.create_course(conn, payload)
        if cid:
            return redirect("/admin?tab=courses&msg=" + urllib.parse.quote("Course published to live site!"))
        return redirect("/admin?tab=courses&err=" + urllib.parse.quote("Course title is required."))

    if path == "/admin/courses/update" and method == "POST":
        cid = get_int(payload.get("id", "0"), 0, low=0)
        if db.update_course(conn, cid, payload):
            return redirect("/admin?tab=courses&msg=" + urllib.parse.quote("Course updated!"))
        return redirect("/admin?tab=courses&err=" + urllib.parse.quote("Course ID and title are required."))

    if path == "/admin/courses/delete" and method == "POST":
        cid = get_int(payload.get("id", "0"), 0, low=0)
        db.delete_course(conn, cid)
        return redirect("/admin?tab=courses&msg=" + urllib.parse.quote("Course deleted."))

    if path == "/admin/courses/duplicate" and method == "POST":
        cid = get_int(payload.get("id", "0"), 0, low=0)
        src = conn.execute("SELECT * FROM courses WHERE id=?", (cid,)).fetchone()
        if src:
            d = dict(src)
            new_title = f"{d['title']} (Copy)"
            db.create_course(conn, {
                "title": new_title,
                "channel": d.get("channel") or "Logistics Waves Academy",
                "instructor": d.get("instructor") or "Logistics Waves Faculty",
                "duration": d.get("duration") or "25m",
                "published_date": d.get("published_date") or "Nov 2026",
                "thumb": d.get("thumb") or "/static/images/fw_today_1.svg",
                "description": d.get("description") or "",
                "chapters_json": d.get("chapters_json") or "[]",
            })
            return redirect("/admin?tab=courses&msg=" + urllib.parse.quote(f"Duplicated '{d['title']}' — click Edit to customize!"))
        return redirect("/admin?tab=courses&err=" + urllib.parse.quote("Course not found."))

    if path == "/admin/articles/duplicate" and method == "POST":
        art_id = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "articles")
        src = conn.execute("SELECT * FROM articles WHERE id=?", (art_id,)).fetchone()
        if src:
            d = dict(src)
            new_title = f"{d['title']} (Copy)"
            new_slug = f"{(views.slugify(d['title']) or 'article')[:50]}-copy-{secrets.token_hex(2)}"
            conn.execute(
                """INSERT INTO articles (slug, title, excerpt, body, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    new_slug, new_title, d.get("excerpt") or "", d.get("body") or "",
                    d.get("author") or "Editorial Staff", datetime.utcnow().strftime("%b %d, %Y"),
                    d.get("category") or "Maritime & Supply Chain", d.get("tag") or "Maritime Insights",
                    d.get("read_time") or "6 min read", d.get("accent") or "#034f9a",
                    d.get("thumb") or "/static/images/fw_today_1.jpg",
                    d.get("is_today") or 0, d.get("duration") or "", d.get("guest") or "",
                ),
            )
            conn.commit()
            db.invalidate_cache()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Duplicated '{d['title']}' — click Edit to customize!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Article not found."))

    if path == "/admin/jobs/duplicate" and method == "POST":
        jid = get_int(payload.get("id", "0"), 0, low=0)
        tab = payload.get("tab", "jobs")
        src = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
        if src:
            d = dict(src)
            new_title = f"{d['title']} (Copy)"
            new_slug = f"{(views.slugify(d['title']) or 'job')[:50]}-copy-{secrets.token_hex(2)}"
            conn.execute(
                """INSERT INTO jobs (slug, title, company_id, company_slug, company_name, company_initials, company_color,
                   category, level, workplace, location, salary_min, salary_max, salary_display, industries, skills,
                   description, posted_at, posted_label, is_remote, accent, status, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    new_slug, new_title, d.get("company_id"), d.get("company_slug"), d.get("company_name"),
                    d.get("company_initials"), d.get("company_color"), d.get("category"), d.get("level"),
                    d.get("workplace"), d.get("location"), d.get("salary_min"), d.get("salary_max"),
                    d.get("salary_display"), d.get("industries"), d.get("skills"), d.get("description"),
                    datetime.utcnow().isoformat(timespec="seconds"), "Just now", d.get("is_remote") or 0,
                    d.get("accent") or "#034f9a", "active", user["id"],
                ),
            )
            conn.commit()
            db.invalidate_cache()
            return redirect(f"/admin?tab={tab}&msg=" + urllib.parse.quote(f"Duplicated '{d['title']}' — click Edit to customize!"))
        return redirect(f"/admin?tab={tab}&err=" + urllib.parse.quote("Job not found."))

    # ---------- admin: salaries ----------
    if path == "/admin/salaries/create" and method == "POST":
        title    = _clip(payload.get("title", ""), 200)
        category = _clip(payload.get("category", "Logistics"), 120) or "Logistics"
        median   = get_int(payload.get("median", "80000"), 80000, low=0, high=10000000)
        low      = get_int(payload.get("low", "60000"), 60000, low=0, high=10000000)
        high     = get_int(payload.get("high", "110000"), 110000, low=0, high=10000000)
        if low > high:
            low, high = high, low
        samples  = get_int(payload.get("samples", "500"), 500, low=0, high=10000000)
        trend    = _clip(payload.get("trend", "+2.0%"), 20) or "+2.0%"
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
        title = _clip(payload.get("title", ""), 200)
        category = _clip(payload.get("category", "Logistics"), 120) or "Logistics"
        median = get_int(payload.get("median", "80000"), 80000, low=0, high=10000000)
        low = get_int(payload.get("low", "60000"), 60000, low=0, high=10000000)
        high = get_int(payload.get("high", "110000"), 110000, low=0, high=10000000)
        if low > high:
            low, high = high, low
        samples = get_int(payload.get("samples", "500"), 500, low=0, high=10000000)
        trend = _clip(payload.get("trend", "+2.0%"), 20) or "+2.0%"
        
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
            "About Logistic Waves", "Platform overview",
            "Global logistics intelligence, industry careers, and employer insights in one unified platform.",
            [
                ("What is Logistic Waves?", "Logistic Waves connects supply chain, maritime, freight forwarding, and engineering professionals with vetted employers and industry reporting."),
                ("Core capabilities", "Searchable jobs and company directories, compensation benchmarks, editorial articles, video briefings, candidate application tracking, job alerts, an employer workspace, and an Admin CMS."),
                ("Content management", "All articles, broadcasts, job listings, companies, and salary benchmarks are managed directly from the Admin Dashboard and persisted in the database."),
                ("Tech stack", "Python standard library WSGI server, SQLite / PostgreSQL storage, server-rendered HTML, and responsive vanilla CSS and JavaScript."),
            ], user))
    if path == "/contact":
        return Response(views.simple_page(
            "Contact", "Get in touch",
            "Reach our editorial and employer partnerships team.",
            [
                ("Editorial inquiries", "Submit news tips, supply chain research, or press releases to the Logistic Waves editorial desk."),
                ("Employer support", "Use the Employer Portal or Admin Dashboard to manage company profiles and active job listings."),
                ("Technical issues", "Report broken links or account issues directly to the platform administrator."),
            ], user))
    if path == "/privacy":
        return Response(views.simple_page(
            "Privacy Policy", "Account & data handling",
            "How Logistic Waves stores and protects account activity.",
            [
                ("Account data", "User profiles, saved jobs, applications, and job alerts are stored in the platform database with PBKDF2-HMAC-SHA256 salted password hashes."),
                ("Cookies & security", "A single HttpOnly, SameSite=Lax session cookie keeps you signed in, paired with HMAC-SHA256 CSRF protection on state-changing requests."),
                ("Session control", "You can sign out at any time to invalidate your active session token."),
            ], user))
    if path == "/terms":
        return Response(views.simple_page(
            "Terms of Use", "Platform guidelines",
            "Standard terms governing access to Logistic Waves.",
            [
                ("Authorized use", "Job listings, editorial reports, and salary benchmarks are provided for legitimate career research and recruiting."),
                ("Content ownership", "Companies and editors are responsible for the accuracy of posted job specifications and published articles."),
                ("Availability", "Platform administrators may moderate, archive, or update listings at any time."),
            ], user))

    if path == "/node/add/company":
        return redirect("/employers/post-job")

    return not_found(user, path)


class Handler(BaseHTTPRequestHandler):
    server_version = "LogisticWaves/1.0"
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
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except (TypeError, ValueError):
            raise BadRequestError("Invalid Content-Length header")
        if length < 0:
            raise BadRequestError("Negative Content-Length header")
        if length > MAX_BODY_BYTES:
            raise PayloadTooLargeError("Request payload too large")
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
            is_https = bool(os.environ.get("VERCEL")) or (self.headers.get("X-Forwarded-Proto", "").lower() == "https")
            sec_flag = "; Secure" if is_https else ""
            for name, value, max_age in resp.set_cookies:
                self.send_header("Set-Cookie", f"{name}={value}; Path=/; HttpOnly; SameSite=Lax{sec_flag}; Max-Age={max_age}")
            for name in resp.clear_cookies:
                self.send_header("Set-Cookie", f"{name}=; Path=/; HttpOnly; SameSite=Lax{sec_flag}; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
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
        try:
            payload = self._payload() if self.command in ("POST", "PUT", "PATCH", "DELETE") else {}
        except PayloadTooLargeError:
            self._send(Response("Payload Too Large", status=413, content_type="text/plain; charset=utf-8"))
            return
        except BadRequestError:
            self._send(Response("Bad Request", status=400, content_type="text/plain; charset=utf-8"))
            return
        token = self._cookie_token()
        conn = db.connect()
        try:
            user = db.current_user(conn, token)
            host = self.headers.get("Host", "localhost")
            direct_ip = (self.client_address[0] if self.client_address else "") or ""
            client_ip = _resolve_client_ip(self.headers, direct_ip)
            csrf_header = (self.headers.get("X-CSRF-Token") or "").strip()
            # Set the per-request CSRF token so views can embed it in forms
            views._set_csrf(get_csrf_token(token))
            resp = route(conn, self.command, path, query, payload, user, token, host, client_ip, csrf_header)
            if (
                self.command in ("POST", "PUT", "PATCH", "DELETE")
                and path.startswith(("/admin/", "/employers/", "/api/employer/"))
                and resp.status < 400
            ):
                db.invalidate_cache("home_")
            self._send(resp)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                body = views.layout("Something went wrong",
                                    '<section class="container narrow-page"><div class="empty-state"><h1>Something went wrong</h1><p>An unexpected error occurred while processing your request. Please try again.</p><a class="btn btn-primary" href="/">Back to home</a></div></section>',
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
    print(f"Logistic Waves running at http://0.0.0.0:{PORT}", flush=True)
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
