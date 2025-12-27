from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from bookings.models import Booking
from bookings.serializers import BookingSerializer, BookingCreateSerializer
from bookings.permissions import IsOwnerOrAdmin


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
    
    