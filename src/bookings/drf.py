from __future__ import annotations
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics

from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date

from .models import Room, Booking
from .serializers import RegisterSerializer, RoomSerializer, BookingSerializer, BookingCreateSerializer
from .permissions import IsOwnerOrAdmin


class RoomFilter(FilterSet):
    min_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    capacity = filters.NumberFilter(field_name='capacity')

    class Meta:
        model = Room
        fields = ['min_price', 'max_price', 'capacity']


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (AllowAny,)
    filterset_class = RoomFilter
    ordering_fields = ['price_per_night', 'capacity', 'number']
    search_fields = ['number', 'name']

    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request, *args, **kwargs):
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')
        if not start or not end:
            return Response({'detail': 'start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        start_d = parse_date(start)
        end_d = parse_date(end)
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


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('room', 'user').all()
    filterset_fields = ('status', 'room')
    ordering_fields = ('start_date', 'end_date')

    def get_permissions(self):
        if self.action in ('create', 'my_bookings', 'cancel'):
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwnerOrAdmin()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return super().list(request, *args, **kwargs)
        return Response({'detail': 'Use /api/bookings/my/ to view your bookings or authenticate as staff'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], url_path='my', permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        qs = Booking.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        serializer = BookingSerializer(page or qs, many=page is not None)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if not (request.user.is_staff or booking.user == request.user):
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        booking.cancel(by_user=request.user)
        return Response({'detail': 'cancelled'}, status=status.HTTP_200_OK)
    
    
User = get_user_model()
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]