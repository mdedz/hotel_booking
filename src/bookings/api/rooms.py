from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from bookings.api.filters import RoomFilter
from bookings.models import Room, Booking
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
    ordering_fields = ['price_per_night', 'capacity', 'number']
    search_fields = ['number', 'name']

    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request, *args, **kwargs) -> Response:
        """
        Retrieve availability details for a specific room.

        Returns:
            - List of disabled (already booked) dates
            - Room price per night

        Date handling:
            - Dates are returned as ISO-8601 strings
            - Computed using half-open intervals

        Use cases:
            - Booking calendar UI
            - Frontend date picker blocking

        Responses:
            200 OK:
                Availability information.
            400 Bad Request:
                Invalid date range.
        """
        start_d: date | None = parse_date(request.query_params.get('start_date') or "")
        end_d: date | None = parse_date(request.query_params.get('end_date') or "")

        if not start_d or not end_d or end_d <= start_d:
            return Response({'detail': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)

        overlapping_booked_rooms = Booking.objects.filter(
            status=Booking.STATUS_ACTIVE,
            start_date__lt=end_d,
            end_date__gt=start_d,
        ).values_list('room_id', flat=True)

        available_rooms = Room.objects.exclude(id__in=overlapping_booked_rooms)
        page = self.paginate_queryset(available_rooms)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, *args, **kwargs) -> Response:
        """
        Retrieve disabled dates and pricing for a specific room.

        Path Parameters:
            - pk: Room ID

        Query Parameters:
            - start_date: YYYY-MM-DD
            - end_date: YYYY-MM-DD

        Responses:
            - 200: Room availability details (disabled_dates and price_per_night)
            - 400: Invalid date range
        """
        room: Room = get_object_or_404(Room, pk=kwargs['pk'])
        
        start_d: date | None = parse_date(request.query_params.get('start_date') or "")
        end_d: date | None = parse_date(request.query_params.get('end_date') or "")

        if not start_d or not end_d or end_d <= start_d:
            return Response({'detail': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(
            room=room,
            status=Booking.STATUS_ACTIVE,
            start_date__lt=end_d,
            end_date__gt=start_d,
        )
        
        disabled_dates = set()
        
        for booking in bookings:
            current = max(booking.start_date, start_d)
            last = min(booking.end_date, end_d)
            
            while current < last:
                disabled_dates.add(current.isoformat())
                current += timedelta(days=1)
        
        return Response({
            "room_id": room.pk,
            "disabled_dates": sorted(disabled_dates),
            "price_per_night": str(room.price_per_night)
        }, status=status.HTTP_200_OK)
            