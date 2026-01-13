from datetime import date, timedelta

import pytest


@pytest.mark.django_db
def test_rooms_available_endpoint(api_client, room):
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=3)

    resp = api_client.get(
        "/api/rooms/",
        {"start_date": start, "end_date": end},
    )

    assert resp.status_code == 200
    assert any(r["id"] == room.id for r in resp.data)
