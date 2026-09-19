from django.contrib.auth.models import User
from django.db.models import Q

from notifications.models import Notification


# =========================================================
# CREATE ADMIN NOTIFICATION
# =========================================================

def create_admin_notification(
    title,
    message,
    notification_type="general",
    booking=None
):
    """
    Create a notification for every active
    hotel administrator.

    Administrators are:
        - is_staff=True
        OR
        - is_superuser=True
    """

    admin_users = (
        User.objects
        .filter(is_active=True)
        .filter(
            Q(is_staff=True) |
            Q(is_superuser=True)
        )
        .distinct()
    )

    notifications = []

    for user in admin_users:

        notifications.append(
            Notification(
                user=user,
                booking=booking,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False
            )
        )

    if notifications:

        Notification.objects.bulk_create(
            notifications
        )

    return notifications