import pytest
from datetime import date, timedelta
from bookings.serializers import BookingCreateSerializer


@pytest.mark.django_db
def test_booking_serializer_validates_date_order(room, user):
    data = {
        "room": room.id,
        "start_date": date.today(),
        "end_date": date.today(),
    }

    serializer = BookingCreateSerializer(
        data=data, context={"request": type("R", (), {"user": user})()}
    )

    assert not serializer.is_valid()
