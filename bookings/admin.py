from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'room',
        'check_in',
        'check_out',
        'total_amount',
        'status',
        'payment_status',
    )

    list_filter = (
        'status',
        'payment_status',
    )

    search_fields = (
        'user__username',
        'room__room_number',
    )