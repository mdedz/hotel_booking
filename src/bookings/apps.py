from django.apps import AppConfig
from django.db.models.signals import post_migrate


class BookingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"

    def ready(self):
        from .models import Room

        def create_default_rooms(sender, **kwargs):
            if Room.objects.exists():
                return

            Room.objects.bulk_create(
                [
                    Room(
                        number="101",
                        name="Deluxe Room",
                        capacity=2,
                        price_per_night=100,
                    ),
                    Room(
                        number="102",
                        name="Suite",
                        capacity=4,
                        price_per_night=250,
                    ),
                ]
            )

        post_migrate.connect(create_default_rooms, sender=self)
