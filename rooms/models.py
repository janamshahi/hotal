from django.db import models


class RoomCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    max_guests = models.PositiveIntegerField(
        default=2
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Room Category"
        verbose_name_plural = "Room Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]

    category = models.ForeignKey(
        RoomCategory,
        on_delete=models.PROTECT,
        related_name='rooms'
    )

    room_number = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField(
        default=2
    )

    size = models.PositiveIntegerField(
        default=30,
        help_text="Room size in square meters"
    )

    bed_type = models.CharField(
        max_length=100,
        default="Double Bed"
    )

    floor = models.PositiveIntegerField(
        default=1
    )

    image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    is_featured = models.BooleanField(
        default=False
    )

    has_wifi = models.BooleanField(
        default=True
    )

    has_ac = models.BooleanField(
        default=True
    )

    has_tv = models.BooleanField(
        default=True
    )

    has_breakfast = models.BooleanField(
        default=False
    )

    has_balcony = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ['room_number']

    def __str__(self):
        return f"{self.room_number} - {self.name}"

    @property
    def is_available(self):
        return self.status == 'available'