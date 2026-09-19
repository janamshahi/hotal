from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Notification


# =========================================================
# NOTIFICATION LIST
# =========================================================

@login_required(login_url="login")
def notification_list(request):

    notifications = (
        Notification.objects
        .filter(user=request.user)
        .select_related("booking", "booking__room")
        .order_by("-created_at")
    )

    unread_notifications = notifications.filter(
        is_read=False
    ).count()

    context = {
        "notifications": notifications,
        "unread_notifications": unread_notifications,
    }

    return render(
        request,
        "notifications/list.html",
        context
    )


# =========================================================
# MARK ONE NOTIFICATION AS READ
# =========================================================

@login_required(login_url="login")
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return redirect("notification_list")


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# =========================================================

@login_required(login_url="login")
def mark_all_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect("notification_list")


# =========================================================
# DELETE NOTIFICATION
# =========================================================

@login_required(login_url="login")
def delete_notification(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.delete()

    return redirect("notification_list")