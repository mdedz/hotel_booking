from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from bookings import drf as bookings_views, views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'rooms', bookings_views.RoomViewSet, basename='room')
router.register(r'bookings', bookings_views.BookingViewSet, basename='booking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', bookings_views.RegisterAPIView.as_view(), name='register'),
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('', views.rooms_list, name='rooms_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('book-room/<int:room_id>/', views.book_room_view, name='book_room'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
]