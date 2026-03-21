#!/bin/sh
set -e

echo "[WorkmateOS] Running database migrations..."
alembic upgrade head

echo "[WorkmateOS] Starting backend server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
