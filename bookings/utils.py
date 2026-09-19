from django.utils import timezone


def update_booking_status(booking):
    """
    Automatically update booking status based on
    check-in and check-out date/time.

    Booking flow:

        Pending
            ↓
        Confirmed
            ↓
        Checked In
            ↓
        Checked Out

    Rules:

    1. Cancelled bookings remain cancelled.
    2. Pending bookings are NOT automatically confirmed.
    3. Only Confirmed bookings become Checked In.
    4. Confirmed or Checked In bookings become Checked Out
       after the checkout date/time.
    """

    # =========================================================
    # CANCELLED BOOKING
    # =========================================================

    if booking.status == "cancelled":
        return booking

    # =========================================================
    # CURRENT LOCAL DATE/TIME
    # =========================================================

    now = timezone.localtime()

    # =========================================================
    # CHECK-IN DATETIME
    # =========================================================

    check_in_datetime = timezone.make_aware(
        booking.check_in_datetime,
        timezone.get_current_timezone()
    )

    # =========================================================
    # CHECK-OUT DATETIME
    # =========================================================

    check_out_datetime = timezone.make_aware(
        booking.check_out_datetime,
        timezone.get_current_timezone()
    )

    # =========================================================
    # CURRENT STATUS
    # =========================================================

    current_status = booking.status

    new_status = current_status

    # =========================================================
    # CHECKED OUT
    # =========================================================
    #
    # Once checkout time has passed:
    #
    # Confirmed   -> Checked Out
    # Checked In  -> Checked Out
    #
    # Pending is intentionally NOT changed.
    # =========================================================

    if now >= check_out_datetime:

        if current_status in [
            "confirmed",
            "checked_in",
        ]:

            new_status = "checked_out"

    # =========================================================
    # CHECKED IN
    # =========================================================
    #
    # At or after check-in time:
    #
    # Confirmed -> Checked In
    #
    # Pending remains Pending.
    # =========================================================

    elif now >= check_in_datetime:

        if current_status == "confirmed":

            new_status = "checked_in"

    # =========================================================
    # BEFORE CHECK-IN
    # =========================================================
    #
    # Do not automatically modify:
    #
    # Pending
    # Confirmed
    # Cancelled
    #
    # This prevents an invalid automatic status change.
    # =========================================================

    else:

        new_status = current_status

    # =========================================================
    # SAVE ONLY WHEN STATUS CHANGES
    # =========================================================

    if new_status != current_status:

        booking.status = new_status

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return booking