"""Sample content for the Built In-style demo clone.

All copy, logos and images here are placeholders. The real site's media is not copied:
company marks are rendered as colored initial tiles in the UI so you can drop in
your own assets later.
"""
from datetime import datetime, timedelta

BASE_DATE = datetime(2026, 11, 3, 9, 0, 0)

CATEGORIES = [
    "AI & Machine Learning", "Consulting", "Customer Success & Experience",
    "Cybersecurity", "Data & Analytics", "Design", "Engineering", "Finance",
    "HR & Recruiting", "Legal", "Marketing", "Operations & Support",
    "Product Management", "Program & Project Management", "Sales",
    "Supply Chain & Procurement",
]

LEVELS = [
    "Internship", "Entry level", "Junior", "Mid level", "Senior level",
    "Expert/Leader",
]

WORKPLACES = ["Fully Remote", "Hybrid", "On Site", "Remote or Hybrid"]

LOCATIONS = [
    "Remote", "US", "United States", "New York, NY, USA", "San Francisco, CA, USA",
    "Boston, MA, USA", "Chicago, IL, USA", "Austin, TX, USA", "Seattle, WA, USA",
    "Atlanta, GA, USA", "Denver, CO, USA", "Los Angeles, CA, USA",
    "San Diego, CA, USA", "San Jose, CA, USA", "Warren, MI, USA", "Boise, ID, USA",
    "Dallas, TX, USA", "Washington, DC, USA", "Miami, FL, USA", "India",
    "2 Locations", "4 Locations",
]

INDUSTRIES = [
    "Artificial Intelligence", "Automation", "Biotech", "Cloud", "Cybersecurity",
    "Data & Analytics", "Design", "Digital Media", "eCommerce", "Edtech", "Energy",
    "Financial Services", "Fintech", "Food", "Gaming", "Hardware", "Healthtech",
    "Hospitality", "HR Tech", "Information Technology", "Insurance", "Legal Tech",
    "Machine Learning", "Manufacturing", "Marketing Tech", "Mobile", "News + Entertainment",
    "Payments", "Pharmaceutical", "Productivity", "Security", "Software",
    "Social Impact", "Social Media", "Transportation",
]

