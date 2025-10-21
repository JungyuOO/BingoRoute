#!/bin/sh
set -e

HOST="${DB_HOST:-postgres}"
PORT="${DB_PORT:-5432}"

printf 'Waiting for PostgreSQL at %s:%s...\n' "$HOST" "$PORT"
while ! python - <<PYCODE
import socket
import sys

host = "${HOST}"
port = int("${PORT}")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(1)
    try:
        sock.connect((host, port))
    except OSError:
        sys.exit(1)
PYCODE
do
  sleep 1
done

echo "PostgreSQL is up, cleaning old migrations..."
# 모든 마이그레이션 파일 삭제 (__init__.py 제외)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "Creating fresh migrations..."
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000