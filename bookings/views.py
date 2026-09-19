from datetime import date, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import Booking
from .utils import update_booking_status

from rooms.models import Room

# =========================================================
# ADMIN NOTIFICATION
# =========================================================

from dashboard.utils import create_admin_notification


# =========================================================
# DEFAULT HOTEL TIMES
# =========================================================

DEFAULT_CHECK_IN_TIME = time(14, 0)   # 2:00 PM
DEFAULT_CHECK_OUT_TIME = time(12, 0)  # 12:00 PM


# =========================================================
# ROOM AVAILABILITY FUNCTION
# =========================================================

def is_room_available(
    room,
    check_in,
    check_out,
    exclude_booking_id=None
):
    """
    Check whether a room is available for the selected dates.

    Existing booking:
        19 Sep 2026 -> 21 Sep 2026

    Occupied nights:
        19 Sep
        20 Sep

    Checkout:
        21 Sep

    Therefore:

        17 -> 19       AVAILABLE
        19 -> 21       NOT AVAILABLE
        20 -> 21       NOT AVAILABLE
        21 -> 23       AVAILABLE
        21 -> 25       AVAILABLE

    Cancelled bookings do not block the room.
    """

    bookings = (
        Booking.objects
        .filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        .exclude(
            status="cancelled"
        )
    )

    if exclude_booking_id is not None:

        bookings = bookings.exclude(
            id=exclude_booking_id
        )

    return not bookings.exists()


# =========================================================
# GET AVAILABLE ROOM
# =========================================================

def get_available_room(room_id):

    return get_object_or_404(
        Room.objects.select_related("category"),
        id=room_id,
        status="available",
        category__is_active=True,
    )


# =========================================================
# CREATE BOOKING
# =========================================================