COMPANIES = [
    dict(slug="viconship", name="Viconship Logistics Group", initials="VS", color="#003366", tagline="Viconship Logistics Group — Accredited Multimodal Terminal Operator",
         industries="Maritime & Seaport,Freight Forwarding & 3PL,Multimodal Logistics,Supply Chain", location="Ho Chi Minh City, VN", employees=2500, offices=5, founded=1985,
         benefits=95, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=12,
         description="Viconship is one of Vietnam's leading integrated container seaport operators. We drive multimodal freight forwarding, container terminal management at Green Port and VIP Green Port, bonded warehousing, and logistics supply chain services connecting Vietnam with major world trade lanes."),
    dict(slug="gitlab", name="GitLab", initials="GL", color="#e24329", tagline="The intelligent orchestration platform for DevSecOps",
         industries="Cloud,Security,Software,Cybersecurity,Automation", location="San Francisco", employees=2500, offices=1, founded=2014,
         benefits=92, office_type="Fully Remote", remote_policy="Fully Remote", hiring_now=1, open_jobs=234,
         description="Teams build the tools that help software creators plan, build, secure and deploy great products. A remote-first culture, documented workflows and a strong open-source heritage shape the day-to-day experience."),
    dict(slug="braze", name="Braze", initials="BZ", color="#20232c", tagline="Customer engagement that connects people and brands",
         industries="Marketing Tech,Software,Artificial Intelligence,Analytics", location="New York", employees=1500, offices=8, founded=2011,
         benefits=68, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=47,
         description="Cross-functional teams create a real-time engagement platform used by global brands. Engineers, designers and go-to-market teammates work closely on data-rich experiences at scale."),
    dict(slug="capital-one", name="Capital One", initials="C1", color="#004977", tagline="Technology-driven financial services",
         industries="Fintech,Financial Services,Artificial Intelligence,Information Technology", location="McLean, VA", employees=52000, offices=18, founded=1988,
         benefits=85, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=312,
         description="Large-scale engineering, data and product teams modernize banking experiences. The culture blends enterprise stability with small-team ownership and a strong investment in cloud and machine learning."),
    dict(slug="servicenow", name="ServiceNow", initials="SN", color="#0b6623", tagline="The AI platform for business transformation",
         industries="Cloud,Software,Information Technology,Automation", location="Santa Clara, CA", employees=24000, offices=31, founded=2004,
         benefits=79, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=188,
         description="Teams build workflow products that connect systems and people across the enterprise. The work spans platform engineering, applied AI, design systems and customer success."),
    dict(slug="datadog", name="Datadog", initials="DD", color="#632ca6", tagline="Observability for the modern cloud",
         industries="Cloud,Analytics,Software,Information Technology", location="New York", employees=5200, offices=12, founded=2010,
         benefits=74, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=96,
         description="Engineers work on high-volume telemetry, distributed systems and developer tooling. The product surface ranges from infrastructure monitoring to security and AI observability."),
    dict(slug="general-motors", name="General Motors", initials="gm", color="#0057b8", tagline="Building an all-electric, software-defined future",
         industries="Automotive,Manufacturing,Artificial Intelligence,Software", location="Detroit, MI", employees=163000, offices=45, founded=1908,
         benefits=88, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=421,
         description="Software, hardware and manufacturing teams collaborate on connected vehicles, autonomous systems and next-generation mobility services."),
    dict(slug="pfizer", name="Pfizer", initials="PZ", color="#0093d0", tagline="Science-driven breakthroughs for patients",
         industries="Pharmaceutical,Healthtech,Biotech,Analytics", location="New York", employees=88000, offices=36, founded=1849,
         benefits=91, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=204,
         description="Digital, data and research teams support the discovery, development and delivery of medicines around the world. Work is grounded in scientific rigor and patient impact."),
    dict(slug="pnc-financial-services-group", name="PNC Bank", initials="PNC", color="#00539f", tagline="A leading diversified financial services institution",
         industries="Machine Learning,Payments,Security,Software,Financial Services", location="Pittsburgh", employees=55000, offices=6, founded=1852,
         benefits=55, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=79,
         description="Technology teams build secure banking, payments and data platforms for millions of customers, with a growing focus on applied AI and resilient infrastructure."),
    dict(slug="toast", name="Toast", initials="T", color="#2a6df4", tagline="The restaurant platform built for operators",
         industries="Cloud,Fintech,Food,Software,Hospitality,Information Technology", location="Boston", employees=5700, offices=7, founded=2012,
         benefits=63, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=142,
         description="Product and engineering teams build point-of-sale, payments, payroll and guest-facing tools used by restaurants of every size."),
    dict(slug="snap-inc", name="Snap Inc.", initials="S", color="#f7d800", tagline="Camera, AR and communication for the world",
         industries="Social Media,Artificial Intelligence,Software,Mobile", location="Santa Monica, CA", employees=5300, offices=9, founded=2011,
         benefits=71, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=88,
         description="Teams experiment at the intersection of computer vision, augmented reality and large-scale consumer infrastructure."),
    dict(slug="nbcuniversal", name="NBCUniversal", initials="NBC", color="#6d28d9", tagline="Stories, streaming and technology at global scale",
         industries="Digital Media,News + Entertainment,Information Technology", location="New York", employees=35000, offices=22, founded=2004,
         benefits=82, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=126,
         description="Engineering, data and product teams power streaming, broadcast and digital experiences across a portfolio of beloved brands."),
    dict(slug="floqast", name="FloQast", initials="FQ", color="#064e3b", tagline="The first accounting transformation platform powered by AI agents",
         industries="Artificial Intelligence,Fintech,Software", location="Los Angeles", employees=800, offices=8, founded=2013,
         benefits=90, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=38,
         description="Automation and accounting teams work together to streamline recurring finance workflows, from month-end close to reporting and reconciliation."),
    dict(slug="comcast", name="Comcast", initials="C", color="#0b3d91", tagline="Connecting people to the experiences they love",
         industries="Digital Media,Information Technology,News + Entertainment", location="Philadelphia", employees=115000, offices=18, founded=1963,
         benefits=94, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=241,
         description="Teams build connectivity platforms, streaming products and customer experiences used in millions of homes and businesses."),
    dict(slug="csc", name="CSC", initials="CSC", color="#0f5a9e", tagline="Business administration and compliance, globally",
         industries="Fintech,Legal Tech,Software,Financial Services,Cybersecurity,Data Privacy", location="Wilmington, DE", employees=8500, offices=45, founded=1899,
         benefits=106, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=64,
         description="Product and operations teams deliver secure digital administration, compliance and entity-management workflows for global clients."),
    dict(slug="sophia-genetics", name="SOPHiA GENETICS", initials="SG", color="#00a6a6", tagline="Data-driven medicine, worldwide",
         industries="Artificial Intelligence,Big Data,Healthtech,Software,Biotech", location="Boston", employees=600, offices=4, founded=2011,
         benefits=58, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=31,
         description="Cloud, analytics and clinical teams build a platform that helps hospitals turn complex genomic data into actionable insights."),
    dict(slug="clearwater-analytics", name="Clearwater Analytics", initials="CW", color="#3b82f6", tagline="Investment data and reporting in one place",
         industries="Fintech,Software,Financial Services", location="Boise, ID", employees=1900, offices=6, founded=2004,
         benefits=61, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=52,
         description="Teams unify, reconcile and report on investment data for global asset managers and insurers, with a strong focus on automation and data quality."),
    dict(slug="built-in", name="Built In", initials="BI", color="#aa2fbe", tagline="Trusted signals for where to work",
         industries="Software,Information Technology,HR Tech,Productivity", location="Chicago", employees=420, offices=3, founded=2011,
         benefits=67, office_type="Fully Remote", remote_policy="Fully Remote", hiring_now=1, open_jobs=26,
         description="Product, content and data teams help candidates and employers make better decisions with company insights, jobs and editorial coverage."),
    dict(slug="kepler", name="Kepler", initials="K", color="#4d1096", tagline="The trust layer for AI",
         industries="Artificial Intelligence,Fintech,Software", location="New York", employees=9, offices=1, founded=2023,
         benefits=26, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=10,
         description="A small team separates what AI does well from what code does well, building systems that can show their work and prove their answers."),
    dict(slug="artera", name="Artera", initials="A", color="#00a6a6", tagline="Agentic patient communication for healthcare",
         industries="Healthtech,Sales,Software,Analytics,Conversational AI", location="Santa Barbara", employees=250, offices=4, founded=2015,
         benefits=66, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=29,
         description="Teams design conversational workflows that help providers reach patients, reduce administrative load and improve access to care."),
    dict(slug="2k", name="2K", initials="2K", color="#e2001a", tagline="Games and worlds that bring people together",
         industries="Gaming,Software,Digital Media,Design", location="Novato, CA", employees=4200, offices=11, founded=2005,
         benefits=77, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=58,
         description="Studio, engineering and publishing teams build immersive entertainment across platforms, supported by data, infrastructure and live operations."),
    dict(slug="stripe", name="Stripe", initials="S", color="#635bff", tagline="Financial infrastructure for the internet",
         industries="Fintech,Payments,Software,Developer Tools", location="San Francisco, CA", employees=8000, offices=14, founded=2010,
         benefits=92, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=385,
         description="Stripe builds economic infrastructure for the internet, helping businesses of all sizes accept payments and manage transactions online."),
    dict(slug="spotify", name="Spotify", initials="SP", color="#1ed760", tagline="Audio and streaming entertainment for millions worldwide",
         industries="Digital Media,Music,Artificial Intelligence,Mobile", location="New York, NY", employees=9100, offices=18, founded=2006,
         benefits=89, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=295,
         description="Spotify connects millions of creators and fans with a personalized audio platform powered by machine learning and large-scale data engineering."),
    dict(slug="airbnb", name="Airbnb", initials="AB", color="#ff5a5f", tagline="Belong anywhere with authentic travel experiences",
         industries="Marketplace,Travel,Software,Design", location="San Francisco, CA", employees=6800, offices=21, founded=2008,
         benefits=94, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=264,
         description="Airbnb operates an online marketplace that connects hosts and travelers, focusing on intuitive product design and community safety."),
    dict(slug="snowflake", name="Snowflake", initials="SF", color="#29b5e8", tagline="The AI Data Cloud mobilizing the world's data",
         industries="Cloud,Big Data,Analytics,Artificial Intelligence", location="Bozeman, MT", employees=7000, offices=25, founded=2012,
         benefits=86, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=248,
         description="Snowflake powers modern data workloads with a single, cloud-native architecture for data warehousing, lakes, sharing and AI applications."),
    dict(slug="figma", name="Figma", initials="FG", color="#a259ff", tagline="Connecting teams to design and build better products together",
         industries="Design,Software,Collaboration,Developer Tools", location="San Francisco, CA", employees=1500, offices=6, founded=2012,
         benefits=91, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=215,
         description="Figma is the collaborative interface design tool where teams build, prototype and share digital experiences in real-time."),
    dict(slug="canva", name="Canva", initials="CV", color="#00c4cc", tagline="Empowering the world to design anything and publish anywhere",
         industries="Design,Artificial Intelligence,Software,Content", location="Austin, TX", employees=4500, offices=8, founded=2013,
         benefits=88, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=195,
         description="Canva democratizes visual communication with intuitive drag-and-drop tools and generative AI features for creators and enterprises."),
    dict(slug="cloudflare", name="Cloudflare", initials="CF", color="#f38020", tagline="Helping build a better, safer and faster internet",
         industries="Cybersecurity,Cloud,Networking,Infrastructure", location="San Francisco, CA", employees=3600, offices=16, founded=2009,
         benefits=87, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=182,
         description="Cloudflare protects and accelerates internet applications, providing global DNS, DDoS protection, edge computing and zero-trust security."),
    dict(slug="mongodb", name="MongoDB", initials="MD", color="#00ed64", tagline="The developer data platform for intelligent applications",
         industries="Database,Cloud,Software,Developer Tools", location="New York, NY", employees=5000, offices=32, founded=2007,
         benefits=84, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=155,
         description="MongoDB provides a flexible, distributed document database and cloud developer data platform that powers critical applications globally."),
    dict(slug="discord", name="Discord", initials="DC", color="#5865f2", tagline="Your place to talk, hangout and build communities",
         industries="Social Media,Gaming,Software,Infrastructure", location="San Francisco, CA", employees=1200, offices=4, founded=2015,
         benefits=89, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=138,
         description="Discord is a voice, video and text communications service used by hundreds of millions of people to chat and hang out with friends."),
    dict(slug="notion", name="Notion", initials="N", color="#000000", tagline="The connected workspace for wiki, docs and projects",
         industries="Productivity,Artificial Intelligence,Software,Collaboration", location="San Francisco, CA", employees=750, offices=5, founded=2016,
         benefits=90, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=125,
         description="Notion blends everyday work apps into one connected workspace with docs, wikis, project tracking and integrated AI assistance."),
    dict(slug="reddit", name="Reddit", initials="RD", color="#ff4500", tagline="The heart of the internet and endless conversation",
         industries="Social Media,Artificial Intelligence,Content,Community", location="San Francisco, CA", employees=2200, offices=7, founded=2005,
         benefits=85, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=118,
         description="Reddit hosts authentic conversations on thousands of topics, powered by passionate communities, machine learning and real-time feeds."),
    dict(slug="atlassian", name="Atlassian", initials="AT", color="#0052cc", tagline="Unleashing the potential of every team across the globe",
         industries="Productivity,Enterprise,Software,Collaboration", location="San Francisco, CA", employees=11000, offices=12, founded=2002,
         benefits=93, office_type="Hybrid", remote_policy="Hybrid", hiring_now=1, open_jobs=110,
         description="Atlassian creates team collaboration tools including Jira, Confluence, and Trello to help engineering, product, and business teams work together."),
]

