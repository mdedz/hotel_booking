import pytest
from datetime import date, timedelta


@pytest.mark.django_db
def test_full_booking_flow(api_client, user, room):
    api_client.force_authenticate(user=user)

    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=3)

    create = api_client.post(
        "/api/bookings/",
        {"room": room.id, "start_date": start, "end_date": end},
        format="json",
    )
    assert create.status_code == 201

    cancel = api_client.post(f"/api/bookings/{create.data['id']}/cancel/")
    assert cancel.status_code == 200
