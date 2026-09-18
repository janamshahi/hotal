from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'booking',
        'amount',
        'method',
        'status',
        'paid_at',
    )

    list_filter = (
        'method',
        'status',
    )