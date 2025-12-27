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

echo "Creating default rooms"
python - <<END
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_booking.settings")
django.setup()
from bookings.models import Room

if not Room.objects.exists():
    Room.objects.bulk_create([
        Room(number="101", name="Deluxe Room", capacity=2, price_per_night=100),
        Room(number="102", name="Suite", capacity=4, price_per_night=250),
    ])
    print("Default rooms created")
else:
    print("Rooms already exist")
END


exec gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3
