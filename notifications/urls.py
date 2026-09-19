from django.urls import path
from . import views


urlpatterns = [

    # Notification list
    path(
        "",
        views.notification_list,
        name="notification_list"
    ),

    # Mark one notification as read
    path(
        "<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),

    # Mark all notifications as read
    path(
        "read-all/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read"
    ),

    # Delete one notification
    path(
        "<int:notification_id>/delete/",
        views.delete_notification,
        name="delete_notification"
    ),
]