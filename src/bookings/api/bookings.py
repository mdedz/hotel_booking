from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from bookings.api.filters import BookingFilter
from bookings.models import Booking
from bookings.permissions import IsOwnerOrAdmin
from bookings.serializers import BookingCreateSerializer, BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    Booking Management Endpoint.

    Provides full CRUD operations for bookings and additional actions:

    list:
        List all bookings. Only accessible by staff users.

    retrieve:
        Retrieve a single booking by its ID.

    create:
        Create a new booking for authenticated users.

    my:
        Retrieve all bookings for the authenticated user.

    update / partial_update:
        Update an existing booking. Only allowed for the owner or admin.

    destroy:
        Delete a booking. Only allowed for the owner or admin.

    cancel:
        Cancel a booking. Only allowed for the owner or admin.
    """

    queryset = Booking.objects.select_related("room", "user").all()
    filterset_class = BookingFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ("start_date", "end_date", "created_at")

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        if self.action in ("create", "my"):
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy", "cancel"):
            return [IsOwnerOrAdmin()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    @action(detail=False, methods=["get"])
    def my(self, request):
        """
        Retrieve bookings for the authenticated user.

        GET:
            Returns all bookings created by the current user.

        Permissions:
            IsAuthenticated
        """
        qs = self.filter_queryset(self.get_queryset().filter(user=request.user))
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        Cancel a booking.

        POST:
            Marks a booking as cancelled.
            Only the booking owner or staff can perform this action.

        Path Parameters:
            - pk: Booking ID

        Responses:
            - 200: Booking successfully cancelled.
            - 403: Not allowed.
        """
        booking = self.get_object()
        booking.cancel(by_user=request.user)
        return Response({"detail": "cancelled"})
