from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Create superuser from env if it does not exist"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", default="")

        if not username or not password:
            self.stdout.write("Superuser env vars not set, skipping")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("Superuser already exists")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write("Superuser created")
