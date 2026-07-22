#!/usr/bin/env sh
set -e

echo "⏳ Waiting for PostgreSQL..."
python - <<'PY'
import os, sys, time
import dj_database_url
import psycopg

cfg = dj_database_url.parse(os.environ["DATABASE_URL"])
for attempt in range(1, 31):
    try:
        psycopg.connect(
            host=cfg["HOST"], port=cfg["PORT"], dbname=cfg["NAME"],
            user=cfg["USER"], password=cfg["PASSWORD"], connect_timeout=3,
        ).close()
        print("✅ Database is ready.")
        sys.exit(0)
    except Exception as exc:  # noqa
        print(f"  ...not ready ({attempt}/30): {exc}")
        time.sleep(2)
sys.exit("❌ Database never became ready")
PY

echo "🗃  Applying migrations..."
python manage.py migrate --noinput

if [ "${SEED_ON_START:-0}" = "1" ]; then
  echo "🌱 Seeding sample data..."
  python manage.py seed
fi

python manage.py collectstatic --noinput >/dev/null 2>&1 || true

echo "🚀 Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
