from django.contrib.auth.models import User
from django.db import models

from rooms.models import Room


class Booking(models.Model):

    # =========================================================
    # BOOKING STATUS
    # =========================================================

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]

    # =========================================================
    # PAYMENT STATUS
    # =========================================================

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # =========================================================
    # CUSTOMER
    # =========================================================

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # =========================================================
    # ROOM
    # =========================================================

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    # =========================================================
    # CHECK-IN
    # =========================================================

    check_in = models.DateField(
        verbose_name="Check-in Date"
    )

    check_in_time = models.TimeField(
        default="14:00",
        verbose_name="Check-in Time"
    )

    # =========================================================
    # CHECK-OUT
    # =========================================================

    check_out = models.DateField(
        verbose_name="Check-out Date"
    )

    check_out_time = models.TimeField(
        default="12:00",
        verbose_name="Check-out Time"
    )

    # =========================================================
    # GUESTS
    # =========================================================

    guests = models.PositiveIntegerField(
        default=1
    )

    # =========================================================
    # PAYMENT / TOTAL
    # =========================================================

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # =========================================================
    # BOOKING STATUS
    # =========================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # =========================================================
    # PAYMENT STATUS
    # =========================================================

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    # =========================================================
    # SPECIAL REQUEST
    # =========================================================

    special_request = models.TextField(
        blank=True
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =========================================================
    # CHECK-IN DATETIME
    # =========================================================

    @property
    def check_in_datetime(self):
        from datetime import datetime

        return datetime.combine(
            self.check_in,
            self.check_in_time
        )

    # =========================================================
    # CHECK-OUT DATETIME
    # =========================================================

    @property
    def check_out_datetime(self):
        from datetime import datetime

        return datetime.combine(
            self.check_out,
            self.check_out_time
        )

    # =========================================================
    # TOTAL NIGHTS
    # =========================================================

    @property
    def total_nights(self):
        return (
            self.check_out - self.check_in
        ).days

    # =========================================================
    # STRING
    # =========================================================

    def __str__(self):

        return (
            f"Booking #{self.id} - "
            f"{self.user.username} - "
            f"{self.room.room_number}"
        )