@login_required(login_url="login")
def create_booking(request, room_id):

    room = get_available_room(room_id)

    today = date.today()

    # =====================================================
    # GET REQUEST
    # =====================================================

    if request.method == "GET":

        return render(
            request,
            "bookings/create_booking.html",
            {
                "room": room,
                "today": today,

                "check_in": "",
                "check_out": "",

                "guests": 1,

                "special_request": "",

                "check_in_time": (
                    DEFAULT_CHECK_IN_TIME.strftime("%H:%M")
                ),

                "check_out_time": (
                    DEFAULT_CHECK_OUT_TIME.strftime("%H:%M")
                ),
            }
        )

    # =====================================================
    # POST DATA
    # =====================================================

    check_in_string = request.POST.get(
        "check_in",
        ""
    ).strip()

    check_out_string = request.POST.get(
        "check_out",
        ""
    ).strip()

    guests_string = request.POST.get(
        "guests",
        "1"
    ).strip()

    special_request = request.POST.get(
        "special_request",
        ""
    ).strip()

    # =====================================================
    # TIME INPUTS
    # =====================================================

    check_in_time_string = request.POST.get(
        "check_in_time",
        DEFAULT_CHECK_IN_TIME.strftime("%H:%M")
    ).strip()

    check_out_time_string = request.POST.get(
        "check_out_time",
        DEFAULT_CHECK_OUT_TIME.strftime("%H:%M")
    ).strip()

    # =====================================================
    # CONTEXT FOR ERROR RENDERING
    # =====================================================

    context = {

        "room": room,
        "today": today,

        "check_in": check_in_string,
        "check_out": check_out_string,

        "guests": guests_string,

        "special_request": special_request,

        "check_in_time": check_in_time_string,
        "check_out_time": check_out_time_string,
    }

    # =====================================================
    # CHECK-IN REQUIRED
    # =====================================================

    if not check_in_string:

        messages.error(
            request,
            "Please select a check-in date."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # CHECK-OUT REQUIRED
    # =====================================================

    if not check_out_string:

        messages.error(
            request,
            "Please select a check-out date."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # CONVERT DATES
    # =====================================================

    try:

        check_in_date = date.fromisoformat(
            check_in_string
        )

        check_out_date = date.fromisoformat(
            check_out_string
        )

    except (ValueError, TypeError):

        messages.error(
            request,
            "Please select valid dates."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # CONVERT TIMES
    # =====================================================

    try:

        check_in_time = time.fromisoformat(
            check_in_time_string
        )

        check_out_time = time.fromisoformat(
            check_out_time_string
        )

    except (ValueError, TypeError):

        messages.error(
            request,
            "Please select valid check-in and check-out times."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # PAST CHECK-IN
    # =====================================================

    if check_in_date < today:

        messages.error(
            request,
            "Check-in date cannot be in the past."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # CHECK-OUT DATE
    # =====================================================

    if check_out_date <= check_in_date:

        messages.error(
            request,
            "Check-out date must be after check-in date."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # SAME-DAY TIME VALIDATION
    # =====================================================

    if (
        check_out_date == check_in_date
        and check_out_time <= check_in_time
    ):

        messages.error(
            request,
            "Check-out time must be after check-in time."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # GUEST VALIDATION
    # =====================================================

    try:

        guests = int(
            guests_string
        )

    except (ValueError, TypeError):

        messages.error(
            request,
            "Please enter a valid number of guests."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # MINIMUM GUESTS
    # =====================================================

    if guests < 1:

        messages.error(
            request,
            "At least one guest is required."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # ROOM CAPACITY
    # =====================================================

    if guests > room.capacity:

        messages.error(
            request,
            f"This room allows a maximum of "
            f"{room.capacity} guests."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # CALCULATE NIGHTS
    # =====================================================

    nights = (
        check_out_date -
        check_in_date
    ).days

    if nights <= 0:

        messages.error(
            request,
            "Booking must be at least one night."
        )

        return render(
            request,
            "bookings/create_booking.html",
            context
        )

    # =====================================================
    # FINAL DATABASE AVAILABILITY CHECK
    # =====================================================

    with transaction.atomic():

        locked_room = (
            Room.objects
            .select_for_update()
            .select_related("category")
            .get(
                id=room.id
            )
        )

        # =================================================
        # CHECK ROOM STATUS
        # =================================================

        if locked_room.status != "available":

            messages.error(
                request,
                "This room is currently unavailable."
            )

            return render(
                request,
                "bookings/create_booking.html",
                context
            )

        # =================================================
        # CHECK CATEGORY
        # =================================================

        if (
            not locked_room.category
            or not locked_room.category.is_active
        ):

            messages.error(
                request,
                "This room is currently unavailable."
            )

            return render(
                request,
                "bookings/create_booking.html",
                context
            )

        # =================================================
        # CHECK OVERLAPPING BOOKING
        # =================================================

        existing_booking = (
            Booking.objects
            .filter(
                room=locked_room,

                check_in__lt=check_out_date,

                check_out__gt=check_in_date,
            )
            .exclude(
                status="cancelled"
            )
            .order_by(
                "check_in"
            )
            .first()
        )

        # =================================================
        # ROOM ALREADY BOOKED
        # =================================================

        if existing_booking:

            messages.error(
                request,

                f"Room {locked_room.room_number} is already "
                f"booked from "
                f"{existing_booking.check_in.strftime('%d %b %Y')} "
                f"to "
                f"{existing_booking.check_out.strftime('%d %b %Y')}. "
                f"Please select different dates."
            )

            return render(
                request,
                "bookings/create_booking.html",
                context
            )

        # =================================================
        # CALCULATE TOTAL
        # =================================================

        total_amount = (
            locked_room.price *
            nights
        )

        # =================================================
        # CREATE BOOKING
        # =================================================

        booking = Booking.objects.create(

            user=request.user,

            room=locked_room,

            check_in=check_in_date,

            check_in_time=check_in_time,

            check_out=check_out_date,

            check_out_time=check_out_time,

            guests=guests,

            total_amount=total_amount,

            status="pending",

            payment_status="pending",

            special_request=special_request,
        )

        # =================================================
        # ADMIN NOTIFICATION
        # =================================================
        #
        # A notification is created ONLY after the booking
        # has been successfully created.
        #
        # All active staff/superuser accounts receive it.
        # =================================================

        create_admin_notification(

            title="New Booking Received",

            message=(
                f"New booking received from "
                f"{booking.user.get_full_name() or booking.user.username} "
                f"for Room "
                f"{booking.room.room_number}. "
                f"Check-in: "
                f"{booking.check_in.strftime('%d %b %Y')}, "
                f"Check-out: "
                f"{booking.check_out.strftime('%d %b %Y')}, "
                f"Guests: "
                f"{booking.guests}, "
                f"Total: Rs. "
                f"{booking.total_amount}."
            ),

            notification_type="booking",

            booking=booking
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    messages.success(
        request,
        "Room booking created successfully. "
        "Please complete your payment."
    )

    return redirect(
        "customer_payment",
        booking_id=booking.id
    )


# =========================================================
# AJAX CHECK ROOM AVAILABILITY
# =========================================================

@login_required(login_url="login")
def check_availability(request, room_id):

    room = get_object_or_404(
        Room.objects.select_related("category"),
        id=room_id,
    )

    check_in_string = request.GET.get(
        "check_in",
        ""
    ).strip()

    check_out_string = request.GET.get(
        "check_out",
        ""
    ).strip()

    # =====================================================
    # REQUIRED DATES
    # =====================================================

    if (
        not check_in_string
        or not check_out_string
    ):

        return JsonResponse({
            "success": False,
            "available": False,
            "message": "Please select both dates.",
        })

    # =====================================================
    # PARSE DATES
    # =====================================================

    try:

        check_in_date = date.fromisoformat(
            check_in_string
        )

        check_out_date = date.fromisoformat(
            check_out_string
        )

    except (ValueError, TypeError):

        return JsonResponse({
            "success": False,
            "available": False,
            "message": "Invalid date format.",
        })

    # =====================================================
    # PAST DATE
    # =====================================================

    if check_in_date < date.today():

        return JsonResponse({
            "success": False,
            "available": False,
            "message": (
                "Check-in date cannot be in the past."
            ),
        })

    # =====================================================
    # DATE ORDER
    # =====================================================

    if check_out_date <= check_in_date:

        return JsonResponse({
            "success": False,
            "available": False,
            "message": (
                "Check-out must be after check-in."
            ),
        })

    # =====================================================
    # ROOM STATUS
    # =====================================================

    if room.status != "available":

        return JsonResponse({
            "success": True,
            "available": False,
            "message": (
                "This room is currently unavailable."
            ),
        })

    # =====================================================
    # CATEGORY STATUS
    # =====================================================

    if (
        not room.category
        or not room.category.is_active
    ):

        return JsonResponse({
            "success": True,
            "available": False,
            "message": (
                "This room category is currently inactive."
            ),
        })

    # =====================================================
    # CALCULATE NIGHTS
    # =====================================================

    nights = (
        check_out_date -
        check_in_date
    ).days

    # =====================================================
    # CHECK DATABASE
    # =====================================================

    available = is_room_available(
        room,
        check_in_date,
        check_out_date,
    )

    # =====================================================
    # UNAVAILABLE
    # =====================================================

    if not available:

        conflicting_booking = (
            Booking.objects
            .filter(
                room=room,

                check_in__lt=check_out_date,

                check_out__gt=check_in_date,
            )
            .exclude(
                status="cancelled"
            )
            .order_by(
                "check_in"
            )
            .first()
        )

        if conflicting_booking:

            message = (
                "This room is already booked from "

                f"{conflicting_booking.check_in.strftime('%d %b %Y')} "

                "to "

                f"{conflicting_booking.check_out.strftime('%d %b %Y')}."
            )

        else:

            message = (
                "This room is not available for the "
                "selected dates."
            )

        return JsonResponse({

            "success": True,

            "available": False,

            "message": message,

            "nights": nights,
        })

    # =====================================================
    # CALCULATE TOTAL
    # =====================================================

    total_amount = (
        room.price *
        nights
    )

    # =====================================================
    # AVAILABLE
    # =====================================================

    return JsonResponse({

        "success": True,

        "available": True,

        "message": (
            "Room is available for these dates."
        ),

        "nights": nights,

        "total_amount": str(
            total_amount
        ),
    })


# =========================================================
# CALENDAR AVAILABILITY
# =========================================================

@login_required(login_url="login")
def calendar_availability(request, room_id):

    room = get_object_or_404(
        Room.objects.select_related("category"),
        id=room_id,
    )

    # =====================================================
    # CHECK ROOM STATUS
    # =====================================================

    if room.status != "available":

        return JsonResponse({

            "success": True,

            "available": False,

            "message": (
                "This room is currently unavailable."
            ),

            "booked_ranges": [],
        })

    # =====================================================
    # CHECK CATEGORY
    # =====================================================

    if (
        not room.category
        or not room.category.is_active
    ):

        return JsonResponse({

            "success": True,

            "available": False,

            "message": (
                "This room category is currently inactive."
            ),

            "booked_ranges": [],
        })

    # =====================================================
    # GET YEAR
    # =====================================================

    try:

        year = int(
            request.GET.get(
                "year",
                date.today().year
            )
        )

    except (ValueError, TypeError):

        return JsonResponse({

            "success": False,

            "message": "Invalid year.",
        }, status=400)

    # =====================================================
    # GET MONTH
    # =====================================================

    try:

        month = int(
            request.GET.get(
                "month",
                date.today().month
            )
        )

    except (ValueError, TypeError):

        return JsonResponse({

            "success": False,

            "message": "Invalid month.",
        }, status=400)

    # =====================================================
    # VALIDATE YEAR
    # =====================================================

    if year < 2000 or year > 2100:

        return JsonResponse({

            "success": False,

            "message": "Invalid year.",
        }, status=400)

    # =====================================================
    # VALIDATE MONTH
    # =====================================================

    if month < 1 or month > 12:

        return JsonResponse({

            "success": False,

            "message": "Invalid month.",
        }, status=400)

    # =====================================================
    # FIRST DAY OF MONTH
    # =====================================================

    first_day = date(
        year,
        month,
        1
    )

    # =====================================================
    # FIRST DAY OF NEXT MONTH
    # =====================================================

    if month == 12:

        next_month = date(
            year + 1,
            1,
            1
        )

    else:

        next_month = date(
            year,
            month + 1,
            1
        )

    # =====================================================
    # GET BOOKINGS FOR THIS MONTH
    # =====================================================

    bookings = (
        Booking.objects
        .filter(

            room=room,

            check_in__lt=next_month,

            check_out__gt=first_day,
        )
        .exclude(
            status="cancelled"
        )
        .order_by(
            "check_in"
        )
    )

    # =====================================================
    # CREATE BOOKED RANGES
    # =====================================================

    booked_ranges = []

    for booking in bookings:

        booked_ranges.append({

            "check_in": (
                booking.check_in.isoformat()
            ),

            "check_out": (
                booking.check_out.isoformat()
            ),
        })

    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse({

        "success": True,

        "room_id": room.id,

        "year": year,

        "month": month,

        "today": (
            date.today().isoformat()
        ),

        "booked_ranges": booked_ranges,
    })


# =========================================================
# MY BOOKINGS
# =========================================================

@login_required(login_url="login")
def my_bookings(request):

    bookings = (
        Booking.objects
        .filter(
            user=request.user
        )
        .select_related(
            "room",
            "room__category",
        )
        .order_by(
            "-created_at"
        )
    )

    # =====================================================
    # AUTOMATICALLY UPDATE BOOKING STATUS
    # =====================================================

    for booking in bookings:

        update_booking_status(
            booking
        )

    # =====================================================
    # CURRENT BOOKINGS
    # =====================================================

    current_statuses = [
        "pending",
        "confirmed",
        "checked_in",
    ]

    # =====================================================
    # HISTORY
    # =====================================================

    history_statuses = [
        "checked_out",
        "cancelled",
    ]

    current_bookings = []

    history_bookings = []

    # =====================================================
    # SEPARATE BOOKINGS
    # =====================================================

    for booking in bookings:

        if booking.status in current_statuses:

            current_bookings.append(
                booking
            )

        elif booking.status in history_statuses:

            history_bookings.append(
                booking
            )

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "bookings/my_bookings.html",
        {
            "current_bookings": current_bookings,

            "history_bookings": history_bookings,
        }
    )


# =========================================================
# BOOKING DETAIL
# =========================================================

@login_required(login_url="login")
def booking_detail(request, booking_id):

    booking = get_object_or_404(

        Booking.objects.select_related(

            "room",

            "room__category",

            "user",
        ),

        id=booking_id,

        user=request.user,
    )

    # =====================================================
    # AUTOMATIC STATUS UPDATE
    # =====================================================

    update_booking_status(
        booking
    )

    # =====================================================
    # TOTAL NIGHTS
    # =====================================================

    total_nights = booking.total_nights

    # =====================================================
    # RENDER
    # =====================================================

    return render(

        request,

        "bookings/booking_detail.html",

        {
            "booking": booking,

            "total_nights": total_nights,

            "status_choices": (
                Booking.STATUS_CHOICES
            ),

            "payment_status_choices": (
                Booking.PAYMENT_STATUS_CHOICES
            ),
        }
    )


# =========================================================
# CANCEL BOOKING
# =========================================================

@login_required(login_url="login")
def cancel_booking(request, booking_id):

    booking = get_object_or_404(

        Booking,

        id=booking_id,

        user=request.user,
    )

    # =====================================================
    # UPDATE AUTOMATIC STATUS FIRST
    # =====================================================

    update_booking_status(
        booking
    )

    # =====================================================
    # ONLY POST
    # =====================================================

    if request.method != "POST":

        return redirect(

            "booking_detail",

            booking_id=booking.id
        )

    # =====================================================
    # CHECK STATUS
    # =====================================================

    if booking.status in [
        "checked_in",
        "checked_out",
        "cancelled",
    ]:

        messages.error(
            request,
            "This booking cannot be cancelled."
        )

        return redirect(

            "booking_detail",

            booking_id=booking.id
        )

    # =====================================================
    # CANCEL
    # =====================================================

    booking.status = "cancelled"

    booking.save(

        update_fields=[
            "status",
            "updated_at",
        ]
    )

    # =====================================================
    # ADMIN NOTIFICATION
    # =====================================================

    create_admin_notification(

        title="Booking Cancelled",

        message=(
            f"Booking #{booking.id} has been cancelled by "
            f"{booking.user.get_full_name() or booking.user.username} "
            f"for Room {booking.room.room_number}."
        ),

        notification_type="booking",

        booking=booking
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    messages.success(

        request,

        "Booking cancelled successfully."
    )

    return redirect(
        "my_bookings"
    )