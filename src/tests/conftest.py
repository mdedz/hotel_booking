from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookings.models import Booking, Room

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="pass")


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", password="admin", email="admin@test.com"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def room(db):
    return Room.objects.create(
        number="101",
        name="Deluxe",
        capacity=2,
        price_per_night=100,
    )


@pytest.fixture
def booking(user, room):
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=3)
    return Booking.objects.create(
        user=user,
        room=room,
        start_date=start,
        end_date=end,
    )
