from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'room',
        'rating',
        'is_approved',
        'created_at',
    )

    list_filter = (
        'rating',
        'is_approved',
    )