from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiResponse

from bookings.serializers import RegisterSerializer


User = get_user_model()

@extend_schema(
    summary="User registration",
    description=(
        "Creates a new user account.\n\n"
        "This endpoint is intended for public registration flows and "
        "does not require authentication."
    ),
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
        400: OpenApiResponse(
            description="Validation error"
        ),
    },
    tags=["Authentication"]
)
class RegisterAPIView(generics.CreateAPIView):
    """
    Public user registration endpoint.

    Responsibilities:
        - Validates user credentials
        - Creates a new user instance
        - Returns serialized user data

    Security considerations:
        - Password hashing is handled by the serializer
        - No sensitive fields are returned in the response
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]