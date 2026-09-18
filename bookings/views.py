from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from rooms.models import Room

from .models import Booking


# =========================================================
# CHECK ROOM AVAILABILITY
# =========================================================

def is_room_available(
    room,
    check_in,
    check_out,
    exclude_booking_id=None
):
    """
    Check whether a room is available for the
    selected date range.
    """

    overlapping_bookings = (
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

    if exclude_booking_id:

        overlapping_bookings = (
            overlapping_bookings
            .exclude(
                id=exclude_booking_id
            )
        )

    return not overlapping_bookings.exists()


# =========================================================
# CUSTOMER BOOKING FORM
# =========================================================

@login_required(login_url="login")
def create_booking(request, room_id):

    room = get_object_or_404(
        Room.objects.select_related("category"),
        id=room_id,
        status="available",
        category__is_active=True
    )

    # -----------------------------------------------------
    # POST REQUEST
    # -----------------------------------------------------

    if request.method == "POST":

        check_in = request.POST.get(
            "check_in",
            ""
        ).strip()

        check_out = request.POST.get(
            "check_out",
            ""
        ).strip()

        guests = request.POST.get(
            "guests",
            ""
        ).strip()

        special_request = request.POST.get(
            "special_request",
            ""
        ).strip()

        today = timezone.localdate()

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not check_in or not check_out or not guests:

            messages.error(
                request,
                "Please fill in all required booking fields."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # CONVERT DATES
        # -------------------------------------------------

        try:

            check_in_date = date.fromisoformat(
                check_in
            )

            check_out_date = date.fromisoformat(
                check_out
            )

        except ValueError:

            messages.error(
                request,
                "Please enter valid check-in and check-out dates."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # CHECK-IN DATE
        # -------------------------------------------------

        if check_in_date < today:

            messages.error(
                request,
                "Check-in date cannot be in the past."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # CHECK-OUT DATE
        # -------------------------------------------------

        if check_out_date <= check_in_date:

            messages.error(
                request,
                "Check-out date must be after check-in date."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # GUEST VALIDATION
        # -------------------------------------------------

        try:

            guests_count = int(guests)

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter a valid number of guests."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        if guests_count < 1:

            messages.error(
                request,
                "At least one guest is required."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # ROOM CAPACITY
        # -------------------------------------------------

        if guests_count > room.capacity:

            messages.error(
                request,
                f"This room can accommodate a maximum of "
                f"{room.capacity} guests."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # ROOM AVAILABILITY
        # -------------------------------------------------

        if not is_room_available(
            room,
            check_in_date,
            check_out_date
        ):

            messages.error(
                request,
                "Sorry, this room is already booked for "
                "the selected dates."
            )

            return render(
                request,
                "bookings/create_booking.html",
                {
                    "room": room,
                    "today": today,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "special_request": special_request,
                }
            )

        # -------------------------------------------------
        # CALCULATE NIGHTS
        # -------------------------------------------------

        total_nights = (
            check_out_date -
            check_in_date
        ).days

        # -------------------------------------------------
        # CALCULATE TOTAL AMOUNT
        # -------------------------------------------------

        total_amount = (
            room.price *
            total_nights
        )

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------

        booking = Booking.objects.create(

            user=request.user,

            room=room,

            check_in=check_in_date,

            check_out=check_out_date,

            guests=guests_count,

            total_amount=total_amount,

            status="pending",

            payment_status="pending",

            special_request=special_request,

        )

        messages.success(
            request,
            f"Booking #{booking.id} created successfully. "
            "Please complete your payment."
        )

        # -------------------------------------------------
        # GO TO CUSTOMER PAYMENT PAGE
        # -------------------------------------------------

        return redirect(
            "customer_payment",
            booking_id=booking.id
        )

    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "bookings/create_booking.html",
        {
            "room": room,
            "today": timezone.localdate(),
        }
    )


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
            "room__category"
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "bookings/my_bookings.html",
        {
            "bookings": bookings,
        }
    )


# =========================================================
# CUSTOMER BOOKING DETAIL
# =========================================================

@login_required(login_url="login")
def booking_detail(request, booking_id):
    """
    Customer can see only their own booking.

    IMPORTANT:
    user=request.user prevents one customer
    from viewing another customer's booking.
    """

    booking = get_object_or_404(
        Booking.objects.select_related(
            "room",
            "room__category",
            "user"
        ),
        id=booking_id,
        user=request.user
    )

    # -----------------------------------------------------
    # CALCULATE TOTAL NIGHTS
    # -----------------------------------------------------

    total_nights = (
        booking.check_out -
        booking.check_in
    ).days

    return render(
        request,
        "bookings/booking_detail.html",
        {
            "booking": booking,
            "total_nights": total_nights,
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
        user=request.user
    )

    # -----------------------------------------------------
    # ONLY POST REQUEST
    # -----------------------------------------------------

    if request.method != "POST":

        return redirect(
            "booking_detail",
            booking_id=booking.id
        )

    # -----------------------------------------------------
    # CHECK BOOKING STATUS
    # -----------------------------------------------------

    if booking.status in [
        "checked_in",
        "checked_out",
        "cancelled"
    ]:

        messages.error(
            request,
            "This booking cannot be cancelled."
        )

        return redirect(
            "booking_detail",
            booking_id=booking.id
        )

    # -----------------------------------------------------
    # CANCEL BOOKING
    # -----------------------------------------------------

    booking.status = "cancelled"

    booking.save(
        update_fields=[
            "status",
            "updated_at"
        ]
    )

    messages.success(
        request,
        f"Booking #{booking.id} has been cancelled successfully."
    )

    return redirect(
        "my_bookings"
    )


# =========================================================
# CHECK ROOM AVAILABILITY
# =========================================================

def check_availability(request, room_id):

    room = get_object_or_404(
        Room.objects.select_related("category"),
        id=room_id
    )

    check_in = request.GET.get(
        "check_in",
        ""
    ).strip()

    check_out = request.GET.get(
        "check_out",
        ""
    ).strip()

    # -----------------------------------------------------
    # NO DATES
    # -----------------------------------------------------

    if not check_in or not check_out:

        return render(
            request,
            "bookings/availability.html",
            {
                "room": room,
                "available": None,
            }
        )

    # -----------------------------------------------------
    # CONVERT DATES
    # -----------------------------------------------------

    try:

        check_in_date = date.fromisoformat(
            check_in
        )

        check_out_date = date.fromisoformat(
            check_out
        )

    except ValueError:

        return render(
            request,
            "bookings/availability.html",
            {
                "room": room,
                "available": False,
                "error": "Invalid date.",
            }
        )

    # -----------------------------------------------------
    # CHECK-IN CANNOT BE IN PAST
    # -----------------------------------------------------

    if check_in_date < timezone.localdate():

        return render(
            request,
            "bookings/availability.html",
            {
                "room": room,
                "available": False,
                "error": "Check-in date cannot be in the past.",
            }
        )

    # -----------------------------------------------------
    # CHECK-OUT VALIDATION
    # -----------------------------------------------------

    if check_out_date <= check_in_date:

        return render(
            request,
            "bookings/availability.html",
            {
                "room": room,
                "available": False,
                "error": "Check-out must be after check-in.",
            }
        )

    # -----------------------------------------------------
    # ROOM STATUS
    # -----------------------------------------------------

    if room.status != "available":

        return render(
            request,
            "bookings/availability.html",
            {
                "room": room,
                "available": False,
                "error": "This room is currently unavailable.",
            }
        )

    # -----------------------------------------------------
    # CHECK OVERLAPPING BOOKINGS
    # -----------------------------------------------------

    available = is_room_available(
        room,
        check_in_date,
        check_out_date
    )

    return render(
        request,
        "bookings/availability.html",
        {
            "room": room,
            "available": available,
            "check_in": check_in,
            "check_out": check_out,
        }
    )