# (company slug, title, category, level, workplace, location, salary low, salary high, industries, skills)
JOB_SPECS = [
    ("viconship", "Senior Ocean Freight Forwarder", "Supply Chain & Procurement", "Senior level", "Hybrid", "Ho Chi Minh City, VN", 112, 168, "Maritime & Seaport,Freight Forwarding & 3PL,Multimodal Logistics", "Ocean Freight (FCL/LCL),Customs EDI Clearance,Carrier FMC Contracts,Demurrage Minimization,FIATA Certification"),
    ("snap-inc", "Independent Agency Partner", "Sales", "Senior level", "Hybrid", "2 Locations", 147, 259, "Social Media,Artificial Intelligence,Software", "Agency Partnerships,Digital Media,Enterprise Sales,Analytics"),
    ("snap-inc", "Lead, Product Marketing Manager - Measurement", "Product Management", "Mid level", "Hybrid", "4 Locations", 162, 284, "Social Media,Artificial Intelligence,Software", "Product Marketing,Measurement,Attribution,SQL"),
    ("snap-inc", "Software Engineer, ML Infrastructure, Core Inference, Level 4", "Engineering", "Senior level", "Hybrid", "2 Locations", 133, 235, "Artificial Intelligence,Machine Learning,Software", "Python,PyTorch,Kubernetes,Distributed Systems"),
    ("general-motors", "Engineering Design group - Engine Team", "Engineering", "Mid level", "Hybrid", "Warren, MI, USA", 104, 168, "Automotive,Manufacturing,Software", "CAD,Mechanical Design,Simulation,Testing"),
    ("general-motors", "Sr Engineering Designer - Engine Team", "Engineering", "Senior level", "Hybrid", "Warren, MI, USA", 128, 196, "Automotive,Manufacturing,Software", "CAD,GD&T,Powertrain,Prototyping"),
    ("general-motors", "Sr. AI/Automation Engineer - HR Technology (Remote India - Night Shift)", "AI & Machine Learning", "Senior level", "Remote or Hybrid", "United States", 139, 214, "Artificial Intelligence,Automation,HR Tech", "LLMs,Python,Workflow Automation,HRIS"),
    ("nbcuniversal", "Analyst, Techline", "Operations & Support", "Mid level", "Remote or Hybrid", "New York, NY, USA", 62, 70, "Digital Media,Information Technology", "Technical Support,ServiceNow,Troubleshooting,Documentation"),
    ("nbcuniversal", "Senior Data Engineer, Streaming Platform", "Data & Analytics", "Senior level", "Hybrid", "New York, NY, USA", 160, 205, "Digital Media,Information Technology,Software", "Spark,Python,AWS,dbt"),
    ("toast", "Solutions Lead, International Upmarket", "Sales", "Senior level", "In-Office", "Boston, MA, USA", 123, 197, "Cloud,Fintech,Food,Software,Hospitality", "REST APIs,Authentication,ERP,PCI DSS"),
    ("toast", "Product Manager, Toast IQ Evaluation", "Product Management", "Entry level", "Remote", "US", 159, 254, "Cloud,Fintech,Food,Software,Hospitality", "LLMs,Databases,Evaluation,AI Coding Tools"),
    ("toast", "Software Engineer II (Fullstack), Digital Storefront", "Engineering", "Entry level", "Remote", "US", 133, 213, "Cloud,Fintech,Food,Software", "React,Node.js,Java,Docker,JavaScript"),
    ("sophia-genetics", "HR Coordinator Intern", "HR & Recruiting", "Internship", "Hybrid", "Boston, MA, USA", 0, 0, "Artificial Intelligence,Big Data,Healthtech,Software,Biotech", "Excel,HR Systems,Payroll Systems,AI Tools"),
    ("clearwater-analytics", "Data Migration Specialist", "Data & Analytics", "Junior", "Hybrid", "Boise, ID, USA", 72, 108, "Fintech,Software,Financial Services", "SQL,Excel,Relational Databases,Reconciliation"),
    ("clearwater-analytics", "Sr. Product Manager I", "Product Management", "Senior level", "Hybrid", "Chicago, IL, USA", 129, 174, "Fintech,Software,Financial Services", "Roadmapping,Agile,Client Discovery,Analytics"),
    ("gitlab", "Senior Ecosystems Sales Manager: Scale, India", "Sales", "Senior level", "Fully Remote", "India", 138, 210, "Cloud,Software,DevSecOps", "Enterprise Sales,Partnerships,Forecasting,SaaS"),
    ("gitlab", "Staff Regional Marketing Manager, West", "Marketing", "Expert/Leader", "Fully Remote", "2 Locations", 145, 220, "Cloud,Software,DevSecOps", "Demand Generation,Field Marketing,Analytics,ABM"),
    ("gitlab", "Staff Software Engineer - NLP", "AI & Machine Learning", "Expert/Leader", "On Site", "Bangalore, India", 168, 260, "Artificial Intelligence,Machine Learning,Software", "NLP,Python,Transformers,Ruby on Rails"),
    ("gitlab", "Incident & Escalation Lead - Enterprise Customers", "Customer Success & Experience", "Senior level", "Fully Remote", "2 Locations", 132, 198, "Cloud,Software,Information Technology", "Incident Management,SRE,Communication,Observability"),
    ("braze", "Senior Software Engineer, Data Platform", "Engineering", "Senior level", "Hybrid", "New York, NY, USA", 175, 255, "Marketing Tech,Software,Analytics", "Kafka,Scala,PostgreSQL,AWS"),
    ("braze", "Product Designer, Canvas", "Design", "Mid level", "Hybrid", "New York, NY, USA", 118, 172, "Marketing Tech,Software,Design", "Figma,Design Systems,Prototyping,User Research"),
    ("capital-one", "Senior Staff Software Engineer", "Engineering", "Expert/Leader", "Hybrid", "Santa Clara, CA, USA", 172, 334, "Artificial Intelligence,Cloud,HR Tech,Software", "Java,Spring Boot,AWS,Microservices"),
    ("capital-one", "Principal Category Sourcing Manager", "Supply Chain & Procurement", "Expert/Leader", "On Site", "San Jose, CA, USA", 155, 249, "Artificial Intelligence,Hardware,Information Technology", "Strategic Sourcing,Negotiation,Supplier Management,Analytics"),
    ("capital-one", "Staff Datapath Design Engineer", "Engineering", "Expert/Leader", "On Site", "San Jose, CA, USA", 190, 246, "Artificial Intelligence,Hardware,Machine Learning", "Verilog,Computer Architecture,RTL,Verification"),
    ("servicenow", "Probe Equipment Engineer", "Engineering", "Mid level", "On Site", "Manassas, VA, USA", 119, 177, "Hardware,Manufacturing,Information Technology", "Semiconductors,Test Equipment,Automation,Statistics"),
    ("servicenow", "Sales Finance Operations Analyst", "Finance", "Mid level", "Hybrid", "Palo Alto, CA, USA", 85, 135, "Fintech,Software,Artificial Intelligence", "Financial Modeling,SQL,Tableau,Forecasting"),
    ("datadog", "SVP Commercial Lender", "Finance", "Expert/Leader", "On Site", "Arlington, MA, USA", 208, 260, "Fintech,Insurance,Payments,Financial Services", "Commercial Lending,Portfolio Management,Credit Risk"),
    ("datadog", "Spirit Defense - Manufacturing Engineer", "Engineering", "Mid level", "Hybrid", "Wichita, KS, USA", 72, 131, "Aerospace,Information Technology,Cybersecurity,Defense", "Manufacturing,Lean,Six Sigma,CAD"),
    ("pfizer", "Machine Learning Research Scientist", "AI & Machine Learning", "Senior level", "Hybrid", "New York, NY, USA", 154, 232, "Pharmaceutical,Healthtech,Biotech,Analytics", "Python,PyTorch,Bioinformatics,Statistics"),
    ("pfizer", "Digital Product Manager, Patient Experience", "Product Management", "Mid level", "Hybrid", "New York, NY, USA", 121, 185, "Healthtech,Pharmaceutical,Software", "Product Strategy,Agile,User Research,Analytics"),
    ("pnc-financial-services-group", "Cybersecurity Threat Analyst", "Cybersecurity", "Mid level", "Hybrid", "Pittsburgh, PA, USA", 98, 152, "Security,Financial Services,Information Technology", "SIEM,Threat Hunting,Incident Response,MITRE ATT&CK"),
    ("pnc-financial-services-group", "Senior UX Researcher", "Design", "Senior level", "Hybrid", "Pittsburgh, PA, USA", 112, 169, "Fintech,Software,Design", "User Research,Usability Testing,Journey Mapping,Figma"),
    ("floqast", "AI Agent Engineer", "AI & Machine Learning", "Senior level", "Hybrid", "Los Angeles, CA, USA", 158, 238, "Artificial Intelligence,Fintech,Software", "LLMs,Python,LangGraph,Evaluation"),
    ("floqast", "Enterprise Account Executive", "Sales", "Senior level", "Hybrid", "Los Angeles, CA, USA", 128, 205, "Fintech,Software,Automation", "SaaS Sales,Discovery,Negotiation,Salesforce"),
    ("comcast", "Principal Cloud Architect", "Engineering", "Expert/Leader", "Hybrid", "Philadelphia, PA, USA", 181, 276, "Cloud,Information Technology,Software", "AWS,Kubernetes,Terraform,Distributed Systems"),
    ("comcast", "Manager, Content Operations", "Operations & Support", "Senior level", "Hybrid", "Philadelphia, PA, USA", 104, 158, "Digital Media,News + Entertainment", "Content Operations,Workflow Design,Analytics,Leadership"),
    ("csc", "Legal Technology Product Lead", "Legal", "Senior level", "Hybrid", "Wilmington, DE, USA", 146, 214, "Legal Tech,Software,Data Privacy", "Compliance,Product Discovery,Contract Lifecycle,Agile"),
    ("csc", "Security Engineer II", "Cybersecurity", "Mid level", "Hybrid", "Wilmington, DE, USA", 102, 160, "Cybersecurity,Software,Financial Services", "AppSec,SAST,OWASP,Python"),
    ("sophia-genetics", "Clinical Data Scientist", "Data & Analytics", "Senior level", "Hybrid", "Boston, MA, USA", 142, 208, "Healthtech,Biotech,Analytics,Software", "Python,R,Genomics,SQL"),
    ("built-in", "Senior Applied AI Engineer", "AI & Machine Learning", "Senior level", "Fully Remote", "India", 165, 245, "Software,HR Tech,Artificial Intelligence", "LLMs,RAG,Python,Evaluation"),
    ("built-in", "Enterprise Account Executive", "Sales", "Senior level", "Hybrid", "Chicago, IL, USA", 135, 210, "Software,HR Tech,Information Technology", "Enterprise Sales,SaaS,Account Planning,Negotiation"),
    ("built-in", "Customer Engagement Manager, SMB", "Customer Success & Experience", "Mid level", "Hybrid", "Chicago, IL, USA", 88, 136, "Software,HR Tech,Productivity", "Customer Success,Onboarding,Data Analysis,CRM"),
    ("kepler", "Founding Full Stack Engineer", "Engineering", "Expert/Leader", "Hybrid", "New York, NY, USA", 175, 265, "Artificial Intelligence,Fintech,Software", "TypeScript,React,PostgreSQL,LLM APIs"),
    ("kepler", "GTM Systems Manager", "Operations & Support", "Mid level", "Hybrid", "New York, NY, USA", 105, 162, "Artificial Intelligence,Software,Productivity", "Salesforce,RevOps,Automation,Analytics"),
    ("artera", "Healthcare Advocate (CX)", "Customer Success & Experience", "Entry level", "Fully Remote", "US", 58, 82, "Healthtech,Software,Analytics", "Customer Support,Healthcare,Communication,Zendesk"),
    ("artera", "Senior Product Designer", "Design", "Senior level", "Hybrid", "Santa Barbara, CA, USA", 132, 195, "Healthtech,Software,Design", "Figma,Design Systems,Accessibility,Prototyping"),
    ("2k", "Gameplay Engineer, Multiplayer", "Engineering", "Senior level", "Hybrid", "Novato, CA, USA", 138, 212, "Gaming,Software,Digital Media", "C++,Unreal Engine,Networking,Gameplay Systems"),
    ("2k", "Technical Artist, Characters", "Design", "Mid level", "Hybrid", "Novato, CA, USA", 96, 148, "Gaming,Design,Software", "Maya,Python,Shaders,Rigging"),
]

