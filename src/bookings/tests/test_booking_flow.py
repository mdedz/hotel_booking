import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from bookings.models import Room, Booking
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

@pytest.mark.django_db
def test_booking_and_availability():
    client = APIClient()
    user = User.objects.create_user(username='john', password='pass')
    room = Room.objects.create(number='101', name='Sea view', price_per_night=100, capacity=2)

    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=3)

    resp = client.post('/api/bookings/', {'room': room.id, 'start_date': start.isoformat(), 'end_date': end.isoformat()}, format='json')
    assert resp.status_code == 401

    resp = client.post('/api/auth/token/', {'username': 'john', 'password': 'pass'}, format='json')
    assert resp.status_code == 200
    token = resp.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    resp = client.post('/api/bookings/', {'room': room.id, 'start_date': start.isoformat(), 'end_date': end.isoformat()}, format='json')
    assert resp.status_code == 201

    resp2 = client.post('/api/bookings/', {'room': room.id, 'start_date': start.isoformat(), 'end_date': (end - timedelta(days=1)).isoformat()}, format='json')
    assert resp2.status_code == 400

    resp3 = client.get(f'/api/rooms/available?start_date={start.isoformat()}&end_date={end.isoformat()}')
    assert resp3.status_code == 200
    assert all(r['id'] != room.id for r in resp3.data)
