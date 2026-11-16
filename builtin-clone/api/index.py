import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app
import db

try:
    db.init_db()
except Exception as ex:
    print(f"init_db notice: {ex}")

class handler(app.Handler):
    pass
