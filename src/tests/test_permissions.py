import pytest
from rest_framework.test import APIRequestFactory

from bookings.permissions import IsOwnerOrAdmin


@pytest.mark.django_db
def test_owner_has_permission(user, booking):
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = user

    perm = IsOwnerOrAdmin()
    assert perm.has_object_permission(request, None, booking)


@pytest.mark.django_db
def test_admin_has_permission(admin_user, booking):
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = admin_user

    perm = IsOwnerOrAdmin()
    assert perm.has_object_permission(request, None, booking)
