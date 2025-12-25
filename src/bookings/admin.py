from django.contrib import admin
from .models import Room, Booking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'price_per_night', 'capacity')
    search_fields = ('number', 'name')
    list_filter = ('capacity',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('user__username', 'room__number')
    readonly_fields = ('created_at', 'updated_at')
