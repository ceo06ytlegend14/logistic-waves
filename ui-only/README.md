# Workboard — UI-only homepage

A single static `index.html` containing the redesigned homepage **layout only**.

## What is (and is not) here

- Pure HTML/CSS with a tiny bit of native `<details>` interaction.
- No backend, no database, no API calls, no accounts, no external assets/CDN/fonts.
- All names, counts, articles, jobs and company profiles are neutral placeholders (`Company A`, `Product Designer`, `Editorial team`, etc.).
- No Built In branding, no real company names, no copied article text, no scraped data.

## Preview locally

```bash
cd ui-only
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy to Vercel

Option A — drag and drop:
1. Go to https://vercel.com/new
2. Drag the `ui-only` folder onto the page, or import a Git repo containing this folder.
3. Deploy. Vercel will serve `index.html` automatically; no build command is needed.

Option B — CLI:
```bash
cd ui-only
npx vercel --prod
```

Option C — connect the Vercel app in this Arena conversation, then ask me to deploy it.

## Other static hosts

The same folder works on Netlify Drop, GitHub Pages, Cloudflare Pages, or any static file server. No configuration file is required.
