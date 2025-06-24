from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from assessment.models import Room, User, Team, Booking
from datetime import date, time


class BookingAPITest(APITestCase):
    def setUp(self):
        # Create rooms
        for _ in range(8):
            Room.objects.create(room_type='PRIVATE', capacity=1)
        for _ in range(4):
            Room.objects.create(room_type='CONFERENCE', capacity=10)
        for _ in range(3):
            Room.objects.create(room_type='SHARED', capacity=4)

        # Create users
        self.user1 = User.objects.create(name="Alice", age=25, gender='F')
        self.user2 = User.objects.create(name="Bob", age=30, gender='M')
        self.user3 = User.objects.create(name="Charlie", age=35, gender='M')

        # Create team
        self.team = Team.objects.create(name="Team Alpha")
        self.team.members.set([self.user1, self.user2, self.user3])

        self.booking_url = reverse('bookings_create')  # or hardcode: /api/v1/bookings/
        self.cancel_url = lambda booking_id: f"/api/v1/cancel/{booking_id}/"
        self.available_url = "/api/v1/rooms/available/?date=2025-06-25&slot=10:00"

    def test_private_room_booking(self):
        response = self.client.post(self.booking_url, {
            "room_type": "PRIVATE",
            "user": self.user1.id,
            "slot": "10:00",
            "date": "2025-06-25"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("booking_id", response.data)

    def test_shared_desk_booking(self):
        response = self.client.post(self.booking_url, {
            "room_type": "SHARED",
            "user": self.user2.id,
            "slot": "11:00",
            "date": "2025-06-25"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_conference_room_booking(self):
        response = self.client.post(self.booking_url, {
            "room_type": "CONFERENCE",
            "team": self.team.id,
            "slot": "12:00",
            "date": "2025-06-25"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_double_book(self):
        self.client.post(self.booking_url, {
            "room_type": "PRIVATE",
            "user": self.user1.id,
            "slot": "13:00",
            "date": "2025-06-25"
        }, format='json')

        response = self.client.post(self.booking_url, {
            "room_type": "PRIVATE",
            "user": self.user1.id,
            "slot": "13:00",
            "date": "2025-06-25"
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_cancel_booking(self):
        booking_response = self.client.post(self.booking_url, {
            "room_type": "PRIVATE",
            "user": self.user3.id,
            "slot": "14:00",
            "date": "2025-06-25"
        }, format='json')

        booking_id = booking_response.data["booking_id"]
        response = self.client.post(self.cancel_url(booking_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_check_available_rooms(self):
        response = self.client.get(self.available_url)
        self.assertEqual(response.status_code, 200)
        room_types = [room['room_type'] for room in response.data]
        self.assertIn("PRIVATE", room_types)
