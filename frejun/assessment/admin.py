from django.contrib import admin
from .models import User, Team, Room, Booking


from django.contrib import admin
from .models import Room

class RoomAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only on create
            count = Room.objects.filter(room_type=obj.room_type).count()
            limit = {
                'PRIVATE': 8,
                'CONFERENCE': 4,
                'SHARED': 3
            }.get(obj.room_type, None)

            if limit and count >= limit:
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Cannot create more than {limit} rooms of type {obj.room_type}")
        
        super().save_model(request, obj, form, change)

admin.site.register(Room, RoomAdmin)
admin.site.register(User)
admin.site.register(Team)

admin.site.register(Booking)
