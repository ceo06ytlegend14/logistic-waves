# Logistic Waves production-readiness audit

Audited: 2026-11-28. This report distinguishes local, isolated verification from production verification. No secrets or production records were read, written, or deleted.

| Category | Status | Evidence |
|---|---|---|
| PostgreSQL production verification | **FAIL — blocked** | `DATABASE_URL` and `POSTGRES_URL` are not set in the available runtime. A real PostgreSQL connection, migration, concurrency, and restore test cannot be truthfully run. |
| Database integrity / development SQLite | **PASS (local)** | Fresh SQLite now enforces essential foreign keys; orphan-insert rejection was tested. PostgreSQL constraints are installed idempotently during initialization after orphan checks. |
| Security controls | **PARTIAL** | Server-side admin role guards, PBKDF2 hashes, HttpOnly/SameSite cookies, CSRF validation, rate limiting, CSP/HSTS headers, and fail-closed media validation were verified. A real dependency/CVE scan and deployed HTTPS test still require CI/deployment access. |
| Backup / recovery | **PARTIAL** | A verified `pg_dump`/`pg_restore --list` script with 30-day retention was added. It is not automated until an operator schedules it and supplies a protected database URL. Media backup needs a Cloudinary export/retention policy. |
| Media management | **PARTIAL** | The server accepts only PNG/JPEG/WEBP/GIF data after base64, size (5 MB), and magic-byte validation; production refuses embedded image data and uses Cloudinary. Cloudinary credentials are not configured, so a real upload/replacement/recovery test was not possible. |
| CMS completion | **FAIL — incomplete** | Article SEO and homepage announcement/footer tagline are stored. Database-backed primary navigation/full footer menus and per-record SEO for jobs, companies, courses, and salaries remain unimplemented. |
| Performance / responsiveness | **PARTIAL** | Existing pagination, indexes, static caching, and in-process invalidation were inspected. No load test or device-browser test was run against production. |
| Deployment verification | **FAIL — blocked** | Vercel configuration and Python entrypoint exist, but deployed environment values and production health endpoint cannot be verified. The application now refuses Vercel/production startup without PostgreSQL, preventing unsafe ephemeral SQLite deployments. |

## Fixes completed in this audit

- Added a production guard: Vercel/`APP_ENV=production` requires `DATABASE_URL` or `POSTGRES_URL`; PostgreSQL connection failure cannot silently fall back to SQLite.
- Completed PostgreSQL DDL for `site_settings` and `courses`, which were previously absent from the PostgreSQL migration path.
- Added idempotent PostgreSQL foreign-key migration plus pre-migration orphan checks for jobs, sessions, saved jobs, follows, applications, and alerts.
- Added matching core foreign-key declarations for fresh SQLite development databases.
- Added a protected Admin media upload endpoint backed by Cloudinary. It validates MIME, base64 format, magic bytes, and a 5 MB decoded-size limit. SVG uploads are rejected; production no longer persists embedded base64 media.
- Added the tested backup script: `scripts/backup_postgres.ps1`.

## Commands executed

```powershell
python -m py_compile app.py db.py cloudinary_helper.py test_production_safety.py
python test_production_safety.py
python test_cms_sync.py
git diff --check
```

Observed results:

```text
PASS: SQLite FK enforcement, SQL input handling, production DB fail-closed,
media validation, and CSRF rejection
PASS: admin persistence, draft isolation, and public synchronization checks
```

## Production deployment steps

1. Provision managed PostgreSQL with TLS and a least-privilege application role.
2. Configure Vercel Production environment variables (never commit them): `DATABASE_URL` or `POSTGRES_URL`, `CSRF_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`. Use a long random `CSRF_SECRET`; do not rely on a generated local file in serverless production.
3. Deploy once to a staging project, then invoke `/health`. The first startup runs schema initialization and foreign-key migration. If orphaned legacy data exists, startup fails with the affected relationship instead of masking corruption.
4. Perform a staging smoke test: sign in as admin; create/update/publish/draft an article, company, job, course, and salary; upload a PNG/JPEG/WEBP; verify public routes; and test an invalid CSRF POST returns 403.
5. From a secured backup runner with PostgreSQL client tools, schedule this daily command (for example with Task Scheduler or CI):

```powershell
& .\scripts\backup_postgres.ps1 -BackupDirectory 'D:\secure-backups\logistic-waves' -RetentionDays 30
```

6. Monthly, restore a recent dump to a fresh non-production database and run `pg_restore --clean --if-exists --dbname $env:STAGING_DATABASE_URL <backup-file>`. Verify `/health`, admin login, and a representative public route.
7. Configure Cloudinary asset backup/export retention separately. Keep a documented mapping of the Cloudinary folder (`logistic-waves`) and the database backup date; do not delete an asset until no database record references it.
8. Only after the staging checks pass, promote the same immutable deployment to production. Keep the prior deployment available for Vercel rollback.

## Remaining launch blockers

- No PostgreSQL URL is configured in this environment; therefore database migration, connection, transaction-concurrency, backup, restore, and deployment behavior have not been tested against a real PostgreSQL instance.
- No Cloudinary credentials are configured; uploads will correctly return a configuration error in production until they are set.
- Navigation/footer menu management and SEO controls beyond articles are still incomplete.
- The backup script has not been scheduled or restore-tested against a managed PostgreSQL instance.
- Add dependency/CVE scanning and a production load/browser test to CI before launch.
