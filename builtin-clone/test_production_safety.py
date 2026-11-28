"""Production-safety checks that do not require a real database credential."""
import os
import sqlite3
import tempfile
from pathlib import Path

import app
import cloudinary_helper
import db


def main():
    old_path = db.DB_PATH
    with tempfile.TemporaryDirectory(prefix="lw-production-safety-") as temp_dir:
        db.DB_PATH = Path(temp_dir) / "site.db"
        try:
            db.init_db()
            conn = db.connect()
            # Fresh SQLite databases enforce the same essential referential
            # relationships as production PostgreSQL.
            foreign_keys = conn.execute("PRAGMA foreign_key_list(saved_jobs)").fetchall()
            assert len(foreign_keys) == 2
            try:
                conn.execute("INSERT INTO saved_jobs (user_id, job_id, created_at) VALUES (999999, 999999, 'now')")
                conn.commit()
                raise AssertionError("SQLite accepted an orphaned saved job")
            except sqlite3.IntegrityError:
                conn.rollback()
            assert db.global_search(conn, "%' OR 1=1 --", 20) == {"jobs": [], "companies": [], "articles": []}
            conn.close()
        finally:
            db.invalidate_cache()
            db.DB_PATH = old_path

    original = {key: os.environ.get(key) for key in ("VERCEL", "APP_ENV", "DATABASE_URL", "POSTGRES_URL")}
    try:
        os.environ["VERCEL"] = "1"
        os.environ.pop("DATABASE_URL", None)
        os.environ.pop("POSTGRES_URL", None)
        try:
            db.validate_production_environment()
            raise AssertionError("Production accepted a missing persistent database")
        except RuntimeError:
            pass
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    assert not cloudinary_helper.upload_data_uri("data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=")["ok"]
    assert not app.verify_csrf("session", "invalid-token")
    print("PASS: SQLite FK enforcement, SQL input handling, production DB fail-closed, media validation, and CSRF rejection")


if __name__ == "__main__":
    main()
