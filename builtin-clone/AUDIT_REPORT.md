# Logistic Waves CMS and public-site audit

Date: 2026-11-28

## Scope and result

The implementation is a Python standard-library HTTP application backed by SQLite locally and PostgreSQL when `DATABASE_URL`/`POSTGRES_URL` is configured. Public content is server-rendered from the same persistence layer used by the CMS.

I discovered 20 directly testable public entry routes, plus parameterized detail, category, tag, company-tab, salary, job, article, hub, and awards routes. The Admin Dashboard exposes 12 tabs: overview, videos, articles, jobs, companies, users, applications, subscribers, salaries, courses, settings, and inbox. Seven primary public content types are editable: site settings, articles/videos, jobs, companies, salaries, courses, and announcement/footer copy.

| Module | Admin Editable | Database Connected | Live Updated | Test Result |
|---|---|---|---|---|
| Homepage | Pass | Pass | Pass | Pass |
| Jobs | Pass | Pass | Pass | Partial — public smoke only |
| Companies | Pass | Pass | Pass | Partial — draft visibility verified |
| Articles / videos | Pass | Pass | Pass | Pass |
| Courses | Pass | Pass | Pass | Partial — public smoke only |
| Salaries | Pass | Pass | Pass | Partial — public smoke only |
| Navigation / footer | Partial | Pass | Partial | Partial |
| SEO | Articles: Pass; other content: Partial | Pass | Articles: Pass | Pass for articles |

## Fixes completed

- Prevented draft and archived companies/articles from resolving on public detail routes, home editorial sections, Logistic Waves Today, and global search.
- Corrected the search predicates so visibility filters cannot be bypassed by `OR` precedence.
- Completed persistence for the Admin article editor’s publication status, SEO title, meta description, featured flag, and comments flag.
- Added a valid article-status allowlist to inline edits and corrected bulk publishing rules: articles use `published`, while jobs use `active`.
- Completed Admin query projections so article/company editing dialogs receive their existing publication, SEO, media, and related fields rather than silently defaulting them.
- Connected site-wide announcement text/link and footer tagline settings to the shared public layout (including job detail), not only their database form.
- Added an isolated integration test that creates a CMS draft, verifies persistence, verifies that it is hidden from public detail/search, publishes it, verifies live access/SEO persistence, and checks announcement/footer synchronization.

## Verification performed

- `python -m py_compile app.py db.py views.py admin_views.py test_cms_sync.py`
- `python test_cms_sync.py` — passed using a temporary SQLite database; it does not mutate `data/site.db`.
- Public HTTP smoke test — 20 routes returned the expected 200 response and an invalid route returned 404. This included homepage, jobs, companies, salaries, articles, courses, discovery pages, search, static pages, sitemap, robots, and health.
- Asset smoke test — homepage stylesheets returned 200.

## Remaining blockers / recommended follow-up

- Primary navigation labels/links and most footer columns/social links are still code-defined. The CMS now controls the announcement and footer tagline, but a database-backed menu builder is required before the navigation/footer row can be marked fully complete.
- SEO fields are complete for articles. Jobs, companies, courses, salary pages, and global defaults need schema fields and per-record CMS inputs before they can be called fully SEO-managed.
- Courses are managed and reflected live in the course catalogue/player, but they do not have a separate canonical server route per course.
- Image “upload” UI currently supports data URIs/remote URLs and can use Cloudinary when configured. A first-party storage lifecycle (file validation, deletion, replacement cleanup) is not present.
- The schema uses application-managed cascades for critical deletes rather than declared foreign keys. Add foreign-key constraints/migrations before production deployment.
- Existing CSRF checks, HttpOnly/SameSite sessions, role guards, input limits, and rate limits were confirmed in code. Production hardening still needs HTTPS enforcement at the edge, secure secret management, backup/restore policy, rate limiting across instances, and security regression tests.
