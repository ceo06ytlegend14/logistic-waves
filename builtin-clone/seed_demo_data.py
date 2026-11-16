import sqlite3, random, os

base = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(base, 'data', 'site.db'))
conn.row_factory = sqlite3.Row

# Seed applications
app_count = conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
if app_count == 0:
    jobs = conn.execute('SELECT id FROM jobs LIMIT 10').fetchall()
    users = conn.execute('SELECT id FROM users').fetchall()
    statuses = ['Applied', 'Reviewing', 'Interview', 'Offer', 'Rejected']
    notes = [
        'Strong candidate with port operations background.',
        'Reviewing CV and cover letter.',
        'Scheduled for panel interview.',
        'Offer extended pending background check.',
        'Position filled internally.',
    ]
    random.seed(42)
    inserted = 0
    for job in jobs:
        for user in users:
            status = random.choice(statuses)
            note = random.choice(notes)
            days = str(random.randint(1, 30))
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO applications (user_id, job_id, status, note, created_at) VALUES (?,?,?,?,date('now','-' || ? || ' days'))",
                    (user['id'], job['id'], status, note, days)
                )
                inserted += 1
            except Exception as ex:
                print('app err:', ex)
    conn.commit()
    print('Seeded', inserted, 'applications')
else:
    print('Applications already exist:', app_count)

# Seed subscribers
sub_count = conn.execute('SELECT COUNT(*) FROM subscribers').fetchone()[0]
if sub_count == 0:
    emails = [
        'nguyen.logistics@gmail.com', 'tran.supply@outlook.com',
        'le.maritime@yahoo.com', 'pham.freight@gmail.com',
        'hoang.port@company.vn', 'minh.shipping@gmail.com',
        'linh.cargo@outlook.com', 'duc.customs@gmail.com',
        'thu.supply@company.vn', 'hung.terminal@gmail.com',
        'mai.logistics@yahoo.com', 'bao.maritime@outlook.com',
    ]
    for i, em in enumerate(emails):
        try:
            conn.execute(
                "INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, date('now','-' || ? || ' days'))",
                (em, str(i * 2 + 1))
            )
        except Exception as ex:
            print('sub err:', ex)
    conn.commit()
    print('Seeded', len(emails), 'subscribers')
else:
    print('Subscribers already exist:', sub_count)

conn.close()
print('Done seeding!')
