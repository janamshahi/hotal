from django.contrib import admin

from .models import Room, RoomCategory


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'max_guests',
        'is_active',
    )

    list_filter = (
        'is_active',
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'room_number',
        'name',
        'category',
        'price',
        'capacity',
        'status',
        'is_featured',
    )

    list_filter = (
        'status',
        'is_featured',
        'category',
    )

    search_fields = (
        'room_number',
        'name',
    )