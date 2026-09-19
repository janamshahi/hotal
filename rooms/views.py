from datetime import date

from django.db.models import Q
from django.shortcuts import (
    render,
    get_object_or_404
)
from django.utils import timezone

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
# - Exclude already-booked rooms
# - Validate dates
# - Show date validation errors
# - Display approved-room review data
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
    # DATE ERROR
    # =====================================================

    date_error = ""


    # =====================================================
    # BASE ROOM QUERY
    # =====================================================
    #
    # Only:
    # - Available rooms
    # - Active categories
    #
    # Featured rooms are displayed first.
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
    # SEARCH
    # =====================================================
    #
    # Search by:
    # - Room name
    # - Room number
    # - Description
    # - Category name
    # =====================================================

    if search:

        rooms = rooms.filter(

            Q(
                name__icontains=search
            )

            |

            Q(
                room_number__icontains=search
            )

            |

            Q(
                description__icontains=search
            )

            |

            Q(
                category__name__icontains=search
            )
        )


    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    selected_category = category_id

    if category_id:

        try:

            category_id = int(
                category_id
            )

            rooms = rooms.filter(
                category_id=category_id
            )

        except (
            ValueError,
            TypeError
        ):

            # Invalid category value
            category_id = ''
            selected_category = ''

    else:

        selected_category = ''


    # =====================================================
    # GUEST FILTER
    # =====================================================

    guests_value = None

    if guests:

        try:

            guests_value = int(
                guests
            )

            # Guest number must be positive

            if guests_value < 1:

                guests_value = None

                guests = ""

            else:

                rooms = rooms.filter(
                    capacity__gte=guests_value
                )

        except (
            ValueError,
            TypeError
        ):

            guests_value = None
            guests = ""


    # =====================================================
    # DATE AVAILABILITY
    # =====================================================
    #
    # A room is unavailable if an existing booking overlaps
    # the requested dates.
    #
    # Overlap condition:
    #
    # existing.check_in < requested.check_out
    #
    # AND
    #
    # existing.check_out > requested.check_in
    #
    # Cancelled bookings do NOT block the room.
    # =====================================================

    valid_dates = False

    check_in_date = None
    check_out_date = None


    # =====================================================
    # BOTH DATES PROVIDED
    # =====================================================

    if check_in or check_out:

        # -------------------------------------------------
        # BOTH DATES ARE REQUIRED
        # -------------------------------------------------

        if not check_in or not check_out:

            date_error = (
                "Please select both "
                "check-in and check-out dates."
            )


        else:

            # -------------------------------------------------
            # PARSE DATES
            # -------------------------------------------------

            try:

                check_in_date = date.fromisoformat(
                    check_in
                )

                check_out_date = date.fromisoformat(
                    check_out
                )

            except ValueError:

                date_error = (
                    "Please enter valid "
                    "check-in and check-out dates."
                )


            # -------------------------------------------------
            # CHECK-IN CANNOT BE IN THE PAST
            # -------------------------------------------------

            if not date_error:

                today = timezone.localdate()

                if check_in_date < today:

                    date_error = (
                        "Check-in date cannot "
                        "be in the past."
                    )


            # -------------------------------------------------
            # CHECK-OUT MUST BE AFTER CHECK-IN
            # -------------------------------------------------

            if not date_error:

                if check_out_date <= check_in_date:

                    date_error = (
                        "Check-out date must be "
                        "after check-in date."
                    )


            # -------------------------------------------------
            # VALID DATE RANGE
            # -------------------------------------------------

            if not date_error:

                valid_dates = True


    # =====================================================
    # ROOM AVAILABILITY FILTER
    # =====================================================

    if valid_dates:

        # Import here to avoid unnecessary model-loading
        # dependency when date filtering is not being used.

        from bookings.models import Booking


        # -------------------------------------------------
        # FIND ROOMS WITH OVERLAPPING BOOKINGS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # REMOVE BOOKED ROOMS
        # -------------------------------------------------

        rooms = rooms.exclude(
            id__in=booked_room_ids
        )


    # =====================================================
    # ACTIVE CATEGORIES
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

        # -------------------------------------------------
        # ROOM DATA
        # -------------------------------------------------

        'rooms': rooms,

        'room_count': room_count,


        # -------------------------------------------------
        # CATEGORY DATA
        # -------------------------------------------------

        'categories': categories,

        'selected_category': selected_category,


        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        'search': search,


        # -------------------------------------------------
        # DATE VALUES
        # -------------------------------------------------

        'check_in': check_in,

        'check_out': check_out,


        # -------------------------------------------------
        # DATE VALIDATION
        # -------------------------------------------------

        'date_error': date_error,

        'valid_dates': valid_dates,


        # -------------------------------------------------
        # GUEST DATA
        # -------------------------------------------------

        'guests': guests,

        'guests_value': guests_value,

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

def room_detail(
    request,
    room_id
):

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
    # Show up to three rooms from the same category.
    # The current room is excluded.
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