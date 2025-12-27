from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect, get_object_or_404
from django.urls import path
from django.contrib import messages

from .models import Room, Booking

# Inline bookings inside Room for quick view
class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ('user', 'start_date', 'end_date', 'status', 'nights', 'created_at')
    can_delete = False
    show_change_link = True

# Custom filter to quickly see available rooms
class FreeRoomsFilter(admin.SimpleListFilter):
    title = 'Availability'
    parameter_name = 'available'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Available'),
            ('no', 'Fully booked'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            booked_ids = Booking.objects.filter(status=Booking.STATUS_ACTIVE).values_list('room_id', flat=True)
            return queryset.exclude(id__in=booked_ids)
        if self.value() == 'no':
            booked_ids = Booking.objects.filter(status=Booking.STATUS_ACTIVE).values_list('room_id', flat=True)
            return queryset.filter(id__in=booked_ids)
        return queryset

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'price_per_night', 'capacity', 'current_bookings', 'book_link')
    list_filter = ('capacity', FreeRoomsFilter)
    search_fields = ('number', 'name')
    inlines = [BookingInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Room Info', {'fields': ('number', 'name', 'capacity', 'price_per_night')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    # Count of active bookings for the room
    def current_bookings(self, obj):
        active = obj.bookings.filter(status=Booking.STATUS_ACTIVE).count()
        return format_html('<b>{}</b> active', active)
    current_bookings.short_description = 'Active Bookings'

    # Quick link to create booking directly from room
    def book_link(self, obj):
        url = reverse('admin:bookings_booking_add') + f'?room={obj.id}'
        return format_html('<a class="button" href="{}">Book</a>', url)
    book_link.short_description = 'Book Room'


@admin.action(description='Cancel selected bookings')
def cancel_bookings(modeladmin, request, queryset):
    updated = queryset.filter(status=Booking.STATUS_ACTIVE).update(status=Booking.STATUS_CANCELLED)
    modeladmin.message_user(request, f"{updated} booking(s) cancelled.")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room_link', 'start_date', 'end_date', 'status_colored', 'nights', 'created_at', 'cancel_button')
    list_filter = ('status', 'start_date', 'room')
    search_fields = ('user__username', 'room__number', 'room__name')
    readonly_fields = ('created_at', 'updated_at', 'nights')
    ordering = ('-start_date',)
    actions = [cancel_bookings]

    # Optimize queryset to reduce queries
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'room')

    # Link to room change page
    def room_link(self, obj):
        url = reverse('admin:bookings_room_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room)
    room_link.short_description = 'Room'

    # Display status with color
    def status_colored(self, obj):
        colors = {
            Booking.STATUS_ACTIVE: 'green',
            Booking.STATUS_CANCELLED: 'red'
        }
        return format_html('<b style="color:{}">{}</b>', colors.get(obj.status, 'black'), obj.status)
    status_colored.short_description = 'Status'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:booking_id>/cancel/',
                self.admin_site.admin_view(self.cancel_booking_view),
                name='bookings_booking_cancel',
            ),
        ]
        return custom_urls + urls

    def cancel_booking_view(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.status == Booking.STATUS_ACTIVE:
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            self.message_user(request, "Booking cancelled", messages.SUCCESS)
        else:
            self.message_user(request, "Booking already cancelled", messages.WARNING)

        return redirect('admin:bookings_booking_changelist')

    # Quick cancel button for active bookings
    def cancel_button(self, obj):
        if obj.status == Booking.STATUS_ACTIVE:
            url = reverse('admin:bookings_booking_cancel', args=[obj.id])
            return format_html('<a class="button" href="{}">Cancel</a>', url)
        return '-'

    cancel_button.short_description = 'Cancel Booking'
