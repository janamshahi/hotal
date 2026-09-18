from django.contrib import admin

from .models import Hotel, Service


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone',
        'email',
        'is_active',
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
    )