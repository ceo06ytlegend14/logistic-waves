"""SQLite storage and query helpers. Standard library only."""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import seed

ROOT = Path(__file__).resolve().parent
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp") / "site.db"
    bundled_db = ROOT / "data" / "site.db"
    if bundled_db.exists():
        if not DB_PATH.exists() or bundled_db.stat().st_mtime > DB_PATH.stat().st_mtime:
            import shutil
            shutil.copyfile(bundled_db, DB_PATH)
else:
    DB_PATH = ROOT / "data" / "site.db" 

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  initials TEXT NOT NULL,
  color TEXT NOT NULL,
  tagline TEXT,
  industries TEXT,
  description TEXT,
  location TEXT,
  employees INTEGER,
  offices INTEGER,
  founded INTEGER,
  benefits INTEGER,
  office_type TEXT,
  remote_policy TEXT,
  hiring_now INTEGER DEFAULT 1,
  open_jobs INTEGER DEFAULT 0,
  website TEXT,
  perks TEXT,
  tech_stack TEXT,
  teams TEXT,
  cover_accent TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY,
  slug TEXT,
  title TEXT NOT NULL,
  company_id INTEGER,
  company_slug TEXT,
  company_name TEXT,
  company_initials TEXT,
  company_color TEXT,
  category TEXT,
  level TEXT,
  workplace TEXT,
  location TEXT,
  salary_min INTEGER,
  salary_max INTEGER,
  salary_display TEXT,
  industries TEXT,
  skills TEXT,
  description TEXT,
  posted_at TEXT,
  posted_label TEXT,
  is_remote INTEGER DEFAULT 0,
  accent TEXT,
  status TEXT DEFAULT 'active',
  created_by INTEGER
);
CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE,
  title TEXT,
  excerpt TEXT,
  body TEXT,
  author TEXT,
  published TEXT,
  category TEXT,
  tag TEXT,
  read_time TEXT,
  accent TEXT,
  thumb TEXT,
  is_today INTEGER DEFAULT 0,
  duration TEXT,
  guest TEXT
);
CREATE TABLE IF NOT EXISTS salaries (
  id INTEGER PRIMARY KEY,
  title TEXT,
  category TEXT,
  median INTEGER,
  low INTEGER,
  high INTEGER,
  samples INTEGER,
  trend TEXT
);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  salt TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'candidate',
  headline TEXT,
  location TEXT,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS saved_jobs (
  user_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  created_at TEXT,
  PRIMARY KEY (user_id, job_id)
);
CREATE TABLE IF NOT EXISTS follows (
  user_id INTEGER NOT NULL,
  company_id INTEGER NOT NULL,
  created_at TEXT,
  PRIMARY KEY (user_id, company_id)
);
CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  status TEXT DEFAULT 'Applied',
  note TEXT,
  created_at TEXT,
  UNIQUE (user_id, job_id)
);
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  query TEXT,
  filters TEXT,
  frequency TEXT DEFAULT 'Daily',
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS demo_seed_state (
  key TEXT PRIMARY KEY,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rate_limits (
  rl_key TEXT NOT NULL,
  ts BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS branches (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  city TEXT,
  country TEXT DEFAULT 'Vietnam',
  address TEXT,
  phone TEXT,
  manager_name TEXT,
  status TEXT DEFAULT 'Active',
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS drivers (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  name TEXT NOT NULL,
  phone TEXT,
  vehicle_type TEXT,
  license_plate TEXT,
  branch_id INTEGER,
  status TEXT DEFAULT 'Available',
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY,
  tracking_code TEXT UNIQUE NOT NULL,
  sender_name TEXT NOT NULL,
  sender_phone TEXT,
  recipient_name TEXT NOT NULL,
  recipient_phone TEXT,
  origin_branch_id INTEGER,
  dest_branch_id INTEGER,
  driver_id INTEGER,
  service_type TEXT DEFAULT 'Express Freight',
  weight_kg REAL DEFAULT 1.0,
  cod_amount INTEGER DEFAULT 0,
  shipping_fee INTEGER DEFAULT 0,
  status TEXT DEFAULT 'Pending',
  notes TEXT,
  created_by INTEGER,
  created_at TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS parcels (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  barcode TEXT UNIQUE NOT NULL,
  description TEXT,
  weight_kg REAL DEFAULT 1.0,
  dimensions TEXT,
  status TEXT DEFAULT 'Pending',
  current_location TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS parcel_events (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  status TEXT NOT NULL,
  location TEXT,
  note TEXT,
  photo_url TEXT,
  created_by INTEGER,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  type TEXT NOT NULL,
  amount INTEGER DEFAULT 0,
  currency TEXT DEFAULT 'VND',
  payment_method TEXT DEFAULT 'COD',
  status TEXT DEFAULT 'Pending',
  reference TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_orders_tracking ON orders(tracking_code);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_parcel_events_order ON parcel_events(order_id);
CREATE INDEX IF NOT EXISTS idx_transactions_order ON transactions(order_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_key_ts ON rate_limits(rl_key, ts);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user ON saved_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_slug);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS idx_jobs_posted ON jobs(posted_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_articles_tag ON articles(tag);
CREATE INDEX IF NOT EXISTS idx_articles_is_today ON articles(is_today);
CREATE INDEX IF NOT EXISTS idx_jobs_workplace ON jobs(workplace);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_remote ON jobs(is_remote);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_token_lookup ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_companies_slug ON companies(slug);
"""



class PgCursor:
    def __init__(self, cur):
        self._cur = cur
        self.lastrowid = None

    def execute(self, sql, params=None):
        pg_sql = sql.replace("?", "%s")
        # PostgreSQL LIKE is case-sensitive whereas SQLite LIKE is case-insensitive
        pg_sql = re.sub(r"\bLIKE\b", "ILIKE", pg_sql, flags=re.I)
        if "INSERT OR IGNORE INTO" in pg_sql.upper():
            pg_sql = re.sub(r'INSERT\s+OR\s+IGNORE\s+INTO', 'INSERT INTO', pg_sql, flags=re.I)
            if "ON CONFLICT" not in pg_sql.upper():
                pg_sql = pg_sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"

        is_insert = pg_sql.strip().upper().startswith("INSERT INTO")
        has_returning = "RETURNING" in pg_sql.upper()

        if is_insert and not has_returning:
            target_tables = ("users", "alerts", "applications", "subscribers", "jobs", "companies", "articles", "salaries", "branches", "drivers", "orders", "parcels", "parcel_events", "transactions")
            for tbl in target_tables:
                if f"into {tbl}" in pg_sql.lower() or f"into \"{tbl}\"" in pg_sql.lower():
                    pg_sql = pg_sql.rstrip().rstrip(";") + " RETURNING id"
                    has_returning = True
                    break

        if params is not None:
            if isinstance(params, list):
                params = tuple(params)
            self._cur.execute(pg_sql, params)
        else:
            self._cur.execute(pg_sql)

        if is_insert and has_returning:
            try:
                row = self._cur.fetchone()
                if row:
                    self.lastrowid = row[0]
            except Exception:
                self.lastrowid = None
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def fetchmany(self, size=None):
        return self._cur.fetchmany(size)

    @property
    def rowcount(self):
        return self._cur.rowcount

    def __iter__(self):
        return iter(self._cur)


class PgConn:
    def __init__(self, raw_conn, pooled=False):
        self._conn = raw_conn
        self._conn.autocommit = True
        self._pooled = pooled

    def cursor(self):
        import psycopg2.extras
        return PgCursor(self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor))

    def execute(self, sql, params=None):
        try:
            cur = self.cursor()
            cur.execute(sql, params)
            return cur
        except Exception as ex:
            # Reconnect once if a pooled serverless connection went stale
            if self._pooled and ex.__class__.__name__ in ("OperationalError", "InterfaceError"):
                db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
                if db_url:
                    import psycopg2
                    global _PG_RAW_CONN
                    _PG_RAW_CONN = psycopg2.connect(db_url, connect_timeout=10)
                    _PG_RAW_CONN.autocommit = True
                    self._conn = _PG_RAW_CONN
                    cur = self.cursor()
                    cur.execute(sql, params)
                    return cur
            raise

    def executemany(self, sql, seq_of_params):
        cur = self.cursor()
        for params in seq_of_params:
            cur.execute(sql, params)
        return cur

    def commit(self):
        pass

    def rollback(self):
        try:
            self._conn.rollback()
        except Exception:
            pass

    def close(self):
        if self._pooled:
            return
        try:
            self._conn.close()
        except Exception:
            pass


_PG_RAW_CONN = None
_TTL_CACHE = {}


def cached_query(key, ttl_seconds, fn):
    """Lightweight in-process TTL cache for read-heavy public catalog queries."""
    import time
    now = time.monotonic()
    entry = _TTL_CACHE.get(key)
    if entry and (now - entry[0]) < ttl_seconds:
        return entry[1]
    val = fn()
    _TTL_CACHE[key] = (now, val)
    return val


def invalidate_cache(prefix=None):
    if prefix is None:
        _TTL_CACHE.clear()
    else:
        for k in list(_TTL_CACHE.keys()):
            if k.startswith(prefix):
                _TTL_CACHE.pop(k, None)


def connect():
    global _PG_RAW_CONN
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if db_url:
        try:
            import psycopg2
            if _PG_RAW_CONN is None or _PG_RAW_CONN.closed:
                _PG_RAW_CONN = psycopg2.connect(db_url, connect_timeout=10)
                _PG_RAW_CONN.autocommit = True
            return PgConn(_PG_RAW_CONN, pooled=True)
        except Exception as e:
            _PG_RAW_CONN = None
            print(f"[db] Warning: Could not connect to PostgreSQL ({e}), falling back to SQLite.")

    if not os.environ.get("VERCEL"):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    else:
        bundled_db = ROOT / "data" / "site.db"
        if bundled_db.exists() and not DB_PATH.exists():
            import shutil
            shutil.copyfile(bundled_db, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-16000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def _now():
    return datetime.utcnow().isoformat(timespec="seconds")


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120000).hex()
    return salt, digest


def verify_password(password, salt, expected):
    _, digest = hash_password(password, salt)
    return hmac.compare_digest(digest, expected)


def _seed(conn):
    now = _now()
    company_ids = {}
    for i, c in enumerate(seed.COMPANIES):
        conn.execute(
            """INSERT INTO companies
               (id, slug, name, initials, color, tagline, industries, description, location,
                employees, offices, founded, benefits, office_type, remote_policy, hiring_now,
                open_jobs, website, perks, tech_stack, teams, cover_accent)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                i + 1, c["slug"], c["name"], c["initials"], c["color"], c["tagline"],
                c["industries"], c["description"], c["location"], c["employees"], c["offices"],
                c["founded"], c["benefits"], c["office_type"], c["remote_policy"], c["hiring_now"],
                c["open_jobs"], c.get("website") or "",
                ",".join(seed.PERKS[: (8 + i % 8)]),
                ",".join(seed.TECH_STACK[i % 5 : i % 5 + 10]),
                ",".join(seed.CATEGORIES[i % 4 : i % 4 + 6]),
                c["color"],
            ),
        )
        company_ids[c["slug"]] = i + 1

    for j in seed.JOBS:
        conn.execute(
            """INSERT INTO jobs
               (id, slug, title, company_id, company_slug, company_name, company_initials,
                company_color, category, level, workplace, location, salary_min, salary_max,
                salary_display, industries, skills, description, posted_at, posted_label,
                is_remote, accent, status, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                j["id"], j["slug"], j["title"], company_ids[j["company_slug"]],
                j["company_slug"], j["company_name"], j["company_initials"],
                j["company_color"], j["category"], j["level"], j["workplace"], j["location"],
                j["salary_min"], j["salary_max"], j["salary_display"], j["industries"],
                j["skills"], j["description"], j["posted_at"], j["posted_label"],
                j["is_remote"], j["accent"], j["status"], None,
            ),
        )

    for i, a in enumerate(seed.ARTICLES):
        conn.execute(
            """INSERT INTO articles
               (id, slug, title, excerpt, body, author, published, category, tag, read_time, accent)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                i + 1, a["slug"], a["title"], a["excerpt"], "\n\n".join(seed.ARTICLE_BODIES),
                a["author"], a["date"], a["category"], a["tag"], a["read_time"], a["accent"],
            ),
        )
    for i, s in enumerate(seed.SALARIES):
        conn.execute(
            "INSERT INTO salaries (id,title,category,median,low,high,samples,trend) VALUES (?,?,?,?,?,?,?,?)",
            (i + 1, s["title"], s["category"], s["median"], s["low"], s["high"], s["samples"], s["trend"]),
        )

    if os.environ.get("ALLOW_DEMO_USERS") == "1":
        demo_pw = os.environ.get("DEMO_USER_PASSWORD") or secrets.token_urlsafe(16)
        demo_users = [
            ("Alex Candidate", "candidate@demo.com", "candidate", "Software Engineer", "Chicago, IL"),
            ("Morgan Employer", "employer@demo.com", "employer", "Talent Leader", "New York, NY"),
        ]
        for i, (name, email, role, headline, location) in enumerate(demo_users):
            salt, digest = hash_password(demo_pw)
            conn.execute(
                "INSERT INTO users (id,name,email,salt,password_hash,role,headline,location,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (i + 1, name, email, salt, digest, role, headline, location, now),
            )
    sync_company_open_jobs(conn)
    conn.commit()


def _sanitize_legacy_placeholders(conn):
    """Remove stale placeholder URLs and legacy editorial labels on existing databases."""
    conn.execute("UPDATE companies SET website='' WHERE lower(website) LIKE ?", ("%example.com%",))
    conn.execute(
        "UPDATE articles SET author='Logistic Waves Editorial' WHERE author IN ('Built In Staff', 'Built In Staff, With AI')"
    )
    conn.execute(
        "UPDATE articles SET title='Logistic Waves Today Live: Port Automation & Space Tech Logistics' WHERE slug='freightwaves-today-live-up-summit' AND title LIKE ?",
        ("FreightWaves Today Live:%",),
    )


_TODAY_EPISODE_SEEDS = [
    (
        "freightwaves-today-live-up-summit",
        "Logistic Waves Today Live: Port Automation & Space Tech Logistics",
        "Join Logistic Waves Today live with industry pioneers at the UP.Summit examining modern autonomous freight and maritime breakthroughs.",
        "Full editorial broadcast analysis for Logistic Waves Today Live: Port Automation & Space Tech Logistics.\n\nFeatured guest Chip Palombini discusses autonomous port cranes, orbital launch supply chains, and next-generation maritime visibility platforms.",
        "Rachel Premack",
        "Nov 5, 2026",
        "Maritime & Tech",
        "Logistic Waves Today",
        "14 min watch",
        "#0084ff",
        "/static/images/fw_today_1.jpg",
        1,
        "14:20 min",
        "Chip Palombini",
    ),
    (
        "flying-taxis-cargo-electric-aviation",
        "Flying Taxis & Cargo: Electric Aviation's Future Takes Off",
        "Electric aviation pioneers showcase eVTOL cargo prototypes and regional delivery aircraft designed to bypass highway freight congestion.",
        "Electric Vertical Takeoff and Landing (eVTOL) aircraft are moving from conceptual test flights to certified commercial freight corridors.\n\nBETA Technologies and regional logistics partners outline battery density gains, FAA certification milestones, and middle-mile cargo economics.",
        "Chip Palombini",
        "Nov 6, 2026",
        "Logistic Waves Today",
        "Logistic Waves Today",
        "18 min watch",
        "#0084ff",
        "/static/images/fw_today_2.jpg",
        1,
        "18:45 min",
        "Chip Palombini",
    ),
    (
        "floridas-space-race-private-sector-boom",
        "Florida's Space Race: 95% Cost Drop Fuels Private Sector Boom",
        "Florida is rapidly becoming the epicenter of the new space race, with groundbreaking public-private partnerships driving down costs and transforming Cape Canaveral freight.",
        "Titusville & Cape Canaveral, Florida — Launch costs to low Earth orbit have dropped by more than 95% over the past decade.\n\nHeavy rocket recovery, maritime barge logistics, and specialized clean-room freight are reshaping port infrastructure across the Space Coast.",
        "Rep. Mike Haridopolos · Space Commerce",
        "Nov 6, 2026",
        "Logistic Waves Today",
        "Logistic Waves Today",
        "19 min watch",
        "#0084ff",
        "/static/images/fw_today_3.jpg",
        1,
        "19:00 min",
        "Rep. Mike Haridopolos",
    ),
    (
        "electric-flying-boat-lands-5-billion",
        "Electric 'Flying Boat' Lands $5 Billion in Orders",
        "REGENT is building electric seagliders that merge the best of boats and planes, flying on a cushion of air over the water to connect coastal ports without runway infrastructure.",
        "North Kingstown, Rhode Island — Maritime mobility startup REGENT has surpassed $5 billion in commercial backorders for its wing-in-ground-effect electric seagliders.\n\nDesigned to serve coastal freight and passenger routes at 180 mph, seagliders dock directly at existing port terminals.",
        "Billy Thalheimer · Maritime Mobility",
        "Nov 6, 2026",
        "Logistic Waves Today",
        "Logistic Waves Today",
        "22 min watch",
        "#0084ff",
        "/static/images/fw_today_4.jpg",
        1,
        "22:00 min",
        "Billy Thalheimer",
    ),
    (
        "autonomous-freight-corridors-commercial-launch",
        "Autonomous Freight Corridors: Texas Triangle Commercial Launch",
        "Driverless Class 8 trucks begin commercial driver-out hauls across I-45 and I-10, demonstrating 99.8% on-time terminal-to-terminal arrival rates.",
        "Dallas & Houston, Texas — Commercial freight transport entered a transformative chapter this week as autonomous Class 8 fleets expanded driverless hub-to-hub operations across the Texas Triangle.\n\nTelematics, radar-lidar fusion, and automated yard handoffs cut dwell time by over 35%.",
        "Marcus Vance · Autonomous Freight",
        "Nov 5, 2026",
        "Logistic Waves Today",
        "Logistic Waves Today",
        "26 min watch",
        "#0084ff",
        "/static/images/fw_today_5.jpg",
        1,
        "26:00 min",
        "Marcus Vance",
    ),
    (
        "decarbonizing-ocean-cargo-methanol-ships",
        "Decarbonizing Ocean Cargo: Dual-Fuel Methanol Containerships",
        "Global shipping alliances accelerate net-zero marine corridors with 12 new green methanol container vessels entering trans-Pacific and Asia-Europe trade lanes.",
        "Singapore & Rotterdam — The decarbonization of global maritime trade reached a critical milestone this month as twelve new dual-fuel green methanol containerships entered scheduled service.\n\nPort bunkering partnerships and digital voyage optimization reduce lifecycle emissions by up to 65%.",
        "Elina Voss · Maritime Supply Chain",
        "Nov 4, 2026",
        "Logistic Waves Today",
        "Logistic Waves Today",
        "21 min watch",
        "#0084ff",
        "/static/images/fw_today_6.jpg",
        1,
        "21:00 min",
        "Elina Voss",
    ),
]


def _ensure_today_episodes(conn):
    """Ensure Logistic Waves Today video episodes exist in articles table."""
    has_today = conn.execute("SELECT 1 FROM articles WHERE is_today = 1 LIMIT 1").fetchone()
    if has_today:
        return
    inserted = False
    for ep in _TODAY_EPISODE_SEEDS:
        if conn.execute("SELECT 1 FROM articles WHERE slug = ?", (ep[0],)).fetchone():
            conn.execute("UPDATE articles SET is_today = 1 WHERE slug = ?", (ep[0],))
            inserted = True
            continue
        conn.execute(
            """INSERT INTO articles
               (slug, title, excerpt, body, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ep,
        )
        inserted = True
    if inserted:
        conn.commit()
        if isinstance(conn, PgConn):
            _sync_pg_sequences(conn)


def _ensure_ops_schema_pg(conn):
    """Ensure Logistics Operations tables exist in PostgreSQL."""
    stmts = [
        """CREATE TABLE IF NOT EXISTS branches (
          id SERIAL PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
          city TEXT, country TEXT DEFAULT 'Vietnam', address TEXT, phone TEXT,
          manager_name TEXT, status TEXT DEFAULT 'Active', created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS drivers (
          id SERIAL PRIMARY KEY, user_id INTEGER, name TEXT NOT NULL, phone TEXT,
          vehicle_type TEXT, license_plate TEXT, branch_id INTEGER,
          status TEXT DEFAULT 'Available', created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS orders (
          id SERIAL PRIMARY KEY, tracking_code TEXT UNIQUE NOT NULL,
          sender_name TEXT NOT NULL, sender_phone TEXT,
          recipient_name TEXT NOT NULL, recipient_phone TEXT,
          origin_branch_id INTEGER, dest_branch_id INTEGER, driver_id INTEGER,
          service_type TEXT DEFAULT 'Express Freight', weight_kg DOUBLE PRECISION DEFAULT 1.0,
          cod_amount INTEGER DEFAULT 0, shipping_fee INTEGER DEFAULT 0,
          status TEXT DEFAULT 'Pending', notes TEXT, created_by INTEGER,
          created_at TEXT, updated_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS parcels (
          id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL, barcode TEXT UNIQUE NOT NULL,
          description TEXT, weight_kg DOUBLE PRECISION DEFAULT 1.0, dimensions TEXT,
          status TEXT DEFAULT 'Pending', current_location TEXT, updated_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS parcel_events (
          id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL, status TEXT NOT NULL,
          location TEXT, note TEXT, photo_url TEXT, created_by INTEGER, created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS transactions (
          id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL, type TEXT NOT NULL,
          amount INTEGER DEFAULT 0, currency TEXT DEFAULT 'VND',
          payment_method TEXT DEFAULT 'COD', status TEXT DEFAULT 'Pending',
          reference TEXT, created_at TEXT
        )""",
        "CREATE INDEX IF NOT EXISTS idx_orders_tracking ON orders(tracking_code)",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
        "CREATE INDEX IF NOT EXISTS idx_parcel_events_order ON parcel_events(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_order ON transactions(order_id)",
    ]
    for s in stmts:
        conn.execute(s)
    conn.commit()


def _ensure_hr_schema_pg(conn):
    """Ensure all core HR / Jobs / Articles / User tables exist in PostgreSQL."""
    stmts = [
        """CREATE TABLE IF NOT EXISTS companies (
          id SERIAL PRIMARY KEY, slug TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
          initials TEXT NOT NULL, color TEXT NOT NULL, tagline TEXT, industries TEXT,
          description TEXT, location TEXT, employees INTEGER, offices INTEGER,
          founded INTEGER, benefits INTEGER, office_type TEXT, remote_policy TEXT,
          hiring_now INTEGER DEFAULT 1, open_jobs INTEGER DEFAULT 0, website TEXT,
          perks TEXT, tech_stack TEXT, teams TEXT, cover_accent TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS jobs (
          id SERIAL PRIMARY KEY, slug TEXT, title TEXT NOT NULL, company_id INTEGER,
          company_slug TEXT, company_name TEXT, company_initials TEXT, company_color TEXT,
          category TEXT, level TEXT, workplace TEXT, location TEXT,
          salary_min INTEGER, salary_max INTEGER, salary_display TEXT,
          industries TEXT, skills TEXT, description TEXT, posted_at TEXT,
          posted_label TEXT, is_remote INTEGER DEFAULT 0, accent TEXT,
          status TEXT DEFAULT 'active', created_by INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS articles (
          id SERIAL PRIMARY KEY, slug TEXT UNIQUE, title TEXT, excerpt TEXT,
          body TEXT, author TEXT, published TEXT, category TEXT, tag TEXT,
          read_time TEXT, accent TEXT, thumb TEXT, is_today INTEGER DEFAULT 0,
          duration TEXT, guest TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS salaries (
          id SERIAL PRIMARY KEY, title TEXT, category TEXT, median INTEGER,
          low INTEGER, high INTEGER, samples INTEGER, trend TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          salt TEXT NOT NULL, password_hash TEXT NOT NULL,
          role TEXT NOT NULL DEFAULT 'candidate', headline TEXT, location TEXT,
          created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS sessions (
          token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires_at TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS saved_jobs (
          user_id INTEGER NOT NULL, job_id INTEGER NOT NULL, created_at TEXT,
          PRIMARY KEY (user_id, job_id)
        )""",
        """CREATE TABLE IF NOT EXISTS follows (
          user_id INTEGER NOT NULL, company_id INTEGER NOT NULL, created_at TEXT,
          PRIMARY KEY (user_id, company_id)
        )""",
        """CREATE TABLE IF NOT EXISTS applications (
          id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, job_id INTEGER NOT NULL,
          status TEXT DEFAULT 'Applied', note TEXT, created_at TEXT,
          UNIQUE (user_id, job_id)
        )""",
        """CREATE TABLE IF NOT EXISTS alerts (
          id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, query TEXT,
          filters TEXT, frequency TEXT DEFAULT 'Daily', created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS subscribers (
          id SERIAL PRIMARY KEY, email TEXT UNIQUE, created_at TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS demo_seed_state (
          key TEXT PRIMARY KEY, created_at TEXT NOT NULL
        )""",
        "CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)",
        "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_saved_jobs_user ON saved_jobs(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_slug)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_posted ON jobs(posted_at)",
        "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_companies_slug ON companies(slug)",
    ]
    for s in stmts:
        conn.execute(s)
    conn.commit()


def _sync_pg_sequences(conn):
    """Ensure PostgreSQL SERIAL sequences are synced past MAX(id) after seeded inserts."""
    for tbl in ("companies", "jobs", "articles", "salaries", "users", "applications", "alerts", "subscribers"):
        try:
            conn.execute(
                f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1), true)"
            )
        except Exception:
            pass
    conn.commit()


def init_db():
    conn = connect()
    if isinstance(conn, PgConn):
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS rate_limits (rl_key TEXT NOT NULL, ts BIGINT NOT NULL)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_key_ts ON rate_limits(rl_key, ts)")
            _ensure_hr_schema_pg(conn)
            if conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
                _seed(conn)
            _sync_pg_sequences(conn)
            admin_email = (os.environ.get("ADMIN_EMAIL") or "admin@logisticwaves.com").strip().lower()
            admin_user = conn.execute("SELECT id FROM users WHERE lower(email)=?", (admin_email,)).fetchone()
            if not admin_user:
                bootstrap_pw = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(18)
                salt, digest = hash_password(bootstrap_pw)
                conn.execute(
                    "INSERT INTO users (name,email,salt,password_hash,role,headline,location,created_at) VALUES (?,?,?,?,?,?,?,?)",
                    ("System Administrator", admin_email, salt, digest, "admin", "Platform Admin", "Ho Chi Minh City, Vietnam", _now()),
                )
                conn.commit()
            seed_workspace_demo_data(conn)
            _sanitize_legacy_placeholders(conn)
            _ensure_today_episodes(conn)
            sync_company_open_jobs(conn)
        except Exception as ex:
            print(f"[db] Pg init warning: {ex}")
        finally:
            conn.close()
        return
    conn.executescript(SCHEMA)
    article_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(articles)").fetchall()
    }
    for column, definition in (
        ("thumb", "TEXT"),
        ("is_today", "INTEGER DEFAULT 0"),
        ("duration", "TEXT"),
        ("guest", "TEXT"),
    ):
        if column not in article_columns:
            # Allowlist guard: only known safe column names allowed
            _SAFE_ARTICLE_COLS = {
                "tag", "reading_time", "duration", "read_time",
                "image_url", "subtitle", "summary", "category",
                "featured", "views", "author_id", "series",
                "thumb", "is_today", "guest",
            }
            if column not in _SAFE_ARTICLE_COLS:
                raise ValueError(f"Disallowed column name: {column!r}")
            conn.execute(f"ALTER TABLE articles ADD COLUMN {column} {definition}")
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
        _seed(conn)
    admin_email = (os.environ.get("ADMIN_EMAIL") or "admin@logisticwaves.com").strip().lower()
    admin_user = conn.execute("SELECT id FROM users WHERE lower(email)=?", (admin_email,)).fetchone()
    if not admin_user:
        bootstrap_pw = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(18)
        salt, digest = hash_password(bootstrap_pw)
        conn.execute(
            "INSERT INTO users (name,email,salt,password_hash,role,headline,location,created_at) VALUES (?,?,?,?,?,?,?,?)",
            ("System Administrator", admin_email, salt, digest, "admin", "Platform Admin", "San Francisco, CA", _now()),
        )
        conn.commit()
        if not os.environ.get("ADMIN_PASSWORD"):
            print(f"[db] Provisioned initial admin '{admin_email}' with generated one-time password.", flush=True)
    # Clean up any legacy accounts
    conn.execute("DELETE FROM users WHERE lower(email)='theancoc69@gmail.com'")
    conn.commit()
    seed_workspace_demo_data(conn)
    _sanitize_legacy_placeholders(conn)
    _ensure_today_episodes(conn)
    sync_company_open_jobs(conn)
    conn.close()


def seed_workspace_demo_data(conn):
    if conn.execute(
        "SELECT 1 FROM demo_seed_state WHERE key='workspace-demo-v1'"
    ).fetchone():
        return
    candidate = conn.execute(
        "SELECT id FROM users WHERE email='candidate@demo.com'"
    ).fetchone()
    employer = conn.execute(
        "SELECT id FROM users WHERE email='employer@demo.com'"
    ).fetchone()
    if not candidate or not employer:
        return
    candidate_id = candidate["id"]
    employer_id = employer["id"]

    if not conn.execute("SELECT 1 FROM saved_jobs WHERE user_id=?", (candidate_id,)).fetchone():
        jobs = conn.execute(
            """SELECT j.id FROM jobs j
               WHERE j.status='active' AND NOT EXISTS (
                 SELECT 1 FROM applications a WHERE a.user_id=? AND a.job_id=j.id
               )
               ORDER BY j.id LIMIT 3""",
            (candidate_id,),
        ).fetchall()
        conn.executemany(
            "INSERT OR IGNORE INTO saved_jobs (user_id,job_id,created_at) VALUES (?,?,?)",
            [(candidate_id, job["id"], _now()) for job in jobs],
        )

    if not conn.execute("SELECT 1 FROM applications WHERE user_id=?", (candidate_id,)).fetchone():
        jobs = conn.execute(
            "SELECT id FROM jobs WHERE status='active' ORDER BY id LIMIT 3"
        ).fetchall()
        statuses = ("Applied", "Interview", "Reviewing")
        notes = (
            "Application sent — tailoring my portfolio for the role.",
            "First interview scheduled with the hiring team.",
            "Recruiter is reviewing my experience.",
        )
        for index, job in enumerate(jobs):
            conn.execute(
                """INSERT OR IGNORE INTO applications
                   (user_id,job_id,status,note,created_at)
                   VALUES (?,?,?,?,date('now',?))""",
                (candidate_id, job["id"], statuses[index], notes[index], f"-{index + 2} days"),
            )
        conn.commit()

    if not conn.execute("SELECT 1 FROM follows WHERE user_id=?", (candidate_id,)).fetchone():
        companies = conn.execute("SELECT id FROM companies ORDER BY id LIMIT 3").fetchall()
        conn.executemany(
            "INSERT OR IGNORE INTO follows (user_id,company_id,created_at) VALUES (?,?,?)",
            [(candidate_id, company["id"], _now()) for company in companies],
        )

    if not conn.execute("SELECT 1 FROM alerts WHERE user_id=?", (candidate_id,)).fetchone():
        conn.executemany(
            """INSERT INTO alerts (user_id,query,filters,frequency,created_at)
               VALUES (?,?,?,?,?)""",
            [
                (candidate_id, "Remote product design", '{"workplace":"Remote"}', "Weekly", _now()),
                (candidate_id, "Senior software engineer", '{"category":"Engineering"}', "Daily", _now()),
            ],
        )

    if not employer_jobs(conn, employer_id):
        examples = [
            {
                "title": "Senior Frontend Engineer",
                "company_slug": "stripe",
                "category": "Engineering",
                "level": "Senior",
                "workplace": "Remote",
                "location": "United States",
                "salary_min": "145",
                "salary_max": "190",
                "skills": "React,TypeScript,Design Systems",
                "description": "Build polished, accessible product experiences for teams moving money around the world.",
            },
            {
                "title": "Product Designer, Platform",
                "company_slug": "figma",
                "category": "Design",
                "level": "Mid level",
                "workplace": "Hybrid",
                "location": "New York, NY",
                "salary_min": "125",
                "salary_max": "165",
                "skills": "Product Design,Prototyping,Research",
                "description": "Shape the tools and workflows that help collaborative teams do their best work.",
            },
        ]
        for example in examples:
            if get_company(conn, example["company_slug"]):
                create_job(conn, example, employer_id)
    conn.execute(
        "INSERT OR IGNORE INTO demo_seed_state (key,created_at) VALUES (?,?)",
        ("workspace-demo-v1", _now()),
    )
    conn.commit()


# ---------- auth ----------

def create_session(conn, user_id):
    token = secrets.token_urlsafe(32)
    expires = (datetime.utcnow() + timedelta(days=30)).isoformat(timespec="seconds")
    conn.execute("INSERT INTO sessions (token,user_id,expires_at) VALUES (?,?,?)", (token, user_id, expires))
    conn.commit()
    # Occasionally clean up expired sessions (1% chance to avoid overhead on every login)
    if secrets.randbelow(100) == 0:
        try:
            conn.execute("DELETE FROM sessions WHERE expires_at < ?", (_now(),))
            conn.commit()
        except Exception:
            pass
    return token


def delete_session(conn, token):
    conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    conn.commit()


def current_user(conn, token):
    if not token:
        return None
    row = conn.execute(
        """SELECT u.id, u.name, u.email, u.role, u.headline, u.location, u.created_at
           FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token=? AND s.expires_at > ?""",
        (token, _now()),
    ).fetchone()
    return dict(row) if row else None


def authenticate(conn, email, password):
    row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip(),)).fetchone()
    if row and verify_password(password, row["salt"], row["password_hash"]):
        return dict(row)
    return None


def create_user(conn, name, email, password, role="candidate", headline="", location=""):
    name = (name or "").strip()[:120]
    email = (email or "").strip().lower()[:254]
    password = password or ""
    if not name:
        return None, "Full name is required."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return None, "Enter a valid email address."
    if conn.execute("SELECT 1 FROM users WHERE lower(email)=?", (email,)).fetchone():
        return None, "An account with that email already exists."
    if len(password) < 6 or len(password) > 128:
        return None, "Password must be between 6 and 128 characters."
    salt, digest = hash_password(password)
    cur = conn.execute(
        "INSERT INTO users (name,email,salt,password_hash,role,headline,location,created_at) VALUES (?,?,?,?,?,?,?,?)",
        (name, email, salt, digest, role, (headline or "").strip()[:160], (location or "").strip()[:120], _now()),
    )
    conn.commit()
    return cur.lastrowid, None


def update_profile(conn, user_id, name, headline, location):
    conn.execute(
        "UPDATE users SET name=?, headline=?, location=? WHERE id=?",
        (name.strip(), headline.strip(), location.strip(), user_id),
    )
    conn.commit()


# ---------- basic getters ----------

def as_dict(row):
    return dict(row) if row else None


def get_company(conn, slug):
    return as_dict(conn.execute("SELECT * FROM companies WHERE slug=?", (slug,)).fetchone())


def get_job(conn, job_id):
    return as_dict(conn.execute("SELECT * FROM jobs WHERE id=? AND status='active'", (job_id,)).fetchone())


def get_article(conn, slug):
    return as_dict(conn.execute("SELECT * FROM articles WHERE slug=?", (slug,)).fetchone())


def get_today_articles(conn, limit=10):
    rows = conn.execute(
        """SELECT * FROM articles
           WHERE is_today=1 OR tag='Logistic Waves Today' OR category='Logistic Waves Today'
           ORDER BY id ASC LIMIT ?""",
        (limit,)
    ).fetchall()
    return [as_dict(r) for r in rows]


def counts(conn):
    r = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM jobs WHERE status='active') as jobs,
            (SELECT COUNT(*) FROM companies) as companies,
            (SELECT COUNT(*) FROM articles) as articles,
            (SELECT COUNT(*) FROM jobs WHERE is_remote=1 AND status='active') as remote,
            (SELECT COUNT(*) FROM users) as users
    """).fetchone()
    return dict(r)


def _where(parts, args):
    return (" WHERE " + " AND ".join(parts)) if parts else "", args


def _escape_like(s):
    """Escape LIKE wildcards in user input to prevent wildcard injection."""
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_jobs(conn, f=None, limit=12, offset=0, user_id=None):
    f = f or {}
    parts, args = ["j.status='active'"], []
    q = (f.get("q") or "").strip()
    if q:
        like = f"%{_escape_like(q)}%"
        parts.append("(j.title LIKE ? ESCAPE '\\' OR j.company_name LIKE ? ESCAPE '\\' OR j.industries LIKE ? ESCAPE '\\' OR j.skills LIKE ? ESCAPE '\\' OR j.description LIKE ? ESCAPE '\\')")
        args += [like, like, like, like, like]
    if f.get("category"):
        parts.append("j.category = ?"); args.append(f["category"])
    if f.get("level"):
        parts.append("j.level = ?"); args.append(f["level"])
    if f.get("workplace"):
        parts.append("(j.workplace = ? OR j.workplace LIKE ?)"); args += [f["workplace"], f"%{f['workplace']}%"]
    if f.get("remote") in ("1", "true", "yes", True, 1):
        parts.append("j.is_remote = 1")
    if f.get("location"):
        parts.append("(j.location LIKE ? OR j.workplace LIKE ?)"); args += [f"%{f['location']}%", f"%{f['location']}%"]
    if f.get("industry"):
        parts.append("j.industries LIKE ?"); args.append(f"%{f['industry']}%")
    if f.get("company_slug"):
        parts.append("j.company_slug = ?"); args.append(f["company_slug"])
    if f.get("posted") in ("24h", "3d", "week", "month"):
        hours = {"24h": 24, "3d": 72, "week": 168, "month": 720}[f["posted"]]
        cutoff = (seed.BASE_DATE - timedelta(hours=hours)).isoformat()
        parts.append("j.posted_at >= ?"); args.append(cutoff)
    where, args = _where(parts, args)
    total = conn.execute("SELECT COUNT(*) FROM jobs j" + where, args).fetchone()[0]
    sort = f.get("sort") or "newest"
    order = {
        "newest": "j.posted_at DESC",
        "oldest": "j.posted_at ASC",
        "salary_high": "j.salary_max DESC, j.posted_at DESC",
        "salary_low": "j.salary_min ASC, j.posted_at DESC",
        "title": "j.title ASC",
        "relevance": "j.posted_at DESC",
    }.get(sort, "j.posted_at DESC")
    rows = conn.execute(
        "SELECT j.* FROM jobs j" + where + " ORDER BY " + order + " LIMIT ? OFFSET ?",
        args + [limit, offset],
    ).fetchall()
    items = [dict(r) for r in rows]
    if user_id and items:
        job_ids = tuple(item["id"] for item in items)
        placeholders = ",".join("?" * len(job_ids))
        saved = {r[0] for r in conn.execute(
            f"SELECT job_id FROM saved_jobs WHERE user_id=? AND job_id IN ({placeholders})",
            (user_id, *job_ids)
        )}
        applied = {r[0] for r in conn.execute(
            f"SELECT job_id FROM applications WHERE user_id=? AND job_id IN ({placeholders})",
            (user_id, *job_ids)
        )}
        for item in items:
            item["saved"] = item["id"] in saved
            item["applied"] = item["id"] in applied
    return items, total


def list_companies(conn, f=None, limit=8, offset=0, user_id=None):
    f = f or {}
    parts, args = ["1=1"], []
    q = (f.get("q") or "").strip()
    if q:
        like = f"%{_escape_like(q)}%"
        parts.append("(c.name LIKE ? ESCAPE '\\' OR c.industries LIKE ? ESCAPE '\\' OR c.description LIKE ? ESCAPE '\\' OR c.tagline LIKE ? ESCAPE '\\')")
        args += [like, like, like, like]
    if f.get("location") and f["location"] not in ("United States", "All Locations", ""):
        parts.append("c.location LIKE ?"); args.append(f"%{f['location']}%")
    if f.get("office_type"):
        parts.append("c.office_type = ?"); args.append(f["office_type"])
    if f.get("industry"):
        parts.append("c.industries LIKE ?"); args.append(f"%{f['industry']}%")
    if f.get("size"):
        ranges = {
            "1 - 10 Employees": (0, 10), "11 - 50 Employees": (11, 50),
            "51 - 200 Employees": (51, 200), "201 - 500 Employees": (201, 500),
            "501 - 1000 Employees": (501, 1000), "1000+ Employees": (1001, 10**9),
        }
        if f["size"] in ranges:
            lo, hi = ranges[f["size"]]
            parts.append("c.employees BETWEEN ? AND ?"); args += [lo, hi]
    if f.get("remote") in ("1", "true", True, 1):
        parts.append("(c.remote_policy LIKE '%Remote%' OR c.office_type='Fully Remote')")
    if f.get("hiring") in ("1", "true", True, 1):
        parts.append("c.hiring_now=1 AND c.open_jobs > 0")
    where, args = _where(parts, args)
    total = conn.execute("SELECT COUNT(*) FROM companies c" + where, args).fetchone()[0]
    rows = conn.execute(
        "SELECT c.* FROM companies c" + where + " ORDER BY c.open_jobs DESC, c.employees DESC LIMIT ? OFFSET ?",
        args + [limit, offset],
    ).fetchall()
    items = [dict(r) for r in rows]
    if user_id:
        followed = {r[0] for r in conn.execute("SELECT company_id FROM follows WHERE user_id=?", (user_id,))}
        for item in items:
            item["followed"] = item["id"] in followed
    return items, total


def list_articles(conn, q="", category="", tag="", limit=20):
    parts, args = ["1=1"], []
    if q:
        like = f"%{_escape_like(q)}%"
        parts.append("(LOWER(title) LIKE LOWER(?) ESCAPE '\\' OR LOWER(excerpt) LIKE LOWER(?) ESCAPE '\\')")
        args += [like, like]
    if category:
        parts.append("LOWER(category) = LOWER(?)"); args.append(category)
    if tag:
        parts.append("LOWER(tag) = LOWER(?)"); args.append(tag)
    where, args = _where(parts, args)
    rows = conn.execute(
        "SELECT id, slug, title, excerpt, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest"
        " FROM articles" + where + " ORDER BY id ASC LIMIT ?",
        args + [limit]
    ).fetchall()
    return [dict(r) for r in rows]


def list_popular_articles(conn, exclude_id=None, limit=8):
    """Return popular articles for sidebar — ordered by id DESC as proxy for recency."""
    if exclude_id:
        rows = conn.execute(
            "SELECT id, slug, title, thumb, category, tag, published, read_time "
            "FROM articles WHERE id != ? ORDER BY id DESC LIMIT ?",
            (exclude_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, slug, title, thumb, category, tag, published, read_time "
            "FROM articles ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def list_salaries(conn, q="", category=""):
    parts, args = ["1=1"], []
    if q:
        parts.append("title LIKE ? ESCAPE '\\'"); args.append(f"%{_escape_like(q)}%")
    if category:
        parts.append("category = ?"); args.append(category)
    where, args = _where(parts, args)
    return [dict(r) for r in conn.execute("SELECT * FROM salaries" + where + " ORDER BY median DESC", args).fetchall()]


def jobs_for_company(conn, company_slug, limit=6):
    rows = conn.execute(
        "SELECT * FROM jobs WHERE company_slug=? AND status='active' ORDER BY posted_at DESC LIMIT ?",
        (company_slug, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def similar_jobs(conn, job, limit=4):
    rows = conn.execute(
        """SELECT * FROM jobs WHERE status='active' AND id<>?
           AND (category=? OR company_slug=?) ORDER BY
           CASE WHEN category=? THEN 0 ELSE 1 END, posted_at DESC LIMIT ?""",
        (job["id"], job["category"], job["company_slug"], job["category"], limit),
    ).fetchall()
    return [dict(r) for r in rows]


def company_job_breakdown(conn, company_slug):
    rows = conn.execute(
        "SELECT category, COUNT(*) AS n FROM jobs WHERE company_slug=? AND status='active' GROUP BY category ORDER BY n DESC LIMIT 5",
        (company_slug,),
    ).fetchall()
    return [dict(r) for r in rows]


# ---------- user actions ----------

def saved_job_ids(conn, user_id):
    return {r[0] for r in conn.execute("SELECT job_id FROM saved_jobs WHERE user_id=?", (user_id,))}


def followed_company_ids(conn, user_id):
    return {r[0] for r in conn.execute("SELECT company_id FROM follows WHERE user_id=?", (user_id,))}


def toggle_saved(conn, user_id, job_id):
    exists = conn.execute("SELECT 1 FROM saved_jobs WHERE user_id=? AND job_id=?", (user_id, job_id)).fetchone()
    if exists:
        conn.execute("DELETE FROM saved_jobs WHERE user_id=? AND job_id=?", (user_id, job_id))
        state = False
    else:
        conn.execute("INSERT INTO saved_jobs (user_id,job_id,created_at) VALUES (?,?,?)", (user_id, job_id, _now()))
        state = True
    conn.commit()
    return state


def toggle_follow(conn, user_id, company_id):
    exists = conn.execute("SELECT 1 FROM follows WHERE user_id=? AND company_id=?", (user_id, company_id)).fetchone()
    if exists:
        conn.execute("DELETE FROM follows WHERE user_id=? AND company_id=?", (user_id, company_id))
        state = False
    else:
        conn.execute("INSERT INTO follows (user_id,company_id,created_at) VALUES (?,?,?)", (user_id, company_id, _now()))
        state = True
    conn.commit()
    return state


def apply_job(conn, user_id, job_id, note=""):
    if conn.execute("SELECT 1 FROM applications WHERE user_id=? AND job_id=?", (user_id, job_id)).fetchone():
        return False, "You already applied to this job."
    conn.execute(
        "INSERT INTO applications (user_id,job_id,status,note,created_at) VALUES (?,?,?,?,?)",
        (user_id, job_id, "Applied", note.strip(), _now()),
    )
    conn.commit()
    return True, "Application submitted."


def list_applications(conn, user_id):
    rows = conn.execute(
        """SELECT a.*, j.title, j.slug AS job_slug, j.company_name, j.company_slug,
                  j.location, j.salary_display, j.workplace
           FROM applications a JOIN jobs j ON j.id=a.job_id
           WHERE a.user_id=? ORDER BY a.created_at DESC""",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_saved_jobs(conn, user_id):
    rows = conn.execute(
        """SELECT j.* FROM saved_jobs s JOIN jobs j ON j.id=s.job_id
           WHERE s.user_id=? AND j.status='active' ORDER BY s.created_at DESC""",
        (user_id,),
    ).fetchall()
    items = [dict(r) for r in rows]
    for item in items:
        item["saved"] = True
    return items


def list_followed_companies(conn, user_id):
    rows = conn.execute(
        "SELECT c.* FROM follows f JOIN companies c ON c.id=f.company_id WHERE f.user_id=? ORDER BY f.created_at DESC",
        (user_id,),
    ).fetchall()
    items = [dict(r) for r in rows]
    for item in items:
        item["followed"] = True
    return items


def list_alerts(conn, user_id):
    return [dict(r) for r in conn.execute("SELECT * FROM alerts WHERE user_id=? ORDER BY created_at DESC", (user_id,))]


def create_alert(conn, user_id, query="", filters=None, frequency="Daily"):
    if not isinstance(query, str) or not query.strip() or frequency not in ("Daily", "Weekly", "Monthly"):
        return None
    cur = conn.execute(
        "INSERT INTO alerts (user_id,query,filters,frequency,created_at) VALUES (?,?,?,?,?)",
        (user_id, query.strip(), json.dumps(filters or {}), frequency, _now()),
    )
    conn.commit()
    return cur.lastrowid


def delete_alert(conn, user_id, alert_id):
    conn.execute("DELETE FROM alerts WHERE id=? AND user_id=?", (alert_id, user_id))
    conn.commit()


def delete_application(conn, user_id, application_id):
    cur = conn.execute(
        "DELETE FROM applications WHERE id=? AND user_id=?",
        (application_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def update_alert(conn, user_id, alert_id, query, frequency):
    if not isinstance(query, str) or frequency not in ("Daily", "Weekly", "Monthly") or not query.strip():
        return False
    cur = conn.execute(
        "UPDATE alerts SET query=?, frequency=? WHERE id=? AND user_id=?",
        (query.strip(), frequency, alert_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def user_stats(conn, user_id):
    r = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM saved_jobs WHERE user_id=?) as saved,
            (SELECT COUNT(*) FROM applications WHERE user_id=?) as applied,
            (SELECT COUNT(*) FROM follows WHERE user_id=?) as following,
            (SELECT COUNT(*) FROM alerts WHERE user_id=?) as alerts
    """, (user_id, user_id, user_id, user_id)).fetchone()
    return dict(r)


def subscribe(conn, email):
    norm_email = email.strip().lower()
    if conn.execute("SELECT 1 FROM subscribers WHERE lower(email)=?", (norm_email,)).fetchone():
        return False, "That email is already subscribed."
    try:
        conn.execute("INSERT INTO subscribers (email,created_at) VALUES (?,?)", (norm_email, _now()))
        conn.commit()
        return True, "You're subscribed."
    except Exception as ex:
        msg = str(ex).lower()
        if isinstance(ex, sqlite3.IntegrityError) or "unique" in msg or "duplicate" in msg:
            return False, "That email is already subscribed."
        raise


def sync_company_open_jobs(conn, company_id=None):
    """Synchronize companies.open_jobs and hiring_now with actual active job counts."""
    if company_id:
        cnt = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE company_id=? AND status='active'",
            (company_id,),
        ).fetchone()[0]
        conn.execute(
            "UPDATE companies SET open_jobs=?, hiring_now=? WHERE id=?",
            (cnt, 1 if cnt > 0 else 0, company_id),
        )
    else:
        conn.execute(
            """UPDATE companies SET
               open_jobs = (SELECT COUNT(*) FROM jobs WHERE jobs.company_id = companies.id AND jobs.status = 'active'),
               hiring_now = CASE WHEN (SELECT COUNT(*) FROM jobs WHERE jobs.company_id = companies.id AND jobs.status = 'active') > 0 THEN 1 ELSE 0 END"""
        )
    conn.commit()


def create_job(conn, data, user_id):
    title = data.get("title", "").strip()
    company_slug = data.get("company_slug", "").strip()
    if not title or not company_slug:
        return None, "Title and company are required."
    company = get_company(conn, company_slug)
    if not company:
        return None, "Choose a company from the list."
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    try:
        smin = max(0, int(data.get("salary_min") or 0))
        smax = max(0, int(data.get("salary_max") or 0))
    except (TypeError, ValueError):
        return None, "Salary must be a whole number."
    if smin and smax and smin > smax:
        return None, "Maximum salary must be greater than minimum salary."
    cur = conn.execute(
        """INSERT INTO jobs
           (slug,title,company_id,company_slug,company_name,company_initials,company_color,
            category,level,workplace,location,salary_min,salary_max,salary_display,industries,
            skills,description,posted_at,posted_label,is_remote,accent,status,created_by)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            slug, title, company["id"], company_slug, company["name"],
            company["initials"], company["color"], data.get("category") or "Engineering",
            data.get("level") or "Mid level", data.get("workplace") or "Hybrid",
            data.get("location") or company["location"], smin, smax,
            f"{smin}K-{smax}K Annually" if smin and smax else "Competitive",
            company["industries"], data.get("skills") or "Collaboration,Communication,Problem Solving",
            data.get("description") or "This is a newly posted role. Add your full job description here.",
            _now(), "Just Now", 1 if "Remote" in (data.get("workplace") or "") else 0,
            company["color"], "active", user_id,
        ),
    )
    next_id = cur.lastrowid
    conn.execute("UPDATE companies SET open_jobs=open_jobs+1, hiring_now=1 WHERE id=?", (company["id"],))
    conn.commit()
    return next_id, None


def employer_jobs(conn, user_id):
    return [dict(r) for r in conn.execute(
        "SELECT * FROM jobs WHERE created_by=? ORDER BY posted_at DESC", (user_id,)
    ).fetchall()]


def employer_applications(conn, employer_id):
    rows = conn.execute(
        """SELECT a.id, a.status, a.note, a.created_at,
                  j.id AS job_id, j.slug AS job_slug, j.title AS job_title, j.company_name,
                  u.name AS candidate_name, u.email AS candidate_email,
                  u.headline AS candidate_headline, u.location AS candidate_location
           FROM applications a
           JOIN jobs j ON j.id = a.job_id
           JOIN users u ON u.id = a.user_id
           WHERE j.created_by=?
           ORDER BY a.created_at DESC""",
        (employer_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def update_employer_application_status(conn, employer_id, app_id, status):
    own = conn.execute(
        """SELECT a.id FROM applications a
           JOIN jobs j ON j.id = a.job_id
           WHERE a.id=? AND j.created_by=?""",
        (app_id, employer_id),
    ).fetchone()
    if not own:
        return False
    conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()
    return True


def update_employer_job(conn, user_id, job_id, data):
    title = data.get("title")
    company_slug = data.get("company_slug")
    title = title.strip() if isinstance(title, str) else ""
    company_slug = company_slug.strip() if isinstance(company_slug, str) else ""
    if not title or not company_slug:
        return False, "Title and company are required."
    company = get_company(conn, company_slug)
    if not company:
        return False, "Choose a company from the list."
    try:
        salary_min = max(0, int(data.get("salary_min") or 0))
        salary_max = max(0, int(data.get("salary_max") or 0))
    except (TypeError, ValueError):
        return False, "Salary must be a whole number."
    if salary_min and salary_max and salary_min > salary_max:
        return False, "Maximum salary must be greater than minimum salary."

    current = conn.execute(
        "SELECT company_id,status FROM jobs WHERE id=? AND created_by=?",
        (job_id, user_id),
    ).fetchone()
    if not current:
        return False, "Job not found."
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    workplace = data.get("workplace")
    workplace = workplace if isinstance(workplace, str) and workplace else "Hybrid"
    location = data.get("location")
    location = location.strip() if isinstance(location, str) else ""
    skills = data.get("skills")
    skills = skills.strip() if isinstance(skills, str) else ""
    description = data.get("description")
    description = description.strip() if isinstance(description, str) else ""
    category = data.get("category")
    category = category if isinstance(category, str) and category else "Engineering"
    level = data.get("level")
    level = level if isinstance(level, str) and level else "Mid level"
    conn.execute(
        """UPDATE jobs SET slug=?,title=?,company_id=?,company_slug=?,company_name=?,
           company_initials=?,company_color=?,category=?,level=?,workplace=?,location=?,
           salary_min=?,salary_max=?,salary_display=?,industries=?,skills=?,description=?,
           is_remote=?,accent=?,status='active'
           WHERE id=? AND created_by=?""",
        (
            slug, title, company["id"], company_slug, company["name"],
            company["initials"], company["color"], category,
            level, workplace, location or company["location"], salary_min, salary_max,
            f"{salary_min}K-{salary_max}K Annually" if salary_min and salary_max else "Competitive",
            company["industries"], skills, description, 1 if "Remote" in workplace else 0,
            company["color"], job_id, user_id,
        ),
    )
    if current["company_id"] != company["id"]:
        if current["status"] == "active":
            conn.execute(
                """UPDATE companies SET open_jobs=CASE WHEN open_jobs > 1 THEN open_jobs-1 ELSE 0 END,
                   hiring_now=CASE WHEN open_jobs<=1 THEN 0 ELSE hiring_now END
                   WHERE id=?""",
                (current["company_id"],),
            )
        conn.execute(
            "UPDATE companies SET open_jobs=open_jobs+1,hiring_now=1 WHERE id=?",
            (company["id"],),
        )
    elif current["status"] != "active":
        conn.execute(
            "UPDATE companies SET open_jobs=open_jobs+1,hiring_now=1 WHERE id=?",
            (company["id"],),
        )
    conn.commit()
    return True, None


def archive_employer_job(conn, user_id, job_id):
    current = conn.execute(
        "SELECT company_id,status FROM jobs WHERE id=? AND created_by=?",
        (job_id, user_id),
    ).fetchone()
    if not current:
        return False
    if current["status"] == "active":
        conn.execute(
            """UPDATE companies SET open_jobs=CASE WHEN open_jobs > 1 THEN open_jobs-1 ELSE 0 END,
               hiring_now=CASE WHEN open_jobs<=1 THEN 0 ELSE hiring_now END
               WHERE id=?""",
            (current["company_id"],),
        )
    conn.execute(
        "UPDATE jobs SET status='closed' WHERE id=? AND created_by=?",
        (job_id, user_id),
    )
    conn.commit()
    return True


def check_rate_limit(conn, rl_key, max_attempts, window_seconds):
    import time
    cutoff = int(time.time()) - int(window_seconds)
    conn.execute("DELETE FROM rate_limits WHERE rl_key=? AND ts < ?", (rl_key, cutoff))
    conn.commit()
    cnt = conn.execute(
        "SELECT COUNT(*) FROM rate_limits WHERE rl_key=? AND ts >= ?",
        (rl_key, cutoff),
    ).fetchone()[0]
    return cnt >= max_attempts


def record_rate_limit(conn, rl_key, window_seconds=3600):
    import time
    now_ts = int(time.time())
    conn.execute("INSERT INTO rate_limits (rl_key, ts) VALUES (?, ?)", (rl_key, now_ts))
    if secrets.randbelow(50) == 0:
        conn.execute("DELETE FROM rate_limits WHERE ts < ?", (now_ts - int(window_seconds),))
    conn.commit()


def consume_rate_limit(conn, rl_key, max_attempts, window_seconds):
    """Return True if rate limit is exceeded; otherwise record attempt and return False."""
    if check_rate_limit(conn, rl_key, max_attempts, window_seconds):
        return True
    record_rate_limit(conn, rl_key, window_seconds)
    return False


def clear_rate_limit(conn, rl_key):
    conn.execute("DELETE FROM rate_limits WHERE rl_key=?", (rl_key,))
    conn.commit()


def delete_user_cascade(conn, uid):
    is_pg = isinstance(conn, PgConn)
    if is_pg:
        conn.execute("BEGIN")
    try:
        conn.execute("DELETE FROM sessions WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM saved_jobs WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM follows WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM applications WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM alerts WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        if is_pg:
            conn.execute("COMMIT")
        else:
            conn.commit()
    except Exception:
        conn.rollback()
        raise


def delete_company_cascade(conn, cid):
    is_pg = isinstance(conn, PgConn)
    if is_pg:
        conn.execute("BEGIN")
    try:
        conn.execute("DELETE FROM follows WHERE company_id=?", (cid,))
        conn.execute("DELETE FROM jobs WHERE company_id=?", (cid,))
        conn.execute("DELETE FROM companies WHERE id=?", (cid,))
        if is_pg:
            conn.execute("COMMIT")
        else:
            conn.commit()
    except Exception:
        conn.rollback()
        raise


def global_search(conn, q, limit=5):
    q = (q or "").strip()
    if not q:
        return {"jobs": [], "companies": [], "articles": []}
    like = f"%{_escape_like(q)}%"
    jobs = [dict(r) for r in conn.execute(
        "SELECT id,slug,title,company_name FROM jobs WHERE status='active' AND (title LIKE ? ESCAPE '\\' OR company_name LIKE ? ESCAPE '\\') ORDER BY posted_at DESC LIMIT ?",
        (like, like, limit),
    ).fetchall()]
    companies = [dict(r) for r in conn.execute(
        "SELECT slug,name,location,color,initials FROM companies WHERE name LIKE ? ESCAPE '\\' OR industries LIKE ? ESCAPE '\\' LIMIT ?",
        (like, like, limit),
    ).fetchall()]
    articles = [dict(r) for r in conn.execute(
        "SELECT slug,title,category FROM articles WHERE title LIKE ? ESCAPE '\\' OR excerpt LIKE ? ESCAPE '\\' LIMIT ?",
        (like, like, limit),
    ).fetchall()]
    return {"jobs": jobs, "companies": companies, "articles": articles}



# ---------- Logistics Operations (Branches, Drivers, Orders, Parcels, Transactions) ----------

def seed_ops_data(conn):
    """Seed initial Vietnam & regional hubs, drivers, orders, parcels, events, and transactions."""
    try:
        if conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0] > 0:
            return
    except Exception:
        return
    now = _now()
    branches_seed = [
        ("SGN-01", "Ho Chi Minh City Port Hub", "Ho Chi Minh City", "Vietnam", "Cat Lai Port Terminal, Thu Duc", "+84 28 3897 6100", "Nguyen Minh Tuan", "Active"),
        ("HAN-01", "Hanoi Northern Logistics Center", "Hanoi", "Vietnam", "Gia Lam Logistics Park, Long Bien", "+84 24 3876 5400", "Tran Thu Ha", "Active"),
        ("HPH-01", "Hai Phong Maritime Gateway", "Hai Phong", "Vietnam", "Dinh Vu Deepwater Port, Hai An", "+84 225 3859 200", "Le Hoang Nam", "Active"),
        ("DAD-01", "Da Nang Central Hub", "Da Nang", "Vietnam", "Lien Chieu Industrial Corridor", "+84 236 3822 100", "Pham Van Khanh", "Active"),
        ("SIN-01", "Singapore Regional Gateway", "Singapore", "Singapore", "Tuas Mega Port Sector 4", "+65 6555 8820", "Daniel Tan", "Active"),
    ]
    for code, name, city, country, addr, phone, mgr, status in branches_seed:
        conn.execute(
            "INSERT OR IGNORE INTO branches (code,name,city,country,address,phone,manager_name,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (code, name, city, country, addr, phone, mgr, status, now),
        )
    branch_map = {r["code"]: r["id"] for r in conn.execute("SELECT id, code FROM branches").fetchall()}

    drivers_seed = [
        ("Nguyen Van Hung", "+84 903 118 402", "2.5T Box Truck", "51C-884.12", branch_map.get("SGN-01"), "On Route"),
        ("Tran Quoc Bao", "+84 912 459 310", "5T Container Van", "29H-441.09", branch_map.get("HAN-01"), "Available"),
        ("Le Duc Anh", "+84 935 772 881", "Express Cargo Van", "43C-219.55", branch_map.get("DAD-01"), "On Route"),
        ("Vo Thanh Long", "+84 908 663 120", "15T Tractor Trailer", "15C-702.44", branch_map.get("HPH-01"), "Available"),
    ]
    for name, phone, vtype, plate, bid, status in drivers_seed:
        conn.execute(
            "INSERT INTO drivers (name,phone,vehicle_type,license_plate,branch_id,status,created_at) VALUES (?,?,?,?,?,?,?)",
            (name, phone, vtype, plate, bid, status, now),
        )
    driver_rows = conn.execute("SELECT id FROM drivers ORDER BY id ASC").fetchall()
    d1 = driver_rows[0]["id"] if len(driver_rows) > 0 else None
    d2 = driver_rows[1]["id"] if len(driver_rows) > 1 else None
    d3 = driver_rows[2]["id"] if len(driver_rows) > 2 else None

    orders_seed = [
        ("LW-2026-8801", "Saigon Newport Logistics", "+84 28 3742 2234", "Viettel Post Hanoi Hub", "+84 24 6266 0306",
         branch_map.get("SGN-01"), branch_map.get("HAN-01"), d1, "Air & Express Freight", 24.5, 4500000, 385000, "In Transit", "Priority electronics & spare parts"),
        ("LW-2026-8802", "Gemadept Cold Chain", "+84 28 3823 6236", "Central Retail Da Nang", "+84 236 3668 900",
         branch_map.get("SGN-01"), branch_map.get("DAD-01"), d3, "Cold Chain Express", 42.0, 0, 520000, "Out for Delivery", "Temperature-controlled 2-8C"),
        ("LW-2026-8803", "Viconship Hai Phong", "+84 225 3836 705", "Thang Long Industrial Park", "+84 24 3881 1200",
         branch_map.get("HPH-01"), branch_map.get("HAN-01"), d2, "Port-to-Door Freight", 18.0, 2100000, 290000, "Delivered", "Signed & verified at Gate B"),
        ("LW-2026-8804", "Pacific Rim Components", "+65 6221 9900", "Thu Duc Hi-Tech Park", "+84 28 3736 0192",
         branch_map.get("SIN-01"), branch_map.get("SGN-01"), None, "Cross-Border Express", 12.4, 0, 640000, "Picked Up", "Customs cleared at Cat Lai"),
    ]
    for code, sname, sphone, rname, rphone, ob, db_id, drv, svc, wt, cod, fee, st, notes in orders_seed:
        cur = conn.execute(
            """INSERT OR IGNORE INTO orders
            (tracking_code,sender_name,sender_phone,recipient_name,recipient_phone,origin_branch_id,dest_branch_id,driver_id,service_type,weight_kg,cod_amount,shipping_fee,status,notes,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code, sname, sphone, rname, rphone, ob, db_id, drv, svc, wt, cod, fee, st, notes, now, now),
        )
        oid = cur.lastrowid
        if not oid:
            row = conn.execute("SELECT id FROM orders WHERE tracking_code=?", (code,)).fetchone()
            oid = row["id"] if row else None
        if oid:
            conn.execute(
                "INSERT OR IGNORE INTO parcels (order_id,barcode,description,weight_kg,dimensions,status,current_location,updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (oid, f"PCL-{code}", notes, wt, "60x40x35 cm", st, "Transit Hub", now),
            )
            conn.execute(
                "INSERT INTO parcel_events (order_id,status,location,note,photo_url,created_at) VALUES (?,?,?,?,?,?)",
                (oid, "Picked Up", "Origin Branch", f"Shipment {code} received and scanned.", "", now),
            )
            if st in ("In Transit", "Out for Delivery", "Delivered"):
                conn.execute(
                    "INSERT INTO parcel_events (order_id,status,location,note,photo_url,created_at) VALUES (?,?,?,?,?,?)",
                    (oid, st, "Regional Transit Hub", f"Updated status to {st}.", "", now),
                )
            conn.execute(
                "INSERT INTO transactions (order_id,type,amount,currency,payment_method,status,reference,created_at) VALUES (?,?,?,?,?,?,?,?)",
                (oid, "Shipping Fee", fee, "VND", "Bank Transfer" if cod == 0 else "COD", "Paid" if st == "Delivered" else "Pending", f"TXN-{code}", now),
            )
            if cod > 0:
                conn.execute(
                    "INSERT INTO transactions (order_id,type,amount,currency,payment_method,status,reference,created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (oid, "COD Collection", cod, "VND", "COD", "Collected" if st == "Delivered" else "Pending", f"COD-{code}", now),
                )
    conn.commit()


def list_branches(conn):
    return [dict(r) for r in conn.execute("SELECT * FROM branches ORDER BY id ASC").fetchall()]


def create_branch(conn, code, name, city, country, address, phone, manager_name):
    now = _now()
    cur = conn.execute(
        "INSERT INTO branches (code,name,city,country,address,phone,manager_name,status,created_at) VALUES (?,?,?,?,?,?,?,'Active',?)",
        (code.strip().upper(), name.strip(), city.strip(), country.strip() or "Vietnam", address.strip(), phone.strip(), manager_name.strip(), now),
    )
    conn.commit()
    return cur.lastrowid


def list_drivers(conn):
    rows = conn.execute(
        """SELECT d.*, b.code AS branch_code, b.name AS branch_name
           FROM drivers d LEFT JOIN branches b ON b.id = d.branch_id
           ORDER BY d.id DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def create_driver(conn, name, phone, vehicle_type, license_plate, branch_id):
    now = _now()
    cur = conn.execute(
        "INSERT INTO drivers (name,phone,vehicle_type,license_plate,branch_id,status,created_at) VALUES (?,?,?,?,?,'Available',?)",
        (name.strip(), phone.strip(), vehicle_type.strip(), license_plate.strip().upper(), branch_id or None, now),
    )
    conn.commit()
    return cur.lastrowid


def update_driver_status(conn, driver_id, status):
    conn.execute("UPDATE drivers SET status=? WHERE id=?", (status, driver_id))
    conn.commit()


def list_orders(conn, q="", status="", driver_id=None):
    where, params = ["1=1"], []
    if q:
        like = f"%{_escape_like(q)}%"
        where.append("(o.tracking_code LIKE ? ESCAPE '\\' OR o.sender_name LIKE ? ESCAPE '\\' OR o.recipient_name LIKE ? ESCAPE '\\')")
        params.extend([like, like, like])
    if status:
        where.append("o.status=?")
        params.append(status)
    if driver_id is not None:
        where.append("o.driver_id=?")
        params.append(driver_id)
    rows = conn.execute(
        f"""SELECT o.*,
                   ob.code AS origin_code, ob.city AS origin_city,
                   db.code AS dest_code, db.city AS dest_city,
                   d.name AS driver_name, d.vehicle_type AS driver_vehicle, d.license_plate AS driver_plate
            FROM orders o
            LEFT JOIN branches ob ON ob.id = o.origin_branch_id
            LEFT JOIN branches db ON db.id = o.dest_branch_id
            LEFT JOIN drivers d ON d.id = o.driver_id
            WHERE {' AND '.join(where)}
            ORDER BY o.id DESC""",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def get_order_by_tracking(conn, tracking_code):
    code = (tracking_code or "").strip().upper()
    if not code:
        return None
    row = conn.execute(
        """SELECT o.*,
                  ob.code AS origin_code, ob.name AS origin_name, ob.city AS origin_city,
                  db.code AS dest_code, db.name AS dest_name, db.city AS dest_city,
                  d.name AS driver_name, d.phone AS driver_phone, d.vehicle_type AS driver_vehicle, d.license_plate AS driver_plate
           FROM orders o
           LEFT JOIN branches ob ON ob.id = o.origin_branch_id
           LEFT JOIN branches db ON db.id = o.dest_branch_id
           LEFT JOIN drivers d ON d.id = o.driver_id
           WHERE upper(o.tracking_code)=?""",
        (code,),
    ).fetchone()
    if not row:
        return None
    order = dict(row)
    order["parcels"] = [dict(r) for r in conn.execute("SELECT * FROM parcels WHERE order_id=? ORDER BY id ASC", (order["id"],)).fetchall()]
    order["events"] = [dict(r) for r in conn.execute("SELECT * FROM parcel_events WHERE order_id=? ORDER BY id DESC", (order["id"],)).fetchall()]
    order["transactions"] = [dict(r) for r in conn.execute("SELECT * FROM transactions WHERE order_id=? ORDER BY id DESC", (order["id"],)).fetchall()]
    return order


def create_order(conn, data, user_id=None):
    now = _now()
    code = (data.get("tracking_code") or "").strip().upper()
    if not code:
        code = f"LW-2026-{secrets.randbelow(9000) + 1000}"
    weight = float(data.get("weight_kg") or 1.0)
    cod = int(data.get("cod_amount") or 0)
    fee = int(data.get("shipping_fee") or max(50000, int(weight * 25000)))
    cur = conn.execute(
        """INSERT INTO orders
        (tracking_code,sender_name,sender_phone,recipient_name,recipient_phone,origin_branch_id,dest_branch_id,driver_id,service_type,weight_kg,cod_amount,shipping_fee,status,notes,created_by,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'Pending',?,?,?,?)""",
        (
            code,
            data["sender_name"].strip(),
            (data.get("sender_phone") or "").strip(),
            data["recipient_name"].strip(),
            (data.get("recipient_phone") or "").strip(),
            data.get("origin_branch_id") or None,
            data.get("dest_branch_id") or None,
            data.get("driver_id") or None,
            (data.get("service_type") or "Express Freight").strip(),
            weight,
            cod,
            fee,
            (data.get("notes") or "").strip(),
            user_id,
            now,
            now,
        ),
    )
    oid = cur.lastrowid
    conn.execute(
        "INSERT INTO parcels (order_id,barcode,description,weight_kg,dimensions,status,current_location,updated_at) VALUES (?,?,?,?,?,'Pending',?,?)",
        (oid, f"PCL-{code}", (data.get("notes") or "Standard Parcel").strip(), weight, (data.get("dimensions") or "40x30x25 cm").strip(), "Origin Branch", now),
    )
    conn.execute(
        "INSERT INTO parcel_events (order_id,status,location,note,photo_url,created_by,created_at) VALUES (?,?,?,?,?,?,?)",
        (oid, "Pending", "Origin Branch", f"Order {code} created.", (data.get("photo_url") or "").strip(), user_id, now),
    )
    conn.execute(
        "INSERT INTO transactions (order_id,type,amount,currency,payment_method,status,reference,created_at) VALUES (?,?,?,?,?,?,?,?)",
        (oid, "Shipping Fee", fee, "VND", "COD" if cod > 0 else "Bank Transfer", "Pending", f"TXN-{code}", now),
    )
    if cod > 0:
        conn.execute(
            "INSERT INTO transactions (order_id,type,amount,currency,payment_method,status,reference,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (oid, "COD Collection", cod, "VND", "COD", "Pending", f"COD-{code}", now),
        )
    conn.commit()
    return oid, code


def update_order_status(conn, order_id, status, location="", note="", photo_url="", driver_id=None, user_id=None):
    now = _now()
    if driver_id is not None:
        conn.execute("UPDATE orders SET status=?, driver_id=?, updated_at=? WHERE id=?", (status, driver_id or None, now, order_id))
    else:
        conn.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?", (status, now, order_id))
    conn.execute("UPDATE parcels SET status=?, current_location=?, updated_at=? WHERE order_id=?", (status, location or status, now, order_id))
    conn.execute(
        "INSERT INTO parcel_events (order_id,status,location,note,photo_url,created_by,created_at) VALUES (?,?,?,?,?,?,?)",
        (order_id, status, location or "Logistics Hub", note or f"Status updated to {status}.", photo_url or "", user_id, now),
    )
    if status == "Delivered":
        conn.execute("UPDATE transactions SET status='Paid' WHERE order_id=? AND type='Shipping Fee'", (order_id,))
        conn.execute("UPDATE transactions SET status='Collected' WHERE order_id=? AND type='COD Collection'", (order_id,))
    conn.commit()


def list_transactions(conn, limit=50):
    rows = conn.execute(
        """SELECT t.*, o.tracking_code, o.sender_name, o.recipient_name
           FROM transactions t
           LEFT JOIN orders o ON o.id = t.order_id
           ORDER BY t.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def ops_stats(conn):
    return {
        "branches": conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0],
        "drivers": conn.execute("SELECT COUNT(*) FROM drivers").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "in_transit": conn.execute("SELECT COUNT(*) FROM orders WHERE status IN ('Picked Up','In Transit','Out for Delivery')").fetchone()[0],
        "delivered": conn.execute("SELECT COUNT(*) FROM orders WHERE status='Delivered'").fetchone()[0],
        "revenue_vnd": conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='Shipping Fee'").fetchone()[0],
        "cod_vnd": conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='COD Collection'").fetchone()[0],
    }
