from datetime import date

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Room, RoomCategory


# =========================================================
# CUSTOMER ROOM LIST
# =========================================================
# Features:
# - Display available rooms
# - Search rooms
# - Filter by category
# - Filter by number of guests
# - Filter by check-in / check-out dates
# - Exclude rooms already booked for selected dates
# =========================================================

def room_list(request):

    # =====================================================
    # GET SEARCH / FILTER VALUES
    # =====================================================

    search = request.GET.get(
        'search',
        ''
    ).strip()

    category_id = request.GET.get(
        'category',
        ''
    ).strip()

    check_in = request.GET.get(
        'check_in',
        ''
    ).strip()

    check_out = request.GET.get(
        'check_out',
        ''
    ).strip()

    guests = request.GET.get(
        'guests',
        ''
    ).strip()


    # =====================================================
    # BASE ROOM QUERY
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
        .prefetch_related(
            'reviews'
        )
        .order_by(
            '-is_featured',
            'room_number'
        )
    )


    # =====================================================
    # SEARCH BY ROOM NAME / NUMBER / DESCRIPTION
    # =====================================================

    if search:

        rooms = rooms.filter(
            Q(name__icontains=search)
            |
            Q(room_number__icontains=search)
            |
            Q(description__icontains=search)
            |
            Q(category__name__icontains=search)
        )


    # =====================================================
    # FILTER BY CATEGORY
    # =====================================================

    if category_id:

        try:

            category_id = int(category_id)

            rooms = rooms.filter(
                category_id=category_id
            )

        except (ValueError, TypeError):

            category_id = ''


    # =====================================================
    # FILTER BY NUMBER OF GUESTS
    # =====================================================

    guests_value = None

    if guests:

        try:

            guests_value = int(guests)

            if guests_value > 0:

                rooms = rooms.filter(
                    capacity__gte=guests_value
                )

        except (ValueError, TypeError):

            guests_value = None


    # =====================================================
    # DATE AVAILABILITY FILTER
    # =====================================================
    #
    # A room is unavailable when an existing booking overlaps
    # with the requested check-in / check-out dates.
    #
    # Overlap condition:
    #
    # existing.check_in < requested.check_out
    # AND
    # existing.check_out > requested.check_in
    #
    # Cancelled bookings are ignored.
    # =====================================================

    valid_dates = False

    if check_in and check_out:

        try:

            check_in_date = date.fromisoformat(
                check_in
            )

            check_out_date = date.fromisoformat(
                check_out
            )

            if check_out_date > check_in_date:

                valid_dates = True

        except ValueError:

            valid_dates = False


    if valid_dates:

        from bookings.models import Booking

        booked_room_ids = (
            Booking.objects
            .filter(
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            )
            .exclude(
                status='cancelled'
            )
            .values_list(
                'room_id',
                flat=True
            )
        )

        rooms = rooms.exclude(
            id__in=booked_room_ids
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
    # ROOM COUNT
    # =====================================================

    room_count = rooms.count()


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'rooms': rooms,

        'categories': categories,

        # Search value
        'search': search,

        # Selected category
        'selected_category': category_id,

        # Dates
        'check_in': check_in,

        'check_out': check_out,

        # Guests
        'guests': guests,

        # Parsed guest value
        'guests_value': guests_value,

        # Result count
        'room_count': room_count,

        # Whether valid dates were supplied
        'valid_dates': valid_dates,

    }


    # =====================================================
    # RENDER ROOM LIST
    # =====================================================

    return render(
        request,
        'rooms/room_list.html',
        context
    )


# =========================================================
# CUSTOMER ROOM DETAIL
# =========================================================
# Features:
# - Display complete room information
# - Display approved reviews
# - Display related rooms
# - Only active/available rooms are shown
# =========================================================

def room_detail(request, room_id):

    # =====================================================
    # GET ROOM
    # =====================================================

    room = get_object_or_404(

        Room.objects
        .select_related(
            'category'
        )
        .prefetch_related(
            'reviews__user'
        ),

        id=room_id,

        status='available',

        category__is_active=True
    )


    # =====================================================
    # APPROVED REVIEWS
    # =====================================================

    reviews = (

        room.reviews

        .filter(
            is_approved=True
        )

        .select_related(
            'user'
        )

        .order_by(
            '-created_at'
        )
    )


    # =====================================================
    # RELATED ROOMS
    # =====================================================
    #
    # Show rooms from the same category.
    # Current room is excluded.
    # =====================================================

    related_rooms = (

        Room.objects

        .filter(

            category=room.category,

            status='available',

            category__is_active=True

        )

        .exclude(

            id=room.id

        )

        .select_related(

            'category'

        )

        .order_by(

            '-is_featured',

            'room_number'

        )[:3]
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'room': room,

        'reviews': reviews,

        'related_rooms': related_rooms,

    }


    # =====================================================
    # RENDER ROOM DETAIL
    # =====================================================

    return render(

        request,

        'rooms/room_detail.html',

        context
    )