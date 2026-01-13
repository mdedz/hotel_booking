from datetime import date
from urllib.parse import urlencode

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from bookings.models import Booking, Room


def rooms_list(request) -> HttpResponse:
    """
    HTML view for listing rooms with optional availability filtering.

    Business rules are enforced at the model level.
    This view only applies query filters and handles user input.
    """
    rooms = Room.objects.all()
    params = request.GET.copy()

    start = parse_date(params.get("start_date") or "")
    end = parse_date(params.get("end_date") or "")

    if start and end:
        rooms = rooms.exclude(
            bookings__status=Booking.STATUS_ACTIVE,
            bookings__start_date__lt=end,
            bookings__end_date__gt=start,
        )

    if params.get("min_price"):
        rooms = rooms.filter(price_per_night__gte=params["min_price"])
    if params.get("max_price"):
        rooms = rooms.filter(price_per_night__lte=params["max_price"])
    if params.get("capacity"):
        rooms = rooms.filter(capacity__gte=params["capacity"])

    ordering = params.get("ordering")
    allowed = {"price_per_night", "-price_per_night", "capacity", "-capacity"}
    if ordering in allowed:
        rooms = rooms.order_by(ordering)

    def sort_url(value: str) -> str:
        q = params.copy()
        q["ordering"] = value
        return "?" + urlencode(q)

    return render(
        request,
        "bookings/rooms_list.html",
        {
            "rooms": rooms,
            "sort_url": sort_url,
            "current_ordering": ordering,
        },
    )


def register_view(request) -> HttpResponse | HttpResponseRedirect:
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("rooms_list")
    else:
        form = UserCreationForm()

    return render(request, "bookings/register.html", {"form": form})


def login_view(request) -> HttpResponse | HttpResponseRedirect:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("rooms_list")
    else:
        form = AuthenticationForm()

    return render(request, "bookings/login.html", {"form": form})


def logout_view(request) -> HttpResponseRedirect:
    logout(request)
    return redirect("rooms_list")


@login_required
def my_bookings_view(request) -> HttpResponse:
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})


@login_required
def book_room_view(request, room_id: int) -> HttpResponse | HttpResponseRedirect:
    """
    HTML booking creation view.

    Validation logic lives in the Booking model.
    This view only handles user input and error presentation.
    """
    room = get_object_or_404(Room, id=room_id)
    guests_range = range(1, room.capacity + 1)

    if request.method == "POST":
        start: date | None = parse_date(request.POST.get("start_date") or "")
        end: date | None = parse_date(request.POST.get("end_date") or "")

        if not start or not end:
            return render(
                request,
                "bookings/book_room.html",
                {
                    "room": room,
                    "guests_range": guests_range,
                    "error": "Invalid dates",
                },
            )

        try:
            Booking.objects.create(
                user=request.user,
                room=room,
                start_date=start,
                end_date=end,
            )
            return redirect("my_bookings")

        except ValidationError as e:
            if hasattr(e, "message_dict"):
                error = " ".join(
                    msg for msgs in e.message_dict.values() for msg in msgs
                )
            else:
                error = " ".join(e.messages)

            return render(
                request,
                "bookings/book_room.html",
                {
                    "room": room,
                    "guests_range": guests_range,
                    "error": error,
                },
            )

    return render(
        request,
        "bookings/book_room.html",
        {
            "room": room,
            "guests_range": guests_range,
        },
    )


@login_required
def cancel_booking_view(request, booking_id: int) -> HttpResponseRedirect:
    if request.user.is_staff:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        booking.cancel(by_user=request.user)

    return redirect("my_bookings")
