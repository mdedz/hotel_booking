from datetime import date, timedelta

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_authenticated_user_can_create_booking(auth_client, room):
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=2)

    resp = auth_client.post(
        reverse("booking-list"),
        {"room": room.id, "start_date": start, "end_date": end},
        format="json",
    )

    assert resp.status_code == 201
