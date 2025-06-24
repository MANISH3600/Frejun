from django.db import models
from django.utils import timezone

class User(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def is_child(self):
        return self.age < 10

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)

    def member_count(self):
        return self.members.count()

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_TYPES = (
        ('PRIVATE', 'Private Room'),
        ('CONFERENCE', 'Conference Room'),
        ('SHARED', 'Shared Desk'),
    )

    room_type = models.CharField(max_length=15, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.room_type} - Room {self.id}"
from datetime import date

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.TimeField()  # E.g., 10:00
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "date", "slot"],
                name="unique_room_booking_per_slot"
            )
        ]
    def __str__(self):
        who = self.team.name if self.team else self.user.name
        return f"{who} booked {self.room} at {self.slot}"
