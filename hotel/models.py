from django.db import models


class Hotel(models.Model):

    name = models.CharField(
        max_length=200,
        default="GrandStay Hotel"
    )

    tagline = models.CharField(
        max_length=300,
        default="Experience Comfort, Luxury & Elegance"
    )

    description = models.TextField(
        blank=True
    )

    address = models.CharField(
        max_length=300,
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    logo = models.ImageField(
        upload_to='hotel/',
        blank=True,
        null=True
    )

    hero_image = models.ImageField(
        upload_to='hotel/',
        blank=True,
        null=True
    )

    years_experience = models.PositiveIntegerField(
        default=15
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

    def __str__(self):
        return self.name


class Service(models.Model):

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    icon = models.CharField(
        max_length=100,
        default='bi bi-star'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name