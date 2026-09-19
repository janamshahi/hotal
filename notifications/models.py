from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):

    # =========================================================
    # NOTIFICATION TYPES
    # =========================================================

    NOTIFICATION_TYPES = [

        # General
        ("general", "General"),
        ("announcement", "Hotel Announcement"),

        # Hotel Offers
        ("offer", "Hotel Offer"),
        ("room_offer", "Room Offer"),
        ("special_deal", "Special Deal"),

        # Booking & Services
        ("booking", "Booking"),
        ("payment", "Payment"),
        ("checkout", "Checkout"),
        ("review", "Review"),
    ]

    # =========================================================
    # USER
    # =========================================================

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    # =========================================================
    # BOOKING
    # =========================================================

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    # =========================================================
    # NOTIFICATION DETAILS
    # =========================================================

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default="general"
    )

    # =========================================================
    # STATUS
    # =========================================================

    is_read = models.BooleanField(
        default=False
    )

    # =========================================================
    # DATE
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =========================================================
    # META
    # =========================================================

    class Meta:
        ordering = [
            "-created_at"
        ]

    # =========================================================
    # STRING
    # =========================================================

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.title}"
        )