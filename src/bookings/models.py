from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

User: type[AbstractUser] = get_user_model()


class Room(models.Model):
    number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["number"]

    def __str__(self) -> str:
        return f"{self.number} {self.name or ''}".strip()


class Booking(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["room", "start_date", "end_date"]),
        ]

    def clean(self) -> None:
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "end_date must be after start_date"})

        overlapping = (
            Booking.objects.filter(
                room=self.room,
                status=Booking.STATUS_ACTIVE,
            )
            .exclude(pk=self.pk)
            .filter(
                start_date__lt=self.end_date,
                end_date__gt=self.start_date,
            )
        )
        if overlapping.exists():
            raise ValidationError("Room is already booked for the given dates")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def nights(self) -> int:
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def cancel(self, by_user: Optional[type[AbstractUser]] = None) -> None:
        self.status = self.STATUS_CANCELLED
        self.save()
