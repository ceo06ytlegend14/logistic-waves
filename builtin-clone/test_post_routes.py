import urllib.request, urllib.parse

BASE = "http://localhost:8000"

def post(path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(BASE + path, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    req.get_method = lambda: "POST"
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return r.status, r.url
    except urllib.error.HTTPError as ex:
        # 303 redirect is success for POST
        if ex.code == 303:
            return 303, ex.headers.get("Location", "")
        return ex.code, str(ex)
    except Exception as ex:
        return 0, str(ex)

tests = [
    ("/admin/users/create",         {"name": "Test User", "email": "test@test.com", "password": "demo1234", "role": "candidate"}),
    ("/admin/salaries/create",      {"title": "Logistics Analyst", "category": "Logistics & Supply Chain", "median": "75000", "low": "55000", "high": "98000", "samples": "800", "trend": "+2.5%"}),
    ("/admin/applications/status",  {"id": "1", "status": "Reviewing"}),
]

print("=" * 60)
print("POST Route Tests")
print("=" * 60)
for path, data in tests:
    status, loc = post(path, data)
    ok = "OK" if status in (200, 303) else "ERR"
    print(f"  {ok}  {status}  POST {path}")
    if loc:
        print(f"       -> {loc}")
print("=" * 60)
