#!/usr/bin/env sh
set -e

cd /app

if [ "${WAIT_FOR_DB:-1}" = "1" ]; then
  python /app/deploy/wait_for_db.py
fi

if [ "${AUTO_CREATE_TABLES:-1}" = "1" ]; then
  python - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv(os.getenv('ENV_FILE', 'config/secrets.env'))
from database.database import init_db, create_all
init_db()
create_all()
print('Database initialized')
PY
fi

exec "$@"
