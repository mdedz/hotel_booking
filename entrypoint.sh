#!/bin/sh

set -e

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "Waiting for database..."
  sleep 2
done

echo "Migrating database"
python src/manage.py migrate

echo "Creating superuser (for test)"
python src/manage.py createsu

exec gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3