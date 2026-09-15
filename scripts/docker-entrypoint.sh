#!/usr/bin/env bash
set -e

# Wait for Postgres
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  until python -c "
import sys, urllib.parse as up, psycopg
u = up.urlparse('$DATABASE_URL')
try:
    psycopg.connect(dbname=u.path[1:], user=u.username, password=u.password, host=u.hostname, port=u.port).close()
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
  done
  echo "Database is up."
fi

exec "$@"