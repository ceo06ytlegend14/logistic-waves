"""Safe integration checks for public CMS visibility and persistence.

Uses a temporary SQLite database, never the workspace's live ``data/site.db``.
Run from ``builtin-clone`` with: ``python test_cms_sync.py``.
"""
import os
import tempfile
from pathlib import Path

import app
import db


def route(method, path, payload, user, token):
    conn = db.connect()
    try:
        return app.route(
            conn, method, path, {}, payload, user, token, "localhost:8000",
            csrf_header="",
        )
    finally:
        conn.close()


def main():
    old_path = db.DB_PATH
    with tempfile.TemporaryDirectory(prefix="lw-cms-test-") as temp_dir:
        db.DB_PATH = Path(temp_dir) / "site.db"
        try:
            db.init_db()
            conn = db.connect()
            admin_id, error = db.create_user(conn, "CMS Test Admin", "cms-test@example.test", "test-password-123", "admin")
            assert admin_id and not error, error
            token = db.create_session(conn, admin_id)
            user = db.current_user(conn, token)
            csrf = app.get_csrf_token(token)
            conn.close()

            draft = route("POST", "/admin/articles/create", {
                "_csrf": csrf, "title": "Private draft visibility check", "status": "draft",
                "seo_title": "Draft SEO", "seo_description": "Draft description",
            }, user, token)
            assert draft.status == 303
            conn = db.connect()
            row = conn.execute("SELECT * FROM articles WHERE slug=?", ("private-draft-visibility-check",)).fetchone()
            assert row and row["status"] == "draft" and row["seo_title"] == "Draft SEO"
            assert db.get_article(conn, row["slug"]) is None
            assert row["slug"] not in {a["slug"] for a in db.global_search(conn, "visibility")["articles"]}
            conn.close()

            published = route("POST", "/admin/articles/update", {
                "_csrf": csrf, "id": str(row["id"]), "title": row["title"], "status": "published",
                "seo_title": "Published SEO", "seo_description": "Published description",
            }, user, token)
            assert published.status == 303
            conn = db.connect()
            live_article = db.get_article(conn, row["slug"])
            assert live_article and live_article["seo_title"] == "Published SEO"
            conn.close()

            settings = route("POST", "/admin/settings/save", {
                "_csrf": csrf, "hero_title_prefix": "Insights for", "hero_title_highlight": "Smarter",
                "hero_title_suffix": "Logistics", "promo_ticker_text": "CMS announcement check",
                "promo_ticker_href": "/courses", "footer_tagline": "CMS footer tagline check",
            }, user, token)
            assert settings.status == 303
            shell = app.views.layout("Test", "<p>test</p>")
            assert "CMS announcement check" in shell and "CMS footer tagline check" in shell

            conn = db.connect()
            conn.execute("UPDATE companies SET status='draft' WHERE id=(SELECT id FROM companies LIMIT 1)")
            conn.commit()
            company = conn.execute("SELECT slug,name FROM companies WHERE status='draft' LIMIT 1").fetchone()
            assert db.get_company(conn, company["slug"]) is None
            assert company["slug"] not in {c["slug"] for c in db.global_search(conn, company["name"])["companies"]}
            conn.close()
            print("PASS: admin persistence, draft isolation, and public synchronization checks")
        finally:
            db.invalidate_cache()
            db.DB_PATH = old_path


if __name__ == "__main__":
    main()