EXTRA_JOB_SPECS = [
    ("gitlab", "Senior Backend Engineer, Verify", "Engineering", "Senior level", "Fully Remote", "US", 150, 230, "Cloud,Software,DevSecOps", "Ruby on Rails,PostgreSQL,Go,GraphQL"),
    ("gitlab", "Product Designer, Secure", "Design", "Mid level", "Fully Remote", "2 Locations", 118, 178, "Cloud,Software,Design", "Figma,Design Systems,Accessibility,Research"),
    ("gitlab", "Customer Success Architect", "Customer Success & Experience", "Senior level", "Fully Remote", "US", 132, 198, "Cloud,Software,Information Technology", "Onboarding,Solution Architecture,SaaS,Communication"),
    ("braze", "Engineering Manager, Messaging", "Engineering", "Expert/Leader", "Hybrid", "New York, NY, USA", 190, 280, "Marketing Tech,Software,Analytics", "Leadership,Distributed Systems,Kafka,Coaching"),
    ("braze", "Data Analyst, Campaign Insights", "Data & Analytics", "Mid level", "Hybrid", "New York, NY, USA", 98, 148, "Marketing Tech,Analytics,Software", "SQL,Tableau,Python,Experimentation"),
    ("capital-one", "Senior iOS Engineer", "Engineering", "Senior level", "Hybrid", "McLean, VA, USA", 145, 220, "Fintech,Software,Mobile", "Swift,UIKit,iOS,GraphQL"),
    ("capital-one", "Cybersecurity Engineer II", "Cybersecurity", "Mid level", "Hybrid", "McLean, VA, USA", 112, 168, "Cybersecurity,Financial Services,Information Technology", "SIEM,Cloud Security,Python,Threat Modeling"),
    ("servicenow", "AI Product Manager", "Product Management", "Senior level", "Hybrid", "Santa Clara, CA, USA", 158, 235, "Artificial Intelligence,Software,Automation", "Roadmapping,LLMs,Discovery,Analytics"),
    ("servicenow", "Staff UX Researcher", "Design", "Expert/Leader", "Hybrid", "Santa Clara, CA, USA", 165, 240, "Software,Design,Information Technology", "User Research,Mixed Methods,Design Strategy,Figma"),
    ("datadog", "Senior Site Reliability Engineer", "Engineering", "Senior level", "Hybrid", "New York, NY, USA", 170, 255, "Cloud,Software,Information Technology", "Kubernetes,Terraform,Go,Observability"),
    ("datadog", "Security Product Marketing Manager", "Marketing", "Senior level", "Fully Remote", "US", 132, 198, "Cybersecurity,Cloud,Software", "Product Marketing,Positioning,GTM,Research"),
    ("general-motors", "Data Scientist, Autonomous Systems", "Data & Analytics", "Senior level", "Hybrid", "Warren, MI, USA", 142, 215, "Automotive,Artificial Intelligence,Software", "Python,Computer Vision,SQL,Statistics"),
    ("general-motors", "Technical Program Manager, Vehicle Software", "Program & Project Management", "Senior level", "Hybrid", "Warren, MI, USA", 148, 220, "Automotive,Software,Manufacturing", "Program Management,Agile,Stakeholder Management,Risk"),
    ("pfizer", "Senior DevOps Engineer", "Engineering", "Senior level", "Hybrid", "New York, NY, USA", 152, 225, "Pharmaceutical,Healthtech,Software", "AWS,Docker,Kubernetes,CI/CD"),
    ("pfizer", "Clinical Trial Data Manager", "Data & Analytics", "Mid level", "Hybrid", "New York, NY, USA", 96, 148, "Pharmaceutical,Biotech,Analytics", "Clinical Data,SQL,EDC,Data Quality"),
    ("pnc-financial-services-group", "Full Stack Engineer, Digital Banking", "Engineering", "Mid level", "Hybrid", "Pittsburgh, PA, USA", 112, 170, "Fintech,Software,Financial Services", "React,Java,Spring Boot,SQL"),
    ("pnc-financial-services-group", "Compliance Analyst", "Legal", "Mid level", "Hybrid", "Pittsburgh, PA, USA", 82, 125, "Financial Services,Legal Tech,Data Privacy", "Compliance,Regulatory Research,Reporting,Audit"),
    ("toast", "Senior Data Engineer", "Data & Analytics", "Senior level", "Fully Remote", "US", 155, 230, "Fintech,Food,Software", "Spark,Python,Airflow,Snowflake"),
    ("toast", "Customer Success Manager, Enterprise", "Customer Success & Experience", "Mid level", "Hybrid", "Boston, MA, USA", 92, 140, "Hospitality,Fintech,Software", "Customer Success,Onboarding,CRM,Analytics"),
    ("snap-inc", "AR Product Designer", "Design", "Senior level", "Hybrid", "Santa Monica, CA, USA", 145, 215, "Augmented Reality,Software,Mobile", "Figma,Prototyping,3D,User Research"),
    ("snap-inc", "Machine Learning Engineer, Ranking", "AI & Machine Learning", "Senior level", "Hybrid", "2 Locations", 168, 255, "Artificial Intelligence,Machine Learning,Software", "Python,PyTorch,Ranking,Feature Engineering"),
    ("nbcuniversal", "Product Manager, Streaming Growth", "Product Management", "Senior level", "Hybrid", "New York, NY, USA", 148, 220, "Digital Media,Software,News + Entertainment", "Growth,Experimentation,Analytics,Roadmapping"),
    ("nbcuniversal", "Cloud Security Architect", "Cybersecurity", "Expert/Leader", "Hybrid", "New York, NY, USA", 180, 265, "Cybersecurity,Cloud,Information Technology", "AWS,Zero Trust,IAM,Architecture"),
    ("floqast", "Senior Product Designer", "Design", "Senior level", "Hybrid", "Los Angeles, CA, USA", 138, 202, "Fintech,Software,Design", "Figma,Design Systems,Prototyping,Research"),
    ("floqast", "Implementation Consultant", "Consulting", "Mid level", "Fully Remote", "US", 88, 135, "Fintech,Software,Automation", "Implementation,Accounting,Client Training,SQL"),
    ("comcast", "Data Platform Engineer", "Engineering", "Senior level", "Hybrid", "Philadelphia, PA, USA", 155, 230, "Information Technology,Software,Analytics", "Spark,Kafka,Python,AWS"),
    ("comcast", "Senior Marketing Analyst", "Marketing", "Mid level", "Hybrid", "Philadelphia, PA, USA", 92, 140, "Digital Media,Analytics,Marketing Tech", "SQL,Tableau,Attribution,Forecasting"),
    ("csc", "Product Manager, Compliance Platform", "Product Management", "Senior level", "Hybrid", "Wilmington, DE, USA", 138, 205, "Legal Tech,Software,Financial Services", "Compliance,Product Discovery,Agile,API"),
    ("sophia-genetics", "Backend Engineer, Genomic Platform", "Engineering", "Mid level", "Hybrid", "Boston, MA, USA", 118, 178, "Healthtech,Biotech,Software", "Python,PostgreSQL,Docker,APIs"),
    ("built-in", "Staff Data Engineer", "Data & Analytics", "Expert/Leader", "Fully Remote", "US", 175, 255, "Software,HR Tech,Analytics", "Spark,dbt,Snowflake,Python"),
    ("kepler", "AI Evaluation Researcher", "AI & Machine Learning", "Mid level", "Hybrid", "New York, NY, USA", 125, 190, "Artificial Intelligence,Software,Fintech", "Evaluation,LLMs,Python,Statistics"),
    ("artera", "Implementation Project Manager", "Program & Project Management", "Mid level", "Fully Remote", "US", 95, 145, "Healthtech,Software,Analytics", "Project Management,Healthcare,Onboarding,Agile"),
    ("2k", "Data Engineer, Live Operations", "Data & Analytics", "Mid level", "Hybrid", "Novato, CA, USA", 115, 175, "Gaming,Software,Analytics", "Python,SQL,Airflow,Telemetry"),
    ("clearwater-analytics", "Frontend Engineer, Reporting", "Engineering", "Mid level", "Hybrid", "Boise, ID, USA", 105, 160, "Fintech,Software,Financial Services", "React,TypeScript,Design Systems,Testing"),
]

