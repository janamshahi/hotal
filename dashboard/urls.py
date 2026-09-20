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

    path(
        'bookings/',
        views.manage_bookings,
        name='manage_bookings'
    ),

    path(
        'bookings/<int:booking_id>/',
        views.booking_detail,
        name='dashboard_booking_detail'
    ),

    path(
        'bookings/<int:booking_id>/update/',
        views.update_booking,
        name='update_booking'
    ),

    path(
        'bookings/<int:booking_id>/delete/',
        views.delete_booking,
        name='delete_booking'
    ),


    # =====================================================
    # PAYMENTS
    # =====================================================

    path(
        'payments/',
        views.manage_payments,
        name='manage_payments'
    ),

    path(
        'payments/<int:payment_id>/',
        views.payment_detail,
        name='payment_detail'
    ),

    path(
        'payments/<int:payment_id>/update/',
        views.update_payment,
        name='update_payment'
    ),

    path(
        'payments/<int:payment_id>/delete/',
        views.delete_payment,
        name='delete_payment'
    ),


    # =====================================================
    # REVIEWS
    # =====================================================

    path(
        'reviews/',
        views.manage_reviews,
        name='manage_reviews'
    ),

    path(
        'reviews/<int:review_id>/',
        views.review_detail,
        name='review_detail'
    ),

    path(
        'reviews/<int:review_id>/toggle/',
        views.toggle_review_approval,
        name='toggle_review_approval'
    ),

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


    # =====================================================
    # ADMIN NOTIFICATIONS
    # =====================================================

    path(
        'notifications/',
        views.admin_notifications,
        name='admin_notifications'
    ),

    path(
        'notifications/send/',
        views.send_notification,
        name='send_notification'
    ),

    # IMPORTANT:
    # This URL was missing from your file.
    # It fixes:
    # NoReverseMatch:
    # Reverse for 'admin_notification_read' not found.

    path(
        'notifications/<int:notification_id>/read/',
        views.admin_notification_read,
        name='admin_notification_read'
    ),

    path(
        'notifications/read-all/',
        views.mark_all_admin_notifications_read,
        name='mark_all_admin_notifications_read'
    ),


    # =====================================================
    # REPORTS
    # =====================================================

    path(
        'reports/',
        views.reports,
        name='reports'
    ),


    # =====================================================
    # ANALYTICS
    # =====================================================

    path(
        'analytics/',
        views.analytics,
        name='analytics'
    ),


    # =====================================================
    # ADMIN PROFILE
    # =====================================================

    path(
        'profile/',
        views.admin_profile,
        name='admin_profile'
    ),


    # =====================================================
    # DASHBOARD CALENDAR
    # =====================================================

    path(
        'calendar-data/',
        views.calendar_data,
        name='calendar_data'
    ),

]