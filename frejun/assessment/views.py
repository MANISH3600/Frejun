from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, Team, Room, Booking
from .serializers import BookingSerializer, RoomSerializer ,UserSerializer, TeamSerializer

from .pagination import CustomBookingPagination

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, F
from datetime import datetime
from .models import Room, Booking, User, Team

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

booking_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['room_type', 'slot', 'date'],
    properties={
        'room_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['PRIVATE', 'CONFERENCE', 'SHARED']),
        'slot': openapi.Schema(type=openapi.TYPE_STRING, example="15:00"),
        'date': openapi.Schema(type=openapi.TYPE_STRING, example="2025-06-25"),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID (for PRIVATE/SHARED)"),
        'team': openapi.Schema(type=openapi.TYPE_INTEGER, description="Team ID (for CONFERENCE)")
    }
)

@swagger_auto_schema(method='post', request_body=booking_request_body)
@api_view(['POST'])
@transaction.atomic
def book_room(request):
    data = request.data
    slot_str = data.get('slot')
    date_str = data.get('date')
    room_type = data.get('room_type')
    user_id = data.get('user')
    team_id = data.get('team')

    if not slot_str or not date_str or not room_type:
        return Response({'error': 'Missing required fields'}, status=400)

    try:
        slot = datetime.strptime(slot_str, "%H:%M").time()
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({'error': 'Invalid date or time format'}, status=400)

    try:
        # PRIVATE room booking
        if room_type == 'PRIVATE' and user_id:
            user = User.objects.get(id=user_id)

            if Booking.objects.filter(user=user, date=date, slot=slot).exists():
                return Response({'error': 'User already has a booking for this slot'}, status=400)

            room = Room.objects.select_for_update().filter(
                room_type='PRIVATE'
            ).exclude(
                booking__date=date,
                booking__slot=slot
            ).first()

            if not room:
                return Response({'error': 'No available private room for the selected slot'}, status=400)

            booking = Booking.objects.create(room=room, user=user, slot=slot, date=date)
            return Response({'booking_id': booking.id})

        # CONFERENCE room booking
        elif room_type == 'CONFERENCE' and team_id:
            team = Team.objects.get(id=team_id)

            if team.members.count() < 3:
                return Response({'error': 'Team must have at least 3 members'}, status=400)

            if Booking.objects.filter(team=team, date=date, slot=slot).exists():
                return Response({'error': 'Team already has a booking for this slot'}, status=400)

            room = Room.objects.select_for_update().filter(
                room_type='CONFERENCE'
            ).exclude(
                booking__date=date,
                booking__slot=slot
            ).first()

            if not room:
                return Response({'error': 'No available conference room for the selected slot'}, status=400)

            booking = Booking.objects.create(room=room, team=team, slot=slot, date=date)
            return Response({'booking_id': booking.id})

        # SHARED desk booking
        elif room_type == 'SHARED' and user_id:
            user = User.objects.get(id=user_id)

            if Booking.objects.filter(user=user, date=date, slot=slot).exists():
                return Response({'error': 'User already has a booking for this slot'}, status=400)

            room = Room.objects.select_for_update().filter(
                room_type='SHARED'
            ).annotate(
                booked_count=Count('booking', filter=Q(booking__date=date, booking__slot=slot))
            ).filter(
                booked_count__lt=F('capacity')
            ).first()

            if not room:
                return Response({'error': 'No available shared desk for the selected slot'}, status=400)

            booking = Booking.objects.create(room=room, user=user, slot=slot, date=date)
            return Response({'booking_id': booking.id})

        return Response({'error': 'Invalid data or room type'}, status=400)

    except ObjectDoesNotExist as e:
        return Response({'error': str(e)}, status=400)
    except IntegrityError:
        return Response({'error': 'Booking conflict occurred. Please try again.'}, status=409)
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, status=500)

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'booking_id',
            openapi.IN_PATH,
            description="Booking ID to cancel",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={200: "Booking cancelled successfully", 404: "Booking not found"}
)
@api_view(['POST'])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.delete()
        return Response({'message': 'Booking cancelled successfully'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)


class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.select_related('room', 'user', 'team').all()
    serializer_class = BookingSerializer
    pagination_class = CustomBookingPagination



@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'date',
            openapi.IN_QUERY,
            description="Booking date in YYYY-MM-DD format",
            type=openapi.TYPE_STRING,
            required=True,
            example="2025-06-25"
        ),
        openapi.Parameter(
            'slot',
            openapi.IN_QUERY,
            description="Booking slot in HH:MM format",
            type=openapi.TYPE_STRING,
            required=True,
            example="15:00"
        )
    ],
    responses={200: "List of available rooms"}
)
@api_view(['GET'])
def available_rooms(request):
    date_str = request.GET.get('date')
    slot_str = request.GET.get('slot')

    if not date_str or not slot_str:
        return Response({'error': 'Provide date and slot as query params'}, status=400)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    slot = datetime.strptime(slot_str, "%H:%M").time()

    available = []
    for room in Room.objects.all():
        bookings = Booking.objects.filter(room=room, date=date, slot=slot)
        if room.room_type == 'SHARED':
            if bookings.count() < room.capacity:
                available.append(room)
        else:
            if not bookings.exists():
                available.append(room)

    serializer = RoomSerializer(available, many=True)
    return Response(serializer.data)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TeamCreateView(generics.CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer