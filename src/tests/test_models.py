from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Booking


@pytest.mark.django_db
def test_booking_invalid_date_range(user, room):
    start = date.today() + timedelta(days=5)
    end = start

    booking = Booking(
        user=user,
        room=room,
        start_date=start,
        end_date=end,
    )

    with pytest.raises(ValidationError):
        booking.full_clean()


@pytest.mark.django_db
def test_booking_overlap_not_allowed(user, room, booking):
    overlapping = Booking(
        user=user,
        room=room,
        start_date=booking.start_date + timedelta(days=1),
        end_date=booking.end_date,
    )

    with pytest.raises(ValidationError):
        overlapping.full_clean()
