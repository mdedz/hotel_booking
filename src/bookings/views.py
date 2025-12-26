from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from bookings.models import Booking, Room

def rooms_list(request):
    rooms = Room.objects.all()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    capacity = request.GET.get('capacity')
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)
    return render(request, 'bookings/rooms_list.html', {'rooms': rooms})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('rooms_list')
    else:
        form = UserCreationForm()
    return render(request, 'bookings/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('rooms_list')
    else:
        form = AuthenticationForm()
    return render(request, 'bookings/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('rooms_list')

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def book_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    guests_range = range(1, room.capacity + 1)
    if request.method == 'POST':
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            booking = Booking.objects.create(user=request.user, room=room, start_date=start, end_date=end)
            return redirect('my_bookings')
        except Exception as e:
            return render(request, 'bookings/book_room.html', {'room': room, 'guests_range': guests_range, 'error': str(e)})
    
    return render(request, 'bookings/book_room.html', {'room': room, 'guests_range': guests_range})

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.cancel()
        return redirect('my_bookings')
    return redirect('my_bookings')