JOB_SPECS += EXTRA_JOB_SPECS


def _slugify(text):
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def _description(title, company, category, industries, skills):
    first_industry = industries.split(",")[0].lower()
    skill_list = ", ".join(skills.split(",")[:3])
    return (
        f"{company['name']} is hiring a {title} to join its {category} team. You will "
        f"partner with cross-functional teammates to design, build and scale {first_industry} "
        f"products, turn ambiguous problems into clear plans, and ship measurable improvements. "
        f"Ideal candidates bring hands-on experience with {skill_list}, a bias toward collaboration, "
        f"and a habit of documenting decisions. This is sample content for the clone — replace it "
        f"with your own job description when you add real listings."
    )


def build_jobs():
    by_slug = {c["slug"]: c for c in COMPANIES}
    labels = [
        "32 Seconds Ago", "2 Minutes Ago", "34 Minutes Ago", "45 Minutes Ago", "An Hour Ago",
        "2 Hours Ago", "3 Hours Ago", "5 Hours Ago", "7 Hours Ago", "8 Hours Ago",
        "10 Hours Ago", "12 Hours Ago", "Yesterday", "Reposted Yesterday", "2 Days Ago",
        "3 Days Ago", "4 Days Ago", "5 Days Ago", "1 Week Ago", "2 Weeks Ago",
    ]
    jobs = []
    for i, spec in enumerate(JOB_SPECS):
        (company_slug, title, category, level, workplace, location, smin, smax,
         industries, skills) = spec
        company = by_slug[company_slug]
        hours = [0.01, 0.03, 0.6, 0.75, 1, 2, 3][i % 7] if i < 7 else (i * 7) % 168 + 4
        if company_slug == "viconship":
            salary_display = "28M-42M VND Annually"
            job_desc = "Viconship is seeking a seasoned Ocean Freight Forwarding Specialist to manage end-to-end container booking, multimodal carrier negotiations, and freight optimization for multinational manufacturing accounts in Southern Vietnam."
            job_label = "Posted 2 Hours Ago"
        else:
            salary_display = f"{smin}K-{smax}K Annually" if smin else "Competitive"
            job_desc = _description(title, company, category, industries, skills)
            job_label = labels[i % len(labels)]
        jobs.append(dict(
            id=i + 1,
            slug=_slugify(title),
            title=title,
            company_slug=company_slug,
            company_name=company["name"],
            company_initials=company["initials"],
            company_color=company["color"],
            category=category,
            level=level,
            workplace=workplace,
            location=location,
            salary_min=smin,
            salary_max=smax,
            salary_display=salary_display,
            industries=industries,
            skills=skills,
            description=job_desc,
            posted_at=(BASE_DATE - timedelta(hours=float(hours))).isoformat(),
            posted_label=job_label,
            is_remote=1 if "Remote" in workplace else 0,
            accent=company["color"],
            status="active",
        ))
    return jobs


JOBS = build_jobs()

ARTICLES = [
    dict(slug="defense-companies-dallas", title="10 Defense Companies in Dallas to Know",
         excerpt="National security, aerospace engineering and high-tech defense innovation thrive in this North Texas hub.",
         author="Built In Staff, With AI", date="November 03, 2026", category="Tech Hubs", tag="Editors' Picks", read_time="8 min read", accent="#4d1096"),
    dict(slug="boston-aerospace-companies", title="8 Top Aerospace Companies in Boston",
         excerpt="These companies are working with a broad range of technologies, from AI and predictive analytics to innovative hardware manufacturing.",
         author="Alyssa Schroer", date="November 03, 2026", category="Tech Hubs", tag="Company Lists", read_time="6 min read", accent="#244fe7"),
    dict(slug="ai-coding-agents-cloud-wars", title="How AI Coding Agents Are Reigniting the Cloud Wars",
         excerpt="As coding agents evolve from writing code to deploying software, cloud infrastructure must adapt to support them.",
         author="Anurag Goel", date="October 28, 2026", category="Artificial Intelligence", tag="Editors' Picks", read_time="9 min read", accent="#aa2fbe"),
    dict(slug="enterprise-ai-platforms", title="Enterprise AI: What It Is and Top Companies to Know",
         excerpt="Enterprise AI helps companies streamline operations, reduce costs and make better data-driven decisions.",
         author="Brooke Becher", date="November 02, 2026", category="Artificial Intelligence", tag="Explainers", read_time="11 min read", accent="#009ee0"),
    dict(slug="php-security-crisis", title="PHP Has Powered the Web for Decades — Now It's at the Center of a Major Security Crisis",
         excerpt="PHP is a programming language tailored for web development, and it now supports nearly 70 percent of the world's websites.",
         author="Matthew Urwin", date="October 28, 2026", category="Software Engineering", tag="News", read_time="7 min read", accent="#6147d7"),
    dict(slug="classification-evidence-hierarchy", title="Why Data Analysts Need to Own Classification Logic, Not Just Clean It",
         excerpt="AI is making classification drift more expensive. Most analysts don't even know it's happening.",
         author="Kriti Saxena", date="October 28, 2026", category="Data & Analytics", tag="Expert Contributor", read_time="10 min read", accent="#009036"),
    dict(slug="remote-first-companies-hiring", title="12 Remote-First Companies Hiring Right Now",
         excerpt="Distributed teams are building products across fintech, healthtech and developer tools. Here are the teams to watch.",
         author="Built In Staff", date="October 24, 2026", category="Remote Work", tag="Company Lists", read_time="8 min read", accent="#4fe2c1"),
    dict(slug="tech-salaries-2026", title="The Complete Guide to Tech Salaries in 2026",
         excerpt="What engineers, designers, product managers and data professionals are earning across the United States this year.",
         author="Ashley Brownridge", date="October 20, 2026", category="Careers", tag="Salaries", read_time="12 min read", accent="#cc1e8a"),
    dict(slug="portfolio-that-gets-you-hired", title="How to Build a Portfolio That Gets You Hired",
         excerpt="Hiring managers want evidence of judgment, not just screenshots. A practical framework for showing your work.",
         author="Alex Kim", date="October 16, 2026", category="Careers", tag="Guides", read_time="9 min read", accent="#244fe7"),
    dict(slug="tech-hubs-outside-silicon-valley", title="Top 10 Tech Hubs Outside Silicon Valley",
         excerpt="From Austin to Atlanta, these metros are attracting engineers, founders and investment at a remarkable pace.",
         author="Alyssa Schroer", date="October 12, 2026", category="Tech Hubs", tag="Company Lists", read_time="7 min read", accent="#f26c00"),
    dict(slug="product-management-interviews", title="A Practical Guide to Product Management Interviews",
         excerpt="A step-by-step approach to product sense, execution and analytical questions — with examples you can practice.",
         author="Priya Nair", date="October 08, 2026", category="Careers", tag="Guides", read_time="10 min read", accent="#aa2fbe"),
    dict(slug="future-of-cybersecurity-jobs", title="The Future of Cybersecurity Jobs",
         excerpt="AI, regulation and cloud complexity are reshaping what security teams need from their next hire.",
         author="Jordan Lee", date="October 02, 2026", category="Cybersecurity", tag="News", read_time="8 min read", accent="#07006c"),
]

ARTICLE_BODIES = [
    "The technology job market keeps changing, but a few signals stay useful: what teams are building, how they work and which skills they actually reward. This guide pulls those signals together so you can compare opportunities with a little more confidence.",
    "Start with the problem, not the job title. The strongest teams describe a clear customer, a measurable outcome and the constraints that make the work hard. That context tells you far more about day-to-day life than a list of perks ever will.",
    "Next, look at the shape of the team. Cross-functional groups with documented decision-making tend to onboard faster, while platform teams invest more deeply in reliability and developer experience. Neither is automatically better — the right fit depends on how you like to work.",
    "Skills matter most when they are tied to evidence. A portfolio, a migration story or a thoughtful postmortem demonstrates judgment. In interviews, ask for a recent decision the team changed its mind about; the answer usually reveals the real culture.",
    "Finally, treat compensation as a system: base salary, equity, bonus, location policy and growth path all interact. Use the salary tools here as a starting point, then compare against the specific scope of the role you are considering.",
    "This article is sample editorial content created for the clone. Replace it with your own articles, images and author bios when you supply the production assets.",
]

SALARIES = [
    dict(title="Software Engineer", category="Engineering", median=148000, low=98000, high=212000, samples=18420, trend="+4.2%"),
    dict(title="Senior Software Engineer", category="Engineering", median=186000, low=132000, high=268000, samples=12840, trend="+3.8%"),
    dict(title="Data Scientist", category="Data & Analytics", median=152000, low=104000, high=218000, samples=9210, trend="+5.1%"),
    dict(title="Product Manager", category="Product Management", median=161000, low=112000, high=235000, samples=8640, trend="+2.9%"),
    dict(title="Product Designer", category="Design", median=132000, low=88000, high=189000, samples=6120, trend="+3.4%"),
    dict(title="DevOps Engineer", category="Engineering", median=157000, low=108000, high=224000, samples=7380, trend="+4.7%"),
    dict(title="Machine Learning Engineer", category="AI & Machine Learning", median=178000, low=124000, high=265000, samples=5940, trend="+7.3%"),
    dict(title="Cybersecurity Engineer", category="Cybersecurity", median=154000, low=103000, high=221000, samples=4820, trend="+5.6%"),
    dict(title="Data Analyst", category="Data & Analytics", median=98000, low=66000, high=142000, samples=10120, trend="+2.4%"),
    dict(title="Account Executive", category="Sales", median=118000, low=72000, high=198000, samples=7860, trend="+3.1%"),
    dict(title="Technical Program Manager", category="Program & Project Management", median=167000, low=118000, high=238000, samples=4260, trend="+2.7%"),
    dict(title="HR Business Partner", category="HR & Recruiting", median=112000, low=79000, high=158000, samples=3480, trend="+2.2%"),
]

