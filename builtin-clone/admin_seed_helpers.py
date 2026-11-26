import sys
sys.path.insert(0, 'builtin-clone')
import db
import seed
from datetime import datetime

def seed_sample_today_videos(conn):
    """Seed or update the 6 Logistic Waves Today episodes"""
    now = datetime.utcnow().strftime("%Y-%m-%d")
    episodes = [
        {
            "slug": "freightwaves-today-live-up-summit",
            "title": "Logistic Waves Today Live: Port Automation & Space Tech Logistics",
            "excerpt": "Join Logistic Waves Today live with industry pioneers at the UP.Summit examining modern autonomous freight and maritime breakthroughs.",
            "category": "Maritime & Tech",
            "tag": "Logistic Waves Today",
            "author": "Rachel Premack",
            "published": "Nov 5, 2026",
            "read_time": "14 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_1.jpg",
            "is_today": 1,
            "duration": "14:20 min",
            "guest": "Chip Palombini"
        },
        {
            "slug": "flying-taxis-and-cargo-electric-aviation",
            "title": "Flying Taxis & Cargo: Electric Aviation's Commercial Future Takes Off",
            "excerpt": "BETA Technologies secures landmark FAA commercial authorization for next-generation electric cargo aircraft.",
            "category": "Air Cargo",
            "tag": "Logistic Waves Today",
            "author": "John Paul Hampstead",
            "published": "Nov 6, 2026",
            "read_time": "18 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_2.svg",
            "is_today": 1,
            "duration": "18:45 min",
            "guest": "Mike Haridopolos"
        },
        {
            "slug": "florida-space-race-private-sector-boom",
            "title": "Florida's Space Race: 95% Launch Cost Drop Fuels Private Port Boom",
            "excerpt": "Cape Canaveral infrastructure expansion unites heavy commercial rocket logistics with deepwater coastal shipping.",
            "category": "Aerospace Logistics",
            "tag": "Logistic Waves Today",
            "author": "Mark Solomon",
            "published": "Nov 6, 2026",
            "read_time": "11 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_3.jpg",
            "is_today": 1,
            "duration": "11:30 min",
            "guest": "Billy Thalheimer"
        },
        {
            "slug": "electric-flying-boat-lands-orderbook",
            "title": "Electric 'Flying Boat' Lands $5 Billion Commercial Marine Orderbook",
            "excerpt": "REGENT Craft's revolutionary wing-in-ground seaglider achieves 180 mph coastal container passenger and express transit.",
            "category": "Maritime Shipping",
            "tag": "Logistic Waves Today",
            "author": "Grace Sharkey",
            "published": "Nov 7, 2026",
            "read_time": "16 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_4.jpg",
            "is_today": 1,
            "duration": "16:15 min",
            "guest": "Elena Rostova"
        },
        {
            "slug": "transpacific-container-spot-rates-ai",
            "title": "Transpacific Container Rates: Algorithmic Routing Softens Spot Volatility",
            "excerpt": "Ocean carriers deploy real-time digital twins to stabilize Asia-to-US West Coast port bottlenecks and demurrage fees.",
            "category": "Container Shipping",
            "tag": "Logistic Waves Today",
            "author": "Greg Miller",
            "published": "Nov 8, 2026",
            "read_time": "21 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_5.jpg",
            "is_today": 1,
            "duration": "21:05 min",
            "guest": "Marcus Vance"
        },
        {
            "slug": "green-corridors-ammonia-containerships",
            "title": "Green Maritime Corridors: Dual-Fuel Ammonia Vessels Enter Global Service",
            "excerpt": "Leading transoceanic liner services initiate zero-carbon bunkering infrastructure across Southeast Asia and Northern Europe.",
            "category": "Clean Freight",
            "tag": "Logistic Waves Today",
            "author": "Henry Byers",
            "published": "Nov 9, 2026",
            "read_time": "15 min watch",
            "accent": "#0084ff",
            "thumb": "/static/images/fw_today_6.jpg",
            "is_today": 1,
            "duration": "15:40 min",
            "guest": "David Lindholm"
        }
    ]

    added = 0
    for ep in episodes:
        existing = conn.execute("SELECT id FROM articles WHERE slug=?", (ep["slug"],)).fetchone()
        body_text = f"Full editorial broadcast analysis for {ep['title']}.\n\nFeatured guest {ep['guest']} joins the broadcast to detail strategic breakthroughs, supply chain resilience, commercial market momentum, and next-generation freight technologies."
        if existing:
            conn.execute(
                """UPDATE articles SET 
                   title=?, excerpt=?, body=?, author=?, published=?, category=?, 
                   tag=?, read_time=?, accent=?, thumb=?, is_today=?, duration=?, guest=?
                   WHERE id=?""",
                (
                    ep["title"], ep["excerpt"], body_text, ep["author"], ep["published"],
                    ep["category"], ep["tag"], ep["read_time"], ep["accent"], ep["thumb"],
                    ep["is_today"], ep["duration"], ep["guest"], existing[0]
                )
            )
        else:
            conn.execute(
                """INSERT INTO articles 
                   (slug, title, excerpt, body, author, published, category, tag, read_time, accent, thumb, is_today, duration, guest)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    ep["slug"], ep["title"], ep["excerpt"], body_text, ep["author"], ep["published"],
                    ep["category"], ep["tag"], ep["read_time"], ep["accent"], ep["thumb"],
                    ep["is_today"], ep["duration"], ep["guest"]
                )
            )
            added += 1
    conn.commit()
    return len(episodes), added

def seed_sample_logistics_companies_and_jobs(conn):
    """Seed dedicated logistics corporations and tech jobs"""
    companies = [
        {
            "slug": "viconship-corp",
            "name": "Viconship Container Ports",
            "initials": "VC",
            "color": "#034f9a",
            "tagline": "Leading Container Terminal & Intermodal Freight Network",
            "industries": "Logistics & Maritime",
            "description": "Vietnam Container Shipping Joint Stock Corporation operates high-efficiency deepwater container terminals, bonded dry ports, and automated logistics depots across key coastal economic corridors.",
            "location": "Haiphong & Da Nang, Vietnam",
            "employees": 3200,
            "offices": 8,
            "founded": 1985,
            "benefits": 18,
            "office_type": "Terminal & Regional HQ",
            "remote_policy": "Hybrid / On-site",
            "hiring_now": 1,
            "open_jobs": 4,
            "website": "https://viconship.com"
        },
        {
            "slug": "gemadept-shipping",
            "name": "Gemadept Logistics & Port",
            "initials": "GD",
            "color": "#0284c7",
            "tagline": "Pioneering Port Ecosystem and Supply Chain Infrastructure",
            "industries": "Logistics & Ocean Freight",
            "description": "Gemadept Corporation is a frontrunner in port operations and integrated logistics, spearheading digital riverways, container feeder networks, and multi-modal logistics parks.",
            "location": "Ho Chi Minh City, Vietnam",
            "employees": 2800,
            "offices": 12,
            "founded": 1990,
            "benefits": 20,
            "office_type": "Corporate Tower & Terminals",
            "remote_policy": "Hybrid",
            "hiring_now": 1,
            "open_jobs": 3,
            "website": "https://gemadept.com.vn"
        },
        {
            "slug": "maersk-logistics-tech",
            "name": "A.P. Moller - Maersk Tech",
            "initials": "MS",
            "color": "#00243d",
            "tagline": "All-the-Way Global Supply Chain Orchestration",
            "industries": "Maritime Logistics & Supply Chain",
            "description": "Global integrated container logistics giant connecting and simplifying customers' supply chains through end-to-end cloud platforms, IoT tracking, and green vessel corridors.",
            "location": "Copenhagen, Denmark / Singapore / Remote",
            "employees": 110000,
            "offices": 130,
            "founded": 1904,
            "benefits": 25,
            "office_type": "Global Tech Hub",
            "remote_policy": "Flexible Remote",
            "hiring_now": 1,
            "open_jobs": 5,
            "website": "https://maersk.com"
        }
    ]

    jobs = [
        {
            "slug": "senior-terminal-automation-engineer",
            "title": "Senior Port Terminal Automation Engineer",
            "company_slug": "viconship-corp",
            "category": "Operations & Robotics",
            "level": "Senior",
            "workplace": "Hybrid",
            "location": "Haiphong, Vietnam",
            "salary_min": 45000,
            "salary_max": 75000,
            "skills": "PLC, SCADA, TOS, Automation, Python, Industrial IoT",
            "description": "Lead the modernization and deployment of autonomous gantry crane systems, automated guided vehicles (AGVs), and smart berth scheduling algorithms across deepwater berths."
        },
        {
            "slug": "lead-supply-chain-digital-twin-architect",
            "title": "Lead Supply Chain Digital Twin Architect",
            "company_slug": "gemadept-shipping",
            "category": "Engineering & Architecture",
            "level": "Lead",
            "workplace": "Hybrid",
            "location": "Ho Chi Minh City, Vietnam",
            "salary_min": 60000,
            "salary_max": 95000,
            "skills": "Distributed Systems, Go, Kafka, Simulation Models, Kubernetes",
            "description": "Architect high-throughput real-time digital twin platforms connecting river barge fleets, container terminals, and bonded customs warehouses."
        },
        {
            "slug": "principal-maritime-routing-systems-lead",
            "title": "Principal Maritime Routing & IoT Platform Lead",
            "company_slug": "maersk-logistics-tech",
            "category": "Data & AI",
            "level": "Principal",
            "workplace": "Remote",
            "location": "Singapore / Global Remote",
            "salary_min": 140000,
            "salary_max": 195000,
            "skills": "AI Optimization, Geo-Spatial Algorithms, Python, Rust, Cloud Native",
            "description": "Drive predictive oceanic route optimization models that dynamically factor in weather fronts, canal transit wait times, and dual-fuel bunkering consumption."
        }
    ]

    comp_count = 0
    for c in companies:
        ex = conn.execute("SELECT id FROM companies WHERE slug=?", (c["slug"],)).fetchone()
        if not ex:
            conn.execute(
                """INSERT INTO companies
                   (slug, name, initials, color, tagline, industries, description, location,
                    employees, offices, founded, benefits, office_type, remote_policy, hiring_now,
                    open_jobs, website, perks, tech_stack, teams, cover_accent)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    c["slug"], c["name"], c["initials"], c["color"], c["tagline"],
                    c["industries"], c["description"], c["location"], c["employees"], c["offices"],
                    c["founded"], c["benefits"], c["office_type"], c["remote_policy"], c["hiring_now"],
                    c["open_jobs"], c["website"], "Health Insurance, Annual Retreat, Stock Options, Free Meals, Tech Budget",
                    "Python, Go, Kafka, Docker, React, PostgreSQL", "Engineering, Port Operations, Data Science", c["color"]
                )
            )
            comp_count += 1

    job_count = 0
    now_date = datetime.utcnow().strftime("%Y-%m-%d")
    for j in jobs:
        ex = conn.execute("SELECT id FROM jobs WHERE slug=?", (j["slug"],)).fetchone()
        if not ex:
            comp = conn.execute("SELECT id, name, initials, color FROM companies WHERE slug=?", (j["company_slug"],)).fetchone()
            if comp:
                cid, cname, cinit, ccolor = comp
                conn.execute(
                    """INSERT INTO jobs
                       (slug, title, company_id, company_slug, company_name, company_initials,
                        company_color, category, level, workplace, location, salary_min, salary_max,
                        salary_display, industries, skills, description, posted_at, posted_label,
                        is_remote, accent, status)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        j["slug"], j["title"], cid, j["company_slug"], cname, cinit,
                        ccolor, j["category"], j["level"], j["workplace"], j["location"],
                        j["salary_min"], j["salary_max"], f"${j['salary_min']:,} - ${j['salary_max']:,}",
                        "Logistics & Technology", j["skills"], j["description"], now_date, "Just now",
                        1 if j["workplace"] == "Remote" else 0, ccolor, "active"
                    )
                )
                job_count += 1
    db.sync_company_open_jobs(conn)
    conn.commit()
    return comp_count, job_count

if __name__ == '__main__':
    c = db.connect()
    ep_total, ep_added = seed_sample_today_videos(c)
    print(f"Seeded videos: {ep_total} total, {ep_added} added.")
    comps, jobs = seed_sample_logistics_companies_and_jobs(c)
    print(f"Seeded logistics entities: {comps} companies, {jobs} jobs.")
    c.close()
