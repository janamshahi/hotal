from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # CREATE BOOKING
    # =====================================================

    path(
        "room/<int:room_id>/book/",
        views.create_booking,
        name="create_booking"
    ),


    # =====================================================
    # CHECK ROOM AVAILABILITY
    # =====================================================

    path(
        "room/<int:room_id>/availability/",
        views.check_availability,
        name="check_availability"
    ),


    # =====================================================
    # CALENDAR AVAILABILITY
    # =====================================================

    path(
        "room/<int:room_id>/calendar-availability/",
        views.calendar_availability,
        name="calendar_availability"
    ),


    # =====================================================
    # CUSTOMER BOOKINGS
    # =====================================================

    path(
        "my/",
        views.my_bookings,
        name="my_bookings"
    ),


    # =====================================================
    # CUSTOMER BOOKING DETAIL
    # =====================================================

    path(
        "<int:booking_id>/",
        views.booking_detail,
        name="booking_detail"
    ),


    # =====================================================
    # CANCEL BOOKING
    # =====================================================

    path(
        "<int:booking_id>/cancel/",
        views.cancel_booking,
        name="cancel_booking"
    ),

]