from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.book_room, name='bookings_create'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel-booking'),
    path('bookings/all/', views.BookingListView.as_view(), name='list-bookings'),
    path('rooms/available/', views.available_rooms, name='available-rooms'),
    path('users/', views.UserCreateView.as_view(), name='create-user'),
    path('teams/', views.TeamCreateView.as_view(), name='create-team'),
]
