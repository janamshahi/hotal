from django.urls import path

from . import views


urlpatterns = [


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        'login/',
        views.dashboard_login,
        name='dashboard_login'
    ),

    path(
        'logout/',
        views.dashboard_logout,
        name='dashboard_logout'
    ),


    # =====================================================
    # DASHBOARD
    # =====================================================

    path(
        '',
        views.dashboard,
        name='dashboard'
    ),


    # =====================================================
    # ROOMS
    # =====================================================

    path(
        'rooms/',
        views.manage_rooms,
        name='manage_rooms'
    ),

    path(
        'rooms/add/',
        views.add_room,
        name='add_room'
    ),

    path(
        'rooms/edit/<int:room_id>/',
        views.edit_room,
        name='edit_room'
    ),

    path(
        'rooms/delete/<int:room_id>/',
        views.delete_room,
        name='delete_room'
    ),


    # =====================================================
    # ROOM CATEGORIES
    # =====================================================

    path(
        'categories/',
        views.manage_categories,
        name='manage_categories'
    ),

    path(
        'categories/add/',
        views.add_category,
        name='add_category'
    ),

    path(
        'categories/edit/<int:category_id>/',
        views.edit_category,
        name='edit_category'
    ),

    path(
        'categories/delete/<int:category_id>/',
        views.delete_category,
        name='delete_category'
    ),


    # =====================================================
    # BOOKINGS
    # =====================================================

    # ADMIN BOOKING LIST

    path(
        'bookings/',
        views.manage_bookings,
        name='manage_bookings'
    ),


    # ADMIN BOOKING DETAILS
    # IMPORTANT:
    # Different name from customer booking_detail
    # to prevent URL reversing conflicts.

    path(
        'bookings/<int:booking_id>/',
        views.booking_detail,
        name='dashboard_booking_detail'
    ),


    # UPDATE BOOKING

    path(
        'bookings/<int:booking_id>/update/',
        views.update_booking,
        name='update_booking'
    ),


    # DELETE BOOKING

    path(
        'bookings/<int:booking_id>/delete/',
        views.delete_booking,
        name='delete_booking'
    ),


    # =====================================================
    # PAYMENTS
    # =====================================================

    # PAYMENT LIST

    path(
        'payments/',
        views.manage_payments,
        name='manage_payments'
    ),


    # PAYMENT DETAILS

    path(
        'payments/<int:payment_id>/',
        views.payment_detail,
        name='payment_detail'
    ),


    # UPDATE PAYMENT

    path(
        'payments/<int:payment_id>/update/',
        views.update_payment,
        name='update_payment'
    ),


    # DELETE PAYMENT

    path(
        'payments/<int:payment_id>/delete/',
        views.delete_payment,
        name='delete_payment'
    ),


    # =====================================================
    # REVIEWS
    # =====================================================

    # REVIEW LIST

    path(
        'reviews/',
        views.manage_reviews,
        name='manage_reviews'
    ),


    # REVIEW DETAILS

    path(
        'reviews/<int:review_id>/',
        views.review_detail,
        name='review_detail'
    ),


    # APPROVE / UNAPPROVE REVIEW

    path(
        'reviews/<int:review_id>/toggle/',
        views.toggle_review_approval,
        name='toggle_review_approval'
    ),


    # DELETE REVIEW

    path(
        'reviews/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review'
    ),



# =====================================================
# CUSTOMERS
# =====================================================

path(
    'customers/',
    views.manage_customers,
    name='manage_customers'
),

path(
    'customers/<int:user_id>/',
    views.customer_detail,
    name='customer_detail'
),

path(
    'customers/<int:user_id>/delete/',
    views.delete_customer,
    name='delete_customer'
),
]