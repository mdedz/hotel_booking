from datetime import date, timedelta

import pytest

from bookings.api.filters import RoomFilter
from bookings.models import Booking


@pytest.mark.django_db
def test_room_filter_excludes_booked_rooms(room, user):
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=2)

    Booking.objects.create(
        user=user,
        room=room,
        start_date=start,
        end_date=end,
    )

    qs = RoomFilter(
        data={"start_date": start, "end_date": end},
        queryset=type(room).objects.all(),
    ).qs

    assert room not in qs
