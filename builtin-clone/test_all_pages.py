import urllib.request, urllib.parse, urllib.error

BASE = "http://localhost:8000"

pages = [
    # Frontend
    ("GET", "/",             "Homepage"),
    ("GET", "/jobs",         "Jobs"),
    ("GET", "/companies",    "Companies"),
    ("GET", "/article-blogs","Articles"),
    ("GET", "/salaries",     "Salaries"),
    ("GET", "/courses",      "Courses"),
    ("GET", "/search?q=logistics", "Search"),
    # Admin tabs
    ("GET", "/admin",                     "Admin Overview"),
    ("GET", "/admin?tab=videos",          "Admin Videos"),
    ("GET", "/admin?tab=articles",        "Admin Articles"),
    ("GET", "/admin?tab=jobs",            "Admin Jobs"),
    ("GET", "/admin?tab=companies",       "Admin Companies"),
    ("GET", "/admin?tab=users",           "Admin Users"),
    ("GET", "/admin?tab=applications",    "Admin Applications"),
    ("GET", "/admin?tab=subscribers",     "Admin Subscribers"),
    ("GET", "/admin?tab=salaries",        "Admin Salaries"),
    # Auth pages
    ("GET", "/auth/login",   "Login Page"),
    ("GET", "/auth/signup",  "Signup Page"),
]

print("=" * 65)
print(f"{'STATUS':<8} {'SIZE':>8}  {'PAGE'}")
print("=" * 65)
all_ok = True
for method, path, label in pages:
    try:
        req = urllib.request.Request(BASE + path, method=method)
        with urllib.request.urlopen(req, timeout=6) as r:
            body = r.read()
            status = r.status
            size = len(body)
            print(f"  OK {status}  {size:>8} bytes  {label}")
    except urllib.error.HTTPError as ex:
        print(f"  ERR {ex.code}  {'—':>8}        {label}")
        all_ok = False
    except Exception as ex:
        print(f"  ERR  {'—':>8}        {label} — {ex}")
        all_ok = False

print("=" * 65)
print("ALL OK" if all_ok else "SOME ERRORS — check above")
