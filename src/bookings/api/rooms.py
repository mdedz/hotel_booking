from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from bookings.api.filters import RoomFilter
from bookings.models import Room
from bookings.serializers import RoomSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Room Management Endpoint.

    Provides read-only access to rooms and their availability.

    list / retrieve:
        Retrieve all rooms or a single room by ID.

    available:
        Retrieve rooms available within a given date range.

    availability:
        Retrieve booked dates and pricing for a specific room.
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (AllowAny,)

    filterset_class = RoomFilter
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    ordering_fields = ["price_per_night", "capacity", "number"]
    search_fields = ["number", "name"]
