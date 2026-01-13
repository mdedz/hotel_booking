from datetime import date

import pytest
from rest_framework import serializers

from bookings.serializers import BookingCreateSerializer


@pytest.mark.django_db
def test_booking_serializer_rejects_invalid_date_order_on_save(room, user):
    data = {
        "room": room.id,
        "start_date": date.today(),
        "end_date": date.today(),
    }

    serializer = BookingCreateSerializer(
        data=data,
        context={"request": type("R", (), {"user": user})()},
    )

    assert serializer.is_valid()

    with pytest.raises(serializers.ValidationError):
        serializer.save()
