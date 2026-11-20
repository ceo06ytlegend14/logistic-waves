# Job 1 Detail Page & Source Code Package

This directory contains the complete source code, styling, and assets for **Job 1**:
`http://localhost:3000/job-detail.html?id=job-1`

## 📂 File Directory

- **`job-1-standalone.html`**: Standalone version pre-configured for `job-1`. You can double-click this file directly to open it in Chrome, Edge, or Firefox without any server.
- **`job-detail.html`**: The full dynamic page that accepts query parameters (e.g. `?id=job-1`, `?id=job-verified-1793071901986`).
- **`css/`**:
  - `styles.css` - Core styles and reset
  - `builtin-theme.css` - Built In clone design tokens
  - `bootstrap-overrides.css` - Segmented search card & pill styling
- **`images/`**: Brand logos including `images/brands/viconship.svg`, `images/sandbox-logo.png`
- **`js/`**: Core data models and interactive utilities (`main.js`)

---

## 🏗️ How Job-1 Data is Structured

The data for `job-1` is hydrated in `job-detail.html` using this object:

```javascript
const fallbackLogisticsJob = {
  id: 'job-1',
  title: 'Senior Ocean Freight Forwarder',
  company: 'Viconship Logistics Group',
  companyLogo: 'images/brands/viconship.svg',
  location: 'Ho Chi Minh City, VN',
  workplace: 'Hybrid',
  salary: '28M-42M VND Annually',
  seniority: 'Senior level',
  postedTime: 'Posted 2 Hours Ago',
  categories: 'Maritime & Seaport • Freight Forwarding & 3PL • Multimodal Logistics',
  tagline: 'Viconship Logistics Group — Accredited Multimodal Terminal Operator',
  overview: 'Viconship is seeking a seasoned Ocean Freight Forwarding Specialist to manage end-to-end container booking, multimodal carrier negotiations, and freight optimization for multinational manufacturing accounts in Southern Vietnam.',
  intro: 'Viconship is one of Vietnam\'s premier integrated logistics and container seaport operators. We drive multimodal freight forwarding, container terminal management, bonded warehousing, and logistics supply chain services connecting Vietnam with major world trade lanes.',
  summary: 'Responsible for managing container ocean freight forwarding, FMC carrier contracts, port dispatch operations, and customer supply chain delivery across Southeast Asia, North America, and European trade corridors.',
  responsibilities: [
    'Coordinate ocean freight routing, rate negotiations, and space allocation with major maritime alliances (2M, Ocean Alliance, THE Alliance).',
    'Manage complex customs clearance, FMC bill-of-lading (B/L) documentation, and cross-border demurrage/detention minimization.',
    'Act as direct strategic escalation lead for Tier-1 automotive and electronics enterprise shippers.',
    'Supervise electronic EDI declarations under Decree 163/2017/ND-CP and international shipping conventions.'
  ],
  requirements: [
    'Bachelor degree in Foreign Trade, Maritime Studies, or Logistics & Supply Chain.',
    '3+ years managing FCL/LCL container logistics at an accredited 3PL or liner agency.',
    'Fluency in customs e-clearance and port booking systems in Southern Vietnam ports.',
    'Commercial English proficiency for international carrier negotiations.'
  ],
  benefits: [
    'Competitive base salary (28M - 42M VND/month net) + quarterly performance bonus',
    'Full PTI comprehensive health insurance & annual company trip',
    'Flexible hybrid work options (3 days office, 2 days remote)',
    'Sponsored international FIATA certification training'
  ],
  skills: ['Ocean Freight (FCL/LCL)', 'Customs EDI Clearance', 'Carrier FMC Contracts', 'Demurrage Minimization', 'FIATA Certification']
};
```

---

## 🚀 How to Run & Preview

1. **Option A (Double-Click / Direct File):**
   Double-click `job-1-standalone.html` in Windows Explorer. It runs directly in any browser.

2. **Option B (Using the Local Server):**
   When the server is running on port 3000, visit:
   `http://localhost:3000/job-detail.html?id=job-1`
