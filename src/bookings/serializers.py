from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Booking, Room

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "number", "name", "price_per_night", "capacity")


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "user",
            "room",
            "start_date",
            "end_date",
            "status",
            "nights",
            "created_at",
        )


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "room", "start_date", "end_date")

    def validate(self, attrs: dict) -> dict:
        if attrs["end_date"] <= attrs["start_date"]:
            raise serializers.ValidationError("end date must be after start date")
        return attrs

    def create(self, validated_data: dict) -> Booking:
        user = self.context["request"].user
        room = validated_data["room"]

        with transaction.atomic():
            room = Room.objects.select_for_update().get(pk=room.pk)
            booking = Booking.objects.create(user=user, **validated_data)
        return booking


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user
