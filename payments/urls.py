from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # CUSTOMER PAYMENT
    # =====================================================

    path(
        "booking/<int:booking_id>/",
        views.customer_payment,
        name="customer_payment"
    ),


    # =====================================================
    # PAYMENT SUCCESS
    # =====================================================

    path(
        "success/<int:payment_id>/",
        views.payment_success,
        name="payment_success"
    ),


    # =====================================================
    # PAYMENT HISTORY
    # =====================================================

    path(
        "history/",
        views.payment_history,
        name="payment_history"
    ),


    # =====================================================
    # PAYMENT DETAIL
    # =====================================================

    path(
        "<int:payment_id>/",
        views.customer_payment_detail,
        name="customer_payment_detail"
    ),

]