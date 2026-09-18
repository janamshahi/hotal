from django.urls import path

from . import views


urlpatterns = [

    # Add review
    path(
        'room/<int:room_id>/add/',
        views.add_review,
        name='add_review'
    ),

    # My reviews
    path(
        'my-reviews/',
        views.my_reviews,
        name='my_reviews'
    ),

    # Delete review
    path(
        '<int:review_id>/delete/',
        views.delete_review,
        name='delete_customer_review'
    ),

]