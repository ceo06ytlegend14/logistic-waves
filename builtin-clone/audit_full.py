import sqlite3, json, os, sys

conn = sqlite3.connect('data/site.db')
conn.row_factory = sqlite3.Row

print("=" * 60)
print("DB TABLE COUNTS")
print("=" * 60)
for t in ['articles','jobs','companies','users','applications','subscribers','alerts','salaries','sessions','saved_jobs','follows']:
    try:
        n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        print(f"  {t:20s}: {n}")
    except Exception as e:
        print(f"  {t:20s}: ERROR - {e}")

print()
print("=" * 60)
print("USERS (first 10)")
print("=" * 60)
try:
    users = [dict(r) for r in conn.execute('SELECT id, name, email, role FROM users ORDER BY id DESC LIMIT 10').fetchall()]
    for u in users:
        print(f"  [{u['id']}] {u['name']} | {u['email']} | role={u['role']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("APPLICATIONS (first 10)")
print("=" * 60)
try:
    apps = conn.execute('''
        SELECT a.id, a.status, a.note, a.created_at,
               j.title as job_title, u.name as user_name, u.email
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.id
        ORDER BY a.id DESC LIMIT 10
    ''').fetchall()
    for a in apps:
        print(f"  [{a['id']}] {a['user_name']} -> {a['job_title']} | status={a['status']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("SUBSCRIBERS (first 10)")
print("=" * 60)
try:
    subs = [dict(r) for r in conn.execute('SELECT id, email, created_at FROM subscribers ORDER BY id DESC LIMIT 10').fetchall()]
    for s in subs:
        print(f"  [{s['id']}] {s['email']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("SALARIES (first 10)")
print("=" * 60)
try:
    sals = [dict(r) for r in conn.execute('SELECT * FROM salaries ORDER BY id DESC LIMIT 10').fetchall()]
    if sals:
        print(f"  Columns: {list(sals[0].keys())}")
        for s in sals:
            print(f"  {s}")
    else:
        print("  EMPTY - no salary data")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("ARTICLES SCHEMA")
print("=" * 60)
try:
    info = conn.execute("PRAGMA table_info(articles)").fetchall()
    for col in info:
        print(f"  {col['name']:20s} {col['type']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("JOBS SCHEMA")
print("=" * 60)
try:
    info = conn.execute("PRAGMA table_info(jobs)").fetchall()
    for col in info:
        print(f"  {col['name']:20s} {col['type']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("COMPANIES SCHEMA")
print("=" * 60)
try:
    info = conn.execute("PRAGMA table_info(companies)").fetchall()
    for col in info:
        print(f"  {col['name']:20s} {col['type']}")
except Exception as e:
    print("  ERROR:", e)

print()
print("=" * 60)
print("ALERTS (first 5)")
print("=" * 60)
try:
    alerts = [dict(r) for r in conn.execute('SELECT * FROM alerts LIMIT 5').fetchall()]
    if alerts:
        print(f"  Columns: {list(alerts[0].keys())}")
        for a in alerts:
            print(f"  {a}")
    else:
        print("  EMPTY")
except Exception as e:
    print("  ERROR:", e)

conn.close()

print()
print("=" * 60)
print("STATIC FILES")
print("=" * 60)
static_dir = 'static'
for f in os.listdir(static_dir):
    size = os.path.getsize(os.path.join(static_dir, f))
    print(f"  {f:40s} {size:>8} bytes")

print()
print("=" * 60)
print("VIEWS.PY SIZE & KEY FUNCTIONS")
print("=" * 60)
with open('views.py', 'r', encoding='utf-8') as f:
    content = f.read()
lines = content.split('\n')
print(f"  Total lines: {len(lines)}")
funcs = [l.strip() for l in lines if l.startswith('def ')]
for fn in funcs:
    print(f"  {fn}")

print()
print("=" * 60)
print("APP.PY ROUTES")
print("=" * 60)
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()
app_lines = app_content.split('\n')
print(f"  Total lines: {len(app_lines)}")
routes = [l.strip() for l in app_lines if ('path ==' in l or "path.startswith" in l) and ('"""' not in l and "'''" not in l)]
for r in routes[:40]:
    print(f"  {r}")
