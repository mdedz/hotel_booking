from django_filters.rest_framework import FilterSet, filters

from bookings.models import Room, Booking


class RoomFilter(FilterSet):
    """
    Filter set for querying rooms.

    Supports filtering by price range, capacity, and availability dates.
    """
    min_price = filters.NumberFilter(
        field_name="price_per_night", lookup_expr="gte"
    )
    max_price = filters.NumberFilter(
        field_name="price_per_night", lookup_expr="lte"
    )
    capacity = filters.NumberFilter(
        field_name="capacity", lookup_expr="gte"
    )

    start_date = filters.DateFilter(method="filter_available")
    end_date = filters.DateFilter(method="filter_available")

    def filter_available(self, queryset, name, value):
        """
        Exclude rooms that are already booked in the provided date range.
        """
        data = self.data or {}
        
        start = data.get("start_date")
        end = data.get("end_date")

        if not start or not end:
            return queryset

        overlapping = Booking.objects.filter(
            status=Booking.STATUS_ACTIVE,
            start_date__lt=end,
            end_date__gt=start,
        ).values_list("room_id", flat=True)

        return queryset.exclude(id__in=overlapping)

    class Meta:
        model = Room
        fields = (
            "min_price",
            "max_price",
            "capacity",
            "start_date",
            "end_date",
        )
