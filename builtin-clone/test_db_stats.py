import sys
sys.path.insert(0, 'builtin-clone')
import db

conn = db.connect()
print('Counts:', db.counts(conn))
print('Articles count:', conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0])
print('Today articles:', conn.execute("SELECT COUNT(*) FROM articles WHERE tag='Logistic Waves Today'").fetchone()[0])
print('Jobs count:', conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0])
print('Companies count:', conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0])
conn.close()
