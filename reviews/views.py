from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from bookings.models import Booking
from rooms.models import Room
from .models import Review


# =========================================================
# CUSTOMER ADD REVIEW
# =========================================================

@login_required(login_url='login')
def add_review(request, room_id):

    room = get_object_or_404(
        Room.objects.select_related('category'),
        id=room_id
    )

    # -----------------------------------------------------
    # CHECK CUSTOMER HAS COMPLETED A BOOKING
    # -----------------------------------------------------

    has_completed_booking = Booking.objects.filter(
        user=request.user,
        room=room,
        status='checked_out'
    ).exists()

    if not has_completed_booking:

        messages.error(
            request,
            'You can review this room only after completing '
            'your stay.'
        )

        return redirect(
            'room_detail',
            room_id=room.id
        )

    # -----------------------------------------------------
    # CHECK EXISTING REVIEW
    # -----------------------------------------------------

    existing_review = Review.objects.filter(
        user=request.user,
        room=room
    ).first()

    if existing_review:

        messages.info(
            request,
            'You have already reviewed this room.'
        )

        return redirect(
            'room_detail',
            room_id=room.id
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == 'POST':

        rating = request.POST.get(
            'rating'
        )

        comment = request.POST.get(
            'comment',
            ''
        ).strip()

        try:

            rating_value = int(rating)

        except (
            TypeError,
            ValueError
        ):

            rating_value = 0

        if rating_value not in [1, 2, 3, 4, 5]:

            messages.error(
                request,
                'Please select a rating from 1 to 5.'
            )

            return render(
                request,
                'reviews/add_review.html',
                {
                    'room': room,
                    'rating_choices': Review.RATING_CHOICES,
                }
            )

        if not comment:

            messages.error(
                request,
                'Please write a review comment.'
            )

            return render(
                request,
                'reviews/add_review.html',
                {
                    'room': room,
                    'rating_choices': Review.RATING_CHOICES,
                }
            )

        Review.objects.create(

            user=request.user,

            room=room,

            rating=rating_value,

            comment=comment,

            is_approved=True,

        )

        messages.success(
            request,
            'Thank you! Your review has been submitted.'
        )

        return redirect(
            'room_detail',
            room_id=room.id
        )

    return render(
        request,
        'reviews/add_review.html',
        {
            'room': room,
            'rating_choices': Review.RATING_CHOICES,
        }
    )


# =========================================================
# CUSTOMER REVIEW HISTORY
# =========================================================

@login_required(login_url='login')
def my_reviews(request):

    reviews = (
        Review.objects
        .filter(
            user=request.user
        )
        .select_related(
            'room',
            'room__category'
        )
        .order_by('-created_at')
    )

    return render(
        request,
        'reviews/my_reviews.html',
        {
            'reviews': reviews,
        }
    )


# =========================================================
# DELETE OWN REVIEW
# =========================================================

@login_required(login_url='login')
def delete_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    if request.method != 'POST':

        return redirect(
            'my_reviews'
        )

    review.delete()

    messages.success(
        request,
        'Your review has been deleted.'
    )

    return redirect(
        'my_reviews'
    )