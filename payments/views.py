from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from bookings.models import Booking

from .models import Payment

# =========================================================
# ADMIN NOTIFICATION
# =========================================================

from dashboard.utils import create_admin_notification


# =========================================================
# CUSTOMER PAYMENT
# =========================================================

@login_required(login_url="login")
def customer_payment(request, booking_id):

    # -----------------------------------------------------
    # Only the logged-in customer can access their booking
    # -----------------------------------------------------

    booking = get_object_or_404(

        Booking.objects.select_related(
            "room",
            "room__category"
        ),

        id=booking_id,

        user=request.user
    )

    # -----------------------------------------------------
    # Cancelled booking cannot be paid
    # -----------------------------------------------------

    if booking.status == "cancelled":

        messages.error(
            request,
            "Cancelled bookings cannot be paid."
        )

        return redirect(
            "booking_detail",
            booking_id=booking.id
        )

    # -----------------------------------------------------
    # Get existing payment
    # -----------------------------------------------------

    payment = (
        Payment.objects
        .filter(
            booking=booking
        )
        .first()
    )

    # -----------------------------------------------------
    # Already completed
    # -----------------------------------------------------

    if payment and payment.status == "completed":

        return redirect(
            "payment_success",
            payment_id=payment.id
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        method = request.POST.get(
            "method",
            ""
        ).strip()

        # -------------------------------------------------
        # Validate payment method
        # -------------------------------------------------

        valid_methods = dict(
            Payment.METHOD_CHOICES
        )

        if method not in valid_methods:

            messages.error(
                request,
                "Please select a valid payment method."
            )

            return render(
                request,
                "payments/payment.html",
                {
                    "booking": booking,
                    "payment": payment,
                    "method_choices":
                        Payment.METHOD_CHOICES,
                }
            )

        # -------------------------------------------------
        # Create payment if it doesn't exist
        # -------------------------------------------------

        if payment is None:

            payment = Payment.objects.create(

                booking=booking,

                amount=booking.total_amount,

                method=method,

                status="pending",
            )

        else:

            payment.amount = booking.total_amount

            payment.method = method

            payment.status = "pending"

            payment.transaction_id = None

            payment.paid_at = None

            payment.save()

        # =================================================
        # CASH PAYMENT
        # =================================================

        if method == "cash":

            booking.payment_status = "pending"

            booking.status = "confirmed"

            booking.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "updated_at",
                ]
            )

            # -------------------------------------------------
            # ADMIN NOTIFICATION
            # -------------------------------------------------
            #
            # Cash payment is not completed yet.
            # Admin is informed that payment will be
            # collected at the hotel.
            # -------------------------------------------------

            create_admin_notification(

                title="Cash Payment Booking",

                message=(
                    f"Booking #{booking.id} has been confirmed "
                    f"with Cash Payment. "

                    f"Customer: "
                    f"{booking.user.get_full_name() or booking.user.username}. "

                    f"Room: "
                    f"{booking.room.room_number}. "

                    f"Amount: Rs. "
                    f"{payment.amount}. "

                    f"Payment will be collected at the hotel."
                ),

                notification_type="payment",

                booking=booking
            )

            messages.success(
                request,
                "Booking confirmed. Payment will be "
                "collected at the hotel."
            )

            return redirect(
                "payment_success",
                payment_id=payment.id
            )

        # =================================================
        # CARD / ONLINE DEMO PAYMENT
        # =================================================

        payment.status = "completed"

        payment.transaction_id = (
            f"GST-"
            f"{payment.id}-"
            f"{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )

        payment.paid_at = timezone.now()

        payment.save()

        # -------------------------------------------------
        # Update booking
        # -------------------------------------------------

        booking.payment_status = "paid"

        booking.status = "confirmed"

        booking.save(
            update_fields=[
                "payment_status",
                "status",
                "updated_at",
            ]
        )

        # =================================================
        # ADMIN PAYMENT NOTIFICATION
        # =================================================

        create_admin_notification(

            title="Payment Completed",

            message=(
                f"Payment completed successfully for "
                f"Booking #{booking.id}. "

                f"Customer: "
                f"{booking.user.get_full_name() or booking.user.username}. "

                f"Room: "
                f"{booking.room.room_number}. "

                f"Amount: Rs. "
                f"{payment.amount}. "

                f"Method: "
                f"{payment.get_method_display()}. "

                f"Transaction ID: "
                f"{payment.transaction_id}."
            ),

            notification_type="payment",

            booking=booking
        )

        # -------------------------------------------------
        # Customer success message
        # -------------------------------------------------

        messages.success(
            request,
            "Payment completed successfully."
        )

        return redirect(
            "payment_success",
            payment_id=payment.id
        )

    # =====================================================
    # GET
    # =====================================================

    return render(

        request,

        "payments/payment.html",

        {
            "booking": booking,

            "payment": payment,

            "method_choices":
                Payment.METHOD_CHOICES,
        }
    )


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@login_required(login_url="login")
def payment_success(
    request,
    payment_id
):

    payment = get_object_or_404(

        Payment.objects.select_related(

            "booking",

            "booking__room",

            "booking__room__category"

        ),

        id=payment_id,

        booking__user=request.user
    )

    return render(

        request,

        "payments/payment_success.html",

        {
            "payment": payment,
        }
    )


# =========================================================
# PAYMENT HISTORY
# =========================================================

@login_required(login_url="login")
def payment_history(request):

    payments = (

        Payment.objects

        .filter(
            booking__user=request.user
        )

        .select_related(

            "booking",

            "booking__room",

            "booking__room__category"

        )

        .order_by(
            "-created_at"
        )
    )

    return render(

        request,

        "payments/payment_history.html",

        {
            "payments": payments,
        }
    )


# =========================================================
# PAYMENT DETAIL
# =========================================================

@login_required(login_url="login")
def customer_payment_detail(
    request,
    payment_id
):

    payment = get_object_or_404(

        Payment.objects.select_related(

            "booking",

            "booking__room",

            "booking__room__category"

        ),

        id=payment_id,

        booking__user=request.user
    )

    return render(

        request,

        "payments/payment_detail.html",

        {
            "payment": payment,
        }
    )