from django.shortcuts import render
from django.db.models import Avg
from django.contrib.auth.models import User

from .models import Hotel, Service

from rooms.models import (
    Room,
    RoomCategory
)

from reviews.models import Review


# =========================================================
# HOME PAGE
# =========================================================

def home(request):

    # =====================================================
    # ACTIVE HOTEL
    # =====================================================

    hotel = (
        Hotel.objects
        .filter(
            is_active=True
        )
        .first()
    )


    # =====================================================
    # AVAILABLE + ACTIVE ROOMS
    #
    # IMPORTANT:
    # room_number is taken directly from the Room model.
    # Therefore, when admin changes the room number,
    # the updated value will be displayed automatically.
    # =====================================================

    rooms = (
        Room.objects
        .filter(
            status='available',
            category__is_active=True
        )
        .select_related(
            'category'
        )
        .order_by(
            '-is_featured',
            'room_number'
        )[:6]
    )


    # =====================================================
    # ACTIVE SERVICES
    # =====================================================

    services = (
        Service.objects
        .filter(
            is_active=True
        )
        .order_by(
            'name'
        )
    )


    # =====================================================
    # ACTIVE ROOM CATEGORIES
    # =====================================================

    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            'name'
        )
    )


    # =====================================================
    # TOTAL ROOMS
    # =====================================================

    total_rooms = (
        Room.objects
        .count()
    )


    # =====================================================
    # AVAILABLE ROOMS
    # =====================================================

    available_rooms = (
        Room.objects
        .filter(
            status='available'
        )
        .count()
    )


    # =====================================================
    # ACTIVE ROOM CATEGORIES COUNT
    # =====================================================

    total_categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .count()
    )


    # =====================================================
    # TOTAL CUSTOMERS
    #
    # Excludes staff and superusers.
    # =====================================================

    total_customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .count()
    )


    # =====================================================
    # APPROVED REVIEWS
    # =====================================================

    reviews = (
        Review.objects
        .filter(
            is_approved=True
        )
        .select_related(
            'user',
            'room'
        )
        .order_by(
            '-created_at'
        )[:6]
    )


    # =====================================================
    # TOTAL APPROVED REVIEWS
    # =====================================================

    total_reviews = (
        Review.objects
        .filter(
            is_approved=True
        )
        .count()
    )


    # =====================================================
    # AVERAGE GUEST RATING
    # =====================================================

    average_rating = (
        Review.objects
        .filter(
            is_approved=True
        )
        .aggregate(
            average=Avg('rating')
        )['average']
    )


    # =====================================================
    # DEFAULT RATING
    # =====================================================

    if average_rating is None:

        average_rating = 0


    # =====================================================
    # HOME PAGE CONTEXT
    # =====================================================

    context = {

        # -------------------------------------------------
        # HOTEL
        # -------------------------------------------------

        'hotel': hotel,


        # -------------------------------------------------
        # ROOMS
        # -------------------------------------------------

        'rooms': rooms,


        # -------------------------------------------------
        # CATEGORIES
        # -------------------------------------------------

        'categories': categories,


        # -------------------------------------------------
        # SERVICES
        # -------------------------------------------------

        'services': services,


        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        'total_rooms': total_rooms,

        'available_rooms': available_rooms,

        'total_categories': total_categories,

        'total_customers': total_customers,


        # -------------------------------------------------
        # REVIEWS
        # -------------------------------------------------

        'reviews': reviews,

        'total_reviews': total_reviews,

        'average_rating': round(
            average_rating,
            1
        ),

    }


    # =====================================================
    # RENDER HOME PAGE
    # =====================================================

    return render(
        request,
        'home.html',
        context
    )
