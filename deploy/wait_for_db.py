import os
import time
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
WAIT_SECONDS = int(os.getenv('DB_WAIT_SECONDS', '30'))

if not DATABASE_URL:
    raise SystemExit('DATABASE_URL not set')

engine = create_engine(DATABASE_URL)

last_error = None
for _ in range(WAIT_SECONDS):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database is reachable')
        raise SystemExit(0)
    except Exception as exc:  # noqa: BLE001
        last_error = exc
        time.sleep(1)

print(f'Database not reachable after {WAIT_SECONDS}s: {last_error}')
raise SystemExit(1)
