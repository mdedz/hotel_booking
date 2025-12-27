import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_registration(api_client):
    resp = api_client.post(
        reverse("api-register"),
        {"username": "newuser", "password": "StrongPass123"},
        format="json",
    )

    assert resp.status_code == 201
    assert User.objects.filter(username="newuser").exists()
