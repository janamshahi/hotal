from django.urls import path

from . import views


urlpatterns = [

    # Customer room listing
    path(
        '',
        views.room_list,
        name='room_list'
    ),

    # Customer room details
    path(
        '<int:room_id>/',
        views.room_detail,
        name='room_detail'
    ),

]