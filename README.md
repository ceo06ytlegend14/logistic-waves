# Built In-style website clone (full-stack demo)

A self-contained, working clone of the public information architecture and visual style of [builtin.com](https://builtin.com/), built in the workspace with a live preview on port **8000**.

> This is an independent demo for learning and prototyping. It is **not affiliated with Built In**. Company marks, photos and editorial copy are placeholders; no assets were copied from the live site.

## Brand Logo Standards (MANDATORY DESIGN RULE)

> **CRITICAL REQUIREMENT -- DO NOT VIOLATE IN ANY FUTURE BUILD:**
>
> 1. **Universal Default Size (84px x 84px)**:
>    - All company and brand logos throughout the entire website MUST be sized at exactly **`84px x 84px`** (`width: 84px; height: 84px;`).
>    - This matches the standard design established on `http://localhost:8000/jobs`.
>    - Function default: `company_logo(company, size=84, extra="")`.
>
> 2. **NO Background & NO Border Behind Brands**:
>    - Brand logos (especially SVG / PNG marks like Viconship, General Motors, Adidas, etc.) must strictly have **NO background** (`background: transparent !important;`) and **NO border** (`border: none !important; box-shadow: none !important; padding: 0 !important;`).
>    - Brand marks must NEVER be enclosed within a white box, gray outline, or padded square container.
>    - The logo SVG / image sits cleanly on the card / page background.
>    - Fallback letter tiles use borderless colored tiles (`border: none; box-shadow: none;`).
>
> 3. **Applies Across All Pages & Components**:
>    - `/jobs` (Job board listing cards)
>    - `/` (Homepage: Best Tech Jobs cards, Company Directory rows, Latest Opportunities cards, Hero cards)
>    - `/companies` (Company directory cards and avatar blocks)
>    - `/company/<slug>` (Company profile header, cover logos, open jobs, and similar company cards)
>    - `/job/<slug>/<id>` (Job detail flagship hero logo box and sidebar employer cards)
>    - Search results, hub cards, and following company lists.
>
> 4. **Enforcing Classes**:
>    - `.company-logo`, `.brand-img-logo`, `.best-job-logo`, `.dir-logo-box`, `.opp-company-logo`, `.flagship-logo-box`, `#hero-logo-box`, `.li-avatar`, `.cover-logo`, `.li-profile-logo`, `.li-side-logo`.


## Run it

```bash
cd /home/user/builtin-clone
python3 app.py
# or: PORT=8000 ./run.sh
```

The server binds `0.0.0.0:8000`, so the Arena live preview can reach it. It uses only the Python standard library plus SQLite — no `pip install`, no build step, no CDN.

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Job seeker | `candidate@demo.com` | `demo1234` |
| Employer | `employer@demo.com` | `demo1234` |

You can also create a new account from `/auth/signup`.

## What is implemented

### Pages / routes

- `/` — homepage with hero, company logo grid, feature strip, job-search links, categories and CTA
- `/jobs` — searchable, filterable job board with pagination
- `/jobs/remote`, `/jobs/<category>` — remote and category landing pages
- `/job/<slug>/<id>` — job detail, description, skills, similar jobs, apply form
- `/companies` — company directory with filters
- `/companies/hiring/remote`, `/companies/location/fully-remote`, `/companies/type/<industry>`
- `/company/<slug>` — company profile with tabs: Overview, Jobs, Offices, Teams, Culture, Perks + Benefits, Articles, Company Insights
- `/salaries`, `/salaries/<role>` — salary explorer, ranges and detail pages
- `/tech-topics`, `/tag/<tag>`, `/articles/<slug>` — article index, tag pages and article detail
- `/tech-hubs`, `/tech-hubs/<city>`, `/tech-dictionary`, `/awards`, `/awards/<city>/current/best-places-to-work`, `/remote`
- `/search` — global search results
- `/auth/login`, `/auth/signup`, `/logout`
- `/profile` — dashboard and profile settings, `/saved`, `/tracker`, `/alerts`
- `/employers`, `/employers/post-job` — employer workspace with job create, edit and archive flows
- `/about`, `/contact`, `/privacy`, `/terms`, `/sitemap.xml`, `/robots.txt`, `/health`
- 404 page

### Real backend behavior

All state lives in `data/site.db` (SQLite). It is created and seeded automatically on first start.

- Sign-up, login, password hashing (PBKDF2-HMAC-SHA256) and HttpOnly session cookies
- Save / unsave jobs, follow / unfollow companies
- Apply to a job and see it in the Application Tracker
- Create, edit and delete job alerts
- Candidate workspace with sidebar navigation, saved roles, application history and profile settings
- Employer workspace with owned job listings that publish to `/jobs`, company pages, search and the sitemap
- First-run demo accounts include saved jobs, applications, followed companies, alerts and employer listings
- Editable profile
- Newsletter subscription (stored in the database)
- Global search across jobs, companies and articles
- JSON API: `/api/me`, `/api/search`, `/api/jobs`, `/api/saved/<id>/toggle`, `/api/follow/<id>/toggle`, `/api/apply/<id>`, `/api/applications/<id>`, `/api/alerts`, `/api/employer/jobs/<id>`, `/api/newsletter`

### Front-end interactions

- Filter forms and pagination
- Expandable job cards
- Optimistic saves, alert edits/deletes, application withdrawals and employer job updates with toast feedback (vanilla JS)
- Workspace loading progress, responsive sidebar navigation and empty states
- Global search overlay (press `/` or click the header search icon)
- Mobile navigation and responsive layout

## Project layout

```
builtin-clone/
├── app.py                 # HTTP server, routing, forms, API handlers
├── db.py                  # SQLite schema, seed, auth and queries
├── seed.py                # Sample companies, jobs, articles, salaries, hubs, glossary
├── views.py               # Server-rendered HTML components and pages
├── static/
│   ├── styles.css         # Full design system, responsive CSS
│   ├── app.js             # Client-side interactions
│   └── fonts/             # Locally served Montserrat variable font (open source)
├── data/site.db           # Created automatically; holds all app state
├── run.sh                 # Convenience launcher
└── README.md
```

## Customize it

1. **Your own assets:** put logos, photos and a favicon in `static/`. Company logos are currently generated as colored initial tiles in `views.company_logo()`; photos are inline SVG illustrations from `views.photo_placeholder()`. Replace those two functions to use `<img>` tags pointing at your files.
2. **Your own content:** edit `seed.py`. To apply changes, reset the database:
   ```bash
   rm -f data/site.db
   python3 app.py
   ```
3. **Brand and colors:** edit the CSS variables at the top of `static/styles.css` (`--navy`, `--blue`, `--magenta`, `--pale`, etc.) and the wordmark in `views.brand_logo()`.
4. **Backend logic:** `db.py` holds the queries; `app.py` holds routes and POST handlers.

## LinkedIn-style restyle

Company profiles, the company directory cards and job detail pages were restyled into a LinkedIn-like layout while keeping the original demo palette (`--navy`, `--blue`, `--magenta`, `--pale`):

- Company profile: gradient cover banner, overlapping profile card with rounded logo, `Follow / View jobs / Website` actions, tab bar (`Overview, Jobs, People, Posts, Insights, Offices, Culture, Perks + Benefits`), two-column content cards and a sidebar with company facts, alerts and similar pages.
- Company directory: clean white result cards with square logos, meta lines, open-role chips and a `Follow` button.
- Job detail: compact header card with `Save / Apply now`, main "About the job" card and a right sidebar with "About the company", "At a glance" and salary insight.
- Legacy links such as `/company/<slug>/teams`, `/articles` and `/faq/<topic>` still resolve and map to the new `People`, `Posts` and `Insights` tabs.

The old Built In-style view functions remain in `views.py` but are no longer routed; the active functions are `linkedin_company_detail_page`, `linkedin_company_card`, `linkedin_job_card` and `linkedin_job_detail_page`.

## Homepage differentiation

The homepage was deliberately moved away from the Built In-style hero so the demo does not read as a one-to-one copy. It now uses an editorial, LinkedIn-adjacent blue/white/gray layout scoped to `body.home-v2`; all other pages keep their existing styling.

- Split hero with a compact search form, `NEW / JOB / MENTOR / Create CV` quick links and a "Today on the network" summary card that links to the detailed articles, jobs and company pages.
- `01 / NEW` section with editor, company and expert post summaries — curated cards, not a social stream.
- `02 / OPPORTUNITIES` section with square image-led job cards, light-blue job titles, short descriptions and an inline "Details" expander on the right that does not navigate away from the homepage.
- `03 / COMPANY` section with a newspaper-style spotlight card plus two compact company cards.
- Gray filter chips, a quiet category cloud, stats band and blue CTA.

The active implementation lives in `home_page()` and the `_hv2_*` helpers in `views.py`; its CSS is the final `home page v2` block in `static/styles.css`. The previous Built In-style homepage markup is no longer routed.

## Notes and limitations

- The original site's proprietary media, exact copy and backend services are not reproduced. Counts such as "500K+ Jobs" are visual placeholders; the demo dataset contains ~80 sample jobs.
- Third-party services (payments, email delivery, maps, real job feeds) are represented by local sample data.
- This is a demo, not production software: no CSRF tokens, rate limiting, email verification, or hardened session/transport policies. Add those before deploying.
- Reset state at any time by deleting `data/site.db` while the server is stopped.