TECH_HUBS = [
    dict(name="San Francisco Bay Area", slug="san-francisco", jobs=48210, companies=3120, color="#244fe7"),
    dict(name="New York City", slug="new-york-city", jobs=39480, companies=2840, color="#aa2fbe"),
    dict(name="Austin", slug="austin", jobs=18240, companies=1120, color="#009ee0"),
    dict(name="Boston", slug="boston", jobs=16920, companies=980, color="#6147d7"),
    dict(name="Chicago", slug="chicago", jobs=15360, companies=1040, color="#4fe2c1"),
    dict(name="Seattle", slug="seattle", jobs=14880, companies=860, color="#009036"),
    dict(name="Atlanta", slug="atlanta", jobs=11240, companies=720, color="#f26c00"),
    dict(name="Los Angeles", slug="los-angeles", jobs=13910, companies=1180, color="#cc1e8a"),
    dict(name="Denver", slug="denver", jobs=9820, companies=610, color="#4d1096"),
    dict(name="Dallas", slug="dallas", jobs=10760, companies=690, color="#07006c"),
    dict(name="Washington, DC", slug="washington-dc", jobs=12430, companies=840, color="#006ab2"),
    dict(name="Miami", slug="miami", jobs=7640, companies=520, color="#e2001a"),
]

DICTIONARY = [
    ("API", "Application Programming Interface", "A contract that lets one piece of software talk to another."),
    ("RAG", "Retrieval-Augmented Generation", "An AI pattern that grounds a model's answer in documents fetched at query time."),
    ("CI/CD", "Continuous Integration / Continuous Delivery", "Automation that builds, tests and ships code changes safely and repeatedly."),
    ("LLM", "Large Language Model", "A neural network trained on large amounts of text to predict and generate language."),
    ("SRE", "Site Reliability Engineering", "A discipline that applies software engineering to operations and reliability problems."),
    ("Design System", "Design System", "A shared library of components, patterns and rules for building consistent interfaces."),
    ("Data Lake", "Data Lake", "A storage approach that keeps raw data in its native format until it is needed."),
    ("Zero Trust", "Zero Trust", "A security model that verifies every request instead of assuming internal traffic is safe."),
    ("OKR", "Objectives and Key Results", "A goal-setting framework that pairs a qualitative objective with measurable outcomes."),
    ("Feature Flag", "Feature Flag", "A switch that lets teams turn functionality on or off without redeploying code."),
    ("Vector Database", "Vector Database", "A database optimized for similarity search over numerical embeddings."),
    ("Technical Debt", "Technical Debt", "The future cost of shortcuts taken to ship something sooner."),
]

AWARDS = [
    ("Best Places To Work", "us", "Large, mid-size and small employers ranked by compensation, culture and benefits."),
    ("Best Places To Work in Atlanta", "atlanta", "Atlanta's highest-rated employers for 2026."),
    ("Best Places To Work in Austin", "austin", "Austin's highest-rated employers for 2026."),
    ("Best Places To Work in Boston", "boston", "Boston's highest-rated employers for 2026."),
    ("Best Places To Work in Chicago", "chicago", "Chicago's highest-rated employers for 2026."),
    ("Best Places To Work in NYC", "new-york-city", "New York City's highest-rated employers for 2026."),
    ("Best Places To Work in San Francisco", "san-francisco", "San Francisco's highest-rated employers for 2026."),
    ("Best Remote Companies To Work For", "remote", "Distributed teams setting the standard for remote work."),
]

PERKS = [
    "Offers 401(K)", "Provides 401(K) matching", "Offers company equity",
    "Provides commuter benefits", "Offers generous parental leave", "Provides family medical leave",
    "Offers health insurance", "Offers dental insurance", "Offers Flexible Spending Account (FSA)",
    "Provides continuing education stipend", "Offers diversity-based Employee Resource Groups",
    "Has a documented equal pay policy", "Hosts company-sponsored family events",
    "Offers performance bonuses", "Provides customized development tracks",
    "Offers company-sponsored outings", "Has a diversity manifesto",
]

TECH_STACK = ["React", "Node.js", "Python", "PostgreSQL", "AWS", "Docker", "Kubernetes", "TypeScript", "Figma", "Tableau", "Snowflake", "GraphQL", "Terraform", "Kafka", "Salesforce"]
