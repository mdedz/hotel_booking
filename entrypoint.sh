#!/bin/sh

set -e

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "Waiting for database..."
  sleep 2
done

python src/manage.py migrate

exec gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3