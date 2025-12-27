from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

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

    my_bookings:
        Retrieve all bookings for the authenticated user.

    update / partial_update:
        Update an existing booking. Only allowed for the owner or admin.

    destroy:
        Delete a booking. Only allowed for the owner or admin.

    cancel:
        Cancel a booking. Only allowed for the owner or admin.
    """

    queryset = Booking.objects.select_related("room", "user").all()
    filterset_fields = ("status", "room")
    ordering_fields = ("start_date", "end_date")

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        if self.action in ("create", "my_bookings", "cancel"):
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsOwnerOrAdmin()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="my",
        permission_classes=[IsAuthenticated],
    )
    def my_bookings(self, request):
        """
        Retrieve bookings for the authenticated user.

        GET:
            Returns all bookings created by the current user.

        Permissions:
            IsAuthenticated
        """
        qs = Booking.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        serializer = BookingSerializer(page or qs, many=page is not None)
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new booking.

        POST:
            Creates a booking for the authenticated user using provided room and dates.

        Request Body:
            - room: integer (room ID)
            - start_date: string (YYYY-MM-DD)
            - end_date: string (YYYY-MM-DD)

        Responses:
            - 201: Booking created successfully.
            - 400: Invalid data.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

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
        if not (request.user.is_staff or booking.user == request.user):
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        booking.cancel(by_user=request.user)
        return Response({"detail": "cancelled"}, status=status.HTTP_200_OK)
