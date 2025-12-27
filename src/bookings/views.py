from datetime import date
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

from urllib.parse import urlencode

from bookings.models import Booking, Room

def rooms_list(request) -> HttpResponse:
    rooms = Room.objects.all()
    params = request.GET.copy()
    
    # filters
    start = parse_date(params.get('start_date') or "")
    end = parse_date(params.get('end_date') or "")

    if start and end:
        if start >= end:
            return render(
                request,
                'bookings/rooms_list.html',
                {
                    'rooms': [],
                    'error': 'End date must be after start date',
                }
            )

        rooms = rooms.exclude(
            bookings__start_date__lt=end,
            bookings__end_date__gt=start,
            bookings__status=Booking.STATUS_ACTIVE,
        )
    
    if params.get('min_price'):
        rooms = rooms.filter(price_per_night__gte=params['min_price'])
    if params.get('max_price'):
        rooms = rooms.filter(price_per_night__lte=params['max_price'])
    if params.get('capacity'):
        rooms = rooms.filter(capacity__gte=params['capacity'])
    
    # sorting
    ordering = params.get('ordering')
    allowed = {'price_per_night', '-price_per_night', 'capacity', '-capacity'}

    if ordering in allowed:
        rooms = rooms.order_by(ordering)

    def sort_url(value) -> str:
        q = params.copy()
        q['ordering'] = value
        return '?' + urlencode(q)

    return render(request, 'bookings/rooms_list.html', {
        'rooms': rooms,
        'sort_url': sort_url,
        'current_ordering': ordering,
    })
    
def register_view(request) -> HttpResponseRedirect | HttpResponse:
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('rooms_list')
    else:
        form = UserCreationForm()
    return render(request, 'bookings/register.html', {'form': form})

def login_view(request) -> HttpResponseRedirect | HttpResponse:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('rooms_list')
    else:
        form = AuthenticationForm()
    return render(request, 'bookings/login.html', {'form': form})

def logout_view(request) -> HttpResponseRedirect:
    logout(request)
    return redirect('rooms_list')

@login_required
def my_bookings_view(request) -> HttpResponse:
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def book_room_view(request, room_id) -> HttpResponse | HttpResponseRedirect:
    room: Room = get_object_or_404(Room, id=room_id)
    guests_range = range(1, room.capacity + 1)
    if request.method == 'POST':
        start: date | None = parse_date(request.POST.get('start_date') or "")
        end: date | None = parse_date(request.POST.get('end_date') or "")
        if not start or not end:
            return render(request, 'bookings/book_room.html', {'room': room, 'guests_range': guests_range, 'error': 'Invalid dates'})
        try:
            Booking.objects.create(user=request.user, room=room, start_date=start, end_date=end)
            return redirect('my_bookings')
        except ValidationError as e:
            if hasattr(e, "message_dict"):
                # __all__ → 'text'
                error = " ".join(
                    msg for msgs in e.message_dict.values() for msg in msgs
                )
            else:
                error = " ".join(e.messages)

            return render(
                request,
                'bookings/book_room.html',
                {
                    'room': room,
                    'guests_range': guests_range,
                    'error': error,
                }
            )
        except Exception:
            return render(request, 'bookings/book_room.html', {'room': room, 'guests_range': guests_range, 'error': 'Could not create booking. Try again.'})
    return render(request, 'bookings/book_room.html', {'room': room, 'guests_range': guests_range})

def cancel_booking_view(request, booking_id):
    if request.user.is_staff:
        booking: Booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking: Booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.cancel()
        return redirect('my_bookings')
    return redirect('my_bookings')