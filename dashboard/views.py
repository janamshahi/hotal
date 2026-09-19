from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Avg
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse

from hotel.models import Hotel, Service
from rooms.models import Room, RoomCategory
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review
from notifications.models import Notification


# =========================================================
# DASHBOARD LOGIN
# =========================================================

def dashboard_login(request):

    if request.user.is_authenticated:

        if (
            request.user.is_staff
            or request.user.is_superuser
        ):
            return redirect("dashboard")

        logout(request)

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "dashboard/login.html"
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "dashboard/login.html"
            )

        if not (
            user.is_staff
            or user.is_superuser
        ):

            logout(request)

            messages.error(
                request,
                "Customer accounts cannot access the admin dashboard. "
                "Please use Customer Login."
            )

            return render(
                request,
                "dashboard/login.html"
            )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Welcome to the Hotel Administration Dashboard."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "dashboard/login.html"
    )


# =========================================================
# DASHBOARD LOGOUT
# =========================================================

def dashboard_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "dashboard_login"
    )


# =========================================================
# DASHBOARD HOME
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def dashboard(request):

    hotel = (
        Hotel.objects
        .filter(
            is_active=True
        )
        .first()
    )

    # -----------------------------------------------------
    # ROOMS
    # -----------------------------------------------------

    total_rooms = Room.objects.count()

    available_rooms = (
        Room.objects
        .filter(
            status="available"
        )
        .count()
    )

    maintenance_rooms = (
        Room.objects
        .filter(
            status="maintenance"
        )
        .count()
    )

    inactive_rooms = (
        Room.objects
        .filter(
            status="inactive"
        )
        .count()
    )

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    total_categories = (
        RoomCategory.objects.count()
    )

    active_categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .count()
    )

    # -----------------------------------------------------
    # SERVICES
    # -----------------------------------------------------

    total_services = (
        Service.objects.count()
    )

    active_services = (
        Service.objects
        .filter(
            is_active=True
        )
        .count()
    )

    # -----------------------------------------------------
    # FEATURED ROOMS
    # -----------------------------------------------------

    featured_rooms = (
        Room.objects
        .filter(
            is_featured=True,
            status="available"
        )
        .select_related(
            "category"
        )
        .order_by(
            "room_number"
        )[:5]
    )

    # -----------------------------------------------------
    # RECENT ROOMS
    # -----------------------------------------------------

    recent_rooms = (
        Room.objects
        .select_related(
            "category"
        )
        .order_by(
            "-created_at"
        )[:5]
    )

    # -----------------------------------------------------
    # BOOKING STATISTICS
    # -----------------------------------------------------

    total_bookings = (
        Booking.objects.count()
    )

    pending_bookings = (
        Booking.objects
        .filter(
            status="pending"
        )
        .count()
    )

    confirmed_bookings = (
        Booking.objects
        .filter(
            status="confirmed"
        )
        .count()
    )

    checked_in_bookings = (
        Booking.objects
        .filter(
            status="checked_in"
        )
        .count()
    )

    checked_out_bookings = (
        Booking.objects
        .filter(
            status="checked_out"
        )
        .count()
    )

    # -----------------------------------------------------
    # PAYMENTS
    # -----------------------------------------------------

    paid_bookings = (
        Booking.objects
        .filter(
            payment_status="paid"
        )
        .count()
    )

    total_revenue = (
        Payment.objects
        .filter(
            status="completed"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    # -----------------------------------------------------
    # RECENT BOOKINGS
    # -----------------------------------------------------

    recent_bookings = (
        Booking.objects
        .select_related(
            "user",
            "room",
            "room__category"
        )
        .order_by(
            "-created_at"
        )[:5]
    )

    context = {

        "hotel": hotel,

        "total_rooms":
            total_rooms,

        "available_rooms":
            available_rooms,

        "maintenance_rooms":
            maintenance_rooms,

        "inactive_rooms":
            inactive_rooms,

        "total_categories":
            total_categories,

        "active_categories":
            active_categories,

        "total_services":
            total_services,

        "active_services":
            active_services,

        "featured_rooms":
            featured_rooms,

        "recent_rooms":
            recent_rooms,

        "total_bookings":
            total_bookings,

        "pending_bookings":
            pending_bookings,

        "confirmed_bookings":
            confirmed_bookings,

        "checked_in_bookings":
            checked_in_bookings,

        "checked_out_bookings":
            checked_out_bookings,

        "paid_bookings":
            paid_bookings,

        "total_revenue":
            total_revenue,

        "recent_bookings":
            recent_bookings,
    }

    return render(
        request,
        "dashboard/home.html",
        context
    )


# =========================================================
# BOOKING CALENDAR API
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def calendar_data(request):

    import calendar
    from datetime import date, timedelta

    today = timezone.localdate()

    # -----------------------------------------------------
    # YEAR
    # -----------------------------------------------------

    try:

        year = int(
            request.GET.get(
                "year",
                today.year
            )
        )

    except (
        ValueError,
        TypeError
    ):

        year = today.year

    # -----------------------------------------------------
    # MONTH
    # -----------------------------------------------------

    try:

        month = int(
            request.GET.get(
                "month",
                today.month
            )
        )

    except (
        ValueError,
        TypeError
    ):

        month = today.month

    # -----------------------------------------------------
    # VALIDATE DATE
    # -----------------------------------------------------

    if year < 2000 or year > 2100:

        year = today.year

    if month < 1 or month > 12:

        month = today.month

    # -----------------------------------------------------
    # MONTH RANGE
    # -----------------------------------------------------

    first_day = date(
        year,
        month,
        1
    )

    last_day = date(
        year,
        month,
        calendar.monthrange(
            year,
            month
        )[1]
    )

    next_day = (
        last_day
        + timedelta(days=1)
    )

    # -----------------------------------------------------
    # BOOKINGS
    # -----------------------------------------------------

    bookings = (
        Booking.objects
        .filter(
            check_in__lt=next_day,
            check_out__gt=first_day
        )
        .exclude(
            status="cancelled"
        )
        .select_related(
            "user",
            "room"
        )
        .order_by(
            "check_in"
        )
    )

    booking_list = []

    # -----------------------------------------------------
    # CONVERT BOOKINGS TO JSON
    # -----------------------------------------------------

    for booking in bookings:

        # Customer
        if booking.user:

            customer_name = (
                booking.user
                .get_full_name()
                .strip()
                or booking.user.username
            )

        else:

            customer_name = "Guest"

        # Room
        if booking.room:

            room_number = str(
                booking.room.room_number
            )

        else:

            room_number = "N/A"

        # Status
        try:

            status_display = (
                booking.get_status_display()
            )

        except Exception:

            status_display = str(
                booking.status
            )

        # Payment status
        try:

            payment_status_display = (
                booking
                .get_payment_status_display()
            )

        except Exception:

            payment_status_display = ""

        # Detail URL
        detail_url = reverse(
            "dashboard_booking_detail",
            args=[
                booking.id
            ]
        )

        booking_list.append({

            "id":
                booking.id,

            "start":
                booking.check_in.isoformat(),

            "end":
                booking.check_out.isoformat(),

            "customer":
                customer_name,

            "username":
                booking.user.username
                if booking.user
                else "",

            "room":
                room_number,

            "status":
                status_display,

            "status_value":
                booking.status,

            "payment_status":
                payment_status_display,

            "payment_status_value":
                booking.payment_status,

            "guests":
                getattr(
                    booking,
                    "guests",
                    0
                ),

            "amount":
                str(
                    getattr(
                        booking,
                        "total_amount",
                        0
                    )
                ),

            "check_in_time":
                (
                    booking.check_in_time
                    .strftime("%I:%M %p")
                    if getattr(
                        booking,
                        "check_in_time",
                        None
                    )
                    else ""
                ),

            "check_out_time":
                (
                    booking.check_out_time
                    .strftime("%I:%M %p")
                    if getattr(
                        booking,
                        "check_out_time",
                        None
                    )
                    else ""
                ),

            "detail_url":
                detail_url,
        })

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return JsonResponse({

        "year":
            year,

        "month":
            month,

        "today":
            today.isoformat(),

        "bookings":
            booking_list,
    })


# =========================================================
# MANAGE ROOMS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_rooms(request):

    rooms = (
        Room.objects
        .select_related(
            "category"
        )
        .order_by(
            "room_number"
        )
    )

    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )

    context = {

        "rooms":
            rooms,

        "categories":
            categories,
    }

    return render(
        request,
        "dashboard/rooms.html",
        context
    )


# =========================================================
# ADD ROOM
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def add_room(request):

    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        room_number = request.POST.get(
            "room_number",
            ""
        ).strip()

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get(
            "price"
        )

        capacity = request.POST.get(
            "capacity"
        )

        size = request.POST.get(
            "size"
        )

        bed_type = request.POST.get(
            "bed_type",
            "Double Bed"
        ).strip()

        floor = request.POST.get(
            "floor"
        )

        status = request.POST.get(
            "status",
            "available"
        )

        is_featured = (
            request.POST.get(
                "is_featured"
            ) == "on"
        )

        has_wifi = (
            request.POST.get(
                "has_wifi"
            ) == "on"
        )

        has_ac = (
            request.POST.get(
                "has_ac"
            ) == "on"
        )

        has_tv = (
            request.POST.get(
                "has_tv"
            ) == "on"
        )

        has_breakfast = (
            request.POST.get(
                "has_breakfast"
            ) == "on"
        )

        has_balcony = (
            request.POST.get(
                "has_balcony"
            ) == "on"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not category_id:

            messages.error(
                request,
                "Please select a room category."
            )

            return render(
                request,
                "dashboard/room_form.html",
                {
                    "categories":
                        categories,

                    "form_data":
                        request.POST
                }
            )

        if not room_number or not name:

            messages.error(
                request,
                "Room number and room name are required."
            )

            return render(
                request,
                "dashboard/room_form.html",
                {
                    "categories":
                        categories,

                    "form_data":
                        request.POST
                }
            )

        if Room.objects.filter(
            room_number=room_number
        ).exists():

            messages.error(
                request,
                "This room number already exists."
            )

            return render(
                request,
                "dashboard/room_form.html",
                {
                    "categories":
                        categories,

                    "form_data":
                        request.POST
                }
            )

        try:

            category = (
                RoomCategory.objects
                .get(
                    id=category_id,
                    is_active=True
                )
            )

            room = Room(

                category=category,

                room_number=room_number,

                name=name,

                description=description,

                price=price,

                capacity=capacity,

                size=size,

                bed_type=bed_type,

                floor=floor,

                status=status,

                is_featured=is_featured,

                has_wifi=has_wifi,

                has_ac=has_ac,

                has_tv=has_tv,

                has_breakfast=has_breakfast,

                has_balcony=has_balcony,

            )

            if request.FILES.get(
                "image"
            ):

                room.image = (
                    request.FILES.get(
                        "image"
                    )
                )

            room.save()

            messages.success(
                request,
                f"Room {room.room_number} added successfully."
            )

            return redirect(
                "manage_rooms"
            )

        except Exception as e:

            messages.error(
                request,
                f"Unable to add room: {e}"
            )

    return render(
        request,
        "dashboard/room_form.html",
        {
            "categories":
                categories
        }
    )


# =========================================================
# EDIT ROOM
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def edit_room(
    request,
    room_id
):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        room_number = request.POST.get(
            "room_number",
            ""
        ).strip()

        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not category_id:

            messages.error(
                request,
                "Please select a room category."
            )

            return redirect(
                "edit_room",
                room_id=room.id
            )

        if not room_number or not name:

            messages.error(
                request,
                "Room number and room name are required."
            )

            return redirect(
                "edit_room",
                room_id=room.id
            )

        if (
            Room.objects
            .filter(
                room_number=room_number
            )
            .exclude(
                id=room.id
            )
            .exists()
        ):

            messages.error(
                request,
                "Another room already uses this room number."
            )

            return redirect(
                "edit_room",
                room_id=room.id
            )

        room.category_id = category_id

        room.room_number = room_number

        room.name = name

        room.description = request.POST.get(
            "description",
            ""
        ).strip()

        room.price = request.POST.get(
            "price"
        )

        room.capacity = request.POST.get(
            "capacity"
        )

        room.size = request.POST.get(
            "size"
        )

        room.bed_type = request.POST.get(
            "bed_type",
            "Double Bed"
        ).strip()

        room.floor = request.POST.get(
            "floor"
        )

        room.status = request.POST.get(
            "status",
            "available"
        )

        room.is_featured = (
            request.POST.get(
                "is_featured"
            ) == "on"
        )

        room.has_wifi = (
            request.POST.get(
                "has_wifi"
            ) == "on"
        )

        room.has_ac = (
            request.POST.get(
                "has_ac"
            ) == "on"
        )

        room.has_tv = (
            request.POST.get(
                "has_tv"
            ) == "on"
        )

        room.has_breakfast = (
            request.POST.get(
                "has_breakfast"
            ) == "on"
        )

        room.has_balcony = (
            request.POST.get(
                "has_balcony"
            ) == "on"
        )

        if request.FILES.get(
            "image"
        ):

            room.image = (
                request.FILES.get(
                    "image"
                )
            )

        room.save()

        messages.success(
            request,
            f"Room {room.room_number} updated successfully."
        )

        return redirect(
            "manage_rooms"
        )

    return render(
        request,
        "dashboard/room_form.html",
        {
            "room":
                room,

            "categories":
                categories,

            "edit_mode":
                True
        }
    )


# =========================================================
# DELETE ROOM
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_room(
    request,
    room_id
):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    if request.method == "POST":

        room_number = room.room_number

        room.delete()

        messages.success(
            request,
            f"Room {room_number} deleted successfully."
        )

    return redirect(
        "manage_rooms"
    )


# =========================================================
# ROOM CATEGORY MANAGEMENT
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_categories(request):

    categories = (
        RoomCategory.objects
        .prefetch_related(
            "rooms"
        )
        .order_by(
            "name"
        )
    )

    return render(
        request,
        "dashboard/categories.html",
        {
            "categories":
                categories
        }
    )


# =========================================================
# ADD CATEGORY
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def add_category(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        max_guests = request.POST.get(
            "max_guests",
            ""
        ).strip()

        is_active = (
            request.POST.get(
                "is_active"
            ) == "on"
        )

        if not name:

            messages.error(
                request,
                "Category name is required."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "form_data":
                        request.POST,

                    "page_title":
                        "Add Room Category",
                }
            )

        if (
            RoomCategory.objects
            .filter(
                name__iexact=name
            )
            .exists()
        ):

            messages.error(
                request,
                "A room category with this name already exists."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "form_data":
                        request.POST,

                    "page_title":
                        "Add Room Category",
                }
            )

        try:

            max_guests = int(
                max_guests
            )

            if max_guests < 1:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Maximum guests must be a valid number greater than 0."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "form_data":
                        request.POST,

                    "page_title":
                        "Add Room Category",
                }
            )

        RoomCategory.objects.create(

            name=name,

            description=description,

            max_guests=max_guests,

            is_active=is_active

        )

        messages.success(
            request,
            f'Room category "{name}" added successfully.'
        )

        return redirect(
            "manage_categories"
        )

    return render(
        request,
        "dashboard/category_form.html",
        {
            "page_title":
                "Add Room Category",
        }
    )


# =========================================================
# EDIT CATEGORY
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def edit_category(
    request,
    category_id
):

    category = get_object_or_404(
        RoomCategory,
        id=category_id
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        max_guests = request.POST.get(
            "max_guests",
            ""
        ).strip()

        is_active = (
            request.POST.get(
                "is_active"
            ) == "on"
        )

        if not name:

            messages.error(
                request,
                "Category name is required."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "category":
                        category,

                    "form_data":
                        request.POST,

                    "page_title":
                        "Edit Room Category",
                }
            )

        duplicate = (
            RoomCategory.objects
            .filter(
                name__iexact=name
            )
            .exclude(
                id=category.id
            )
            .exists()
        )

        if duplicate:

            messages.error(
                request,
                "Another room category with this name already exists."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "category":
                        category,

                    "form_data":
                        request.POST,

                    "page_title":
                        "Edit Room Category",
                }
            )

        try:

            max_guests = int(
                max_guests
            )

            if max_guests < 1:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Maximum guests must be a valid number greater than 0."
            )

            return render(
                request,
                "dashboard/category_form.html",
                {
                    "category":
                        category,

                    "form_data":
                        request.POST,

                    "page_title":
                        "Edit Room Category",
                }
            )

        category.name = name

        category.description = description

        category.max_guests = max_guests

        category.is_active = is_active

        category.save()

        messages.success(
            request,
            f'Room category "{name}" updated successfully.'
        )

        return redirect(
            "manage_categories"
        )

    return render(
        request,
        "dashboard/category_form.html",
        {
            "category":
                category,

            "page_title":
                "Edit Room Category",
        }
    )


# =========================================================
# DELETE CATEGORY
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_category(
    request,
    category_id
):

    if request.method != "POST":

        return redirect(
            "manage_categories"
        )

    category = get_object_or_404(
        RoomCategory,
        id=category_id
    )

    room_count = category.rooms.count()

    if room_count > 0:

        messages.error(
            request,
            (
                f'Cannot delete "{category.name}" because '
                f"{room_count} room(s) are using this category. "
                f"Please move or remove those rooms first."
            )
        )

        return redirect(
            "manage_categories"
        )

    category_name = category.name

    category.delete()

    messages.success(
        request,
        f'Room category "{category_name}" deleted successfully.'
    )

    return redirect(
        "manage_categories"
    )


# =========================================================
# AUTOMATIC CHECKOUT
# =========================================================

def process_expired_bookings():

    today = timezone.localdate()

    expired_bookings = (
        Booking.objects
        .select_related(
            "user",
            "room"
        )
        .filter(
            check_out__lt=today,
            status__in=[
                "confirmed",
                "checked_in"
            ]
        )
        .order_by(
            "check_out"
        )
    )

    processed_count = 0

    for booking in expired_bookings:

        with transaction.atomic():

            booking = (
                Booking.objects
                .select_for_update()
                .select_related(
                    "user",
                    "room"
                )
                .get(
                    id=booking.id
                )
            )

            if booking.status not in [
                "confirmed",
                "checked_in"
            ]:

                continue

            if booking.check_out >= today:

                continue

            booking.status = "checked_out"

            booking.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )

            room_number = (
                booking.room.room_number
                if booking.room
                else "N/A"
            )

            notification_message = (
                f"Your booking #{booking.id} at GrandStay Hotel "
                f"for Room {room_number} has been automatically "
                f"marked as Checked Out because your checkout "
                f"date ({booking.check_out.strftime('%d %B %Y')}) "
                f"has passed. Thank you for staying with us."
            )

            Notification.objects.get_or_create(

                user=booking.user,

                booking=booking,

                notification_type="checkout",

                defaults={

                    "title":
                        "Booking Checked Out",

                    "message":
                        notification_message,

                    "is_read":
                        False,
                }
            )

            processed_count += 1

    return processed_count


# =========================================================
# MANAGE BOOKINGS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_bookings(request):

    process_expired_bookings()

    bookings = (
        Booking.objects
        .select_related(
            "user",
            "room",
            "room__category"
        )
        .order_by(
            "-created_at"
        )
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        bookings = bookings.filter(

            Q(
                user__username__icontains=search
            )

            |

            Q(
                user__first_name__icontains=search
            )

            |

            Q(
                user__last_name__icontains=search
            )

            |

            Q(
                room__room_number__icontains=search
            )

            |

            Q(
                room__name__icontains=search
            )
        )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        status_values = dict(
            Booking.STATUS_CHOICES
        )

        if status in status_values:

            bookings = bookings.filter(
                status=status
            )

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    payment_status = request.GET.get(
        "payment_status",
        ""
    ).strip()

    if payment_status:

        payment_status_values = dict(
            Booking.PAYMENT_STATUS_CHOICES
        )

        if payment_status in payment_status_values:

            bookings = bookings.filter(
                payment_status=payment_status
            )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    total_bookings = Booking.objects.count()

    pending_bookings = (
        Booking.objects
        .filter(
            status="pending"
        )
        .count()
    )

    confirmed_bookings = (
        Booking.objects
        .filter(
            status="confirmed"
        )
        .count()
    )

    checked_in_bookings = (
        Booking.objects
        .filter(
            status="checked_in"
        )
        .count()
    )

    checked_out_bookings = (
        Booking.objects
        .filter(
            status="checked_out"
        )
        .count()
    )

    paid_bookings = (
        Booking.objects
        .filter(
            payment_status="paid"
        )
        .count()
    )

    context = {

        "bookings":
            bookings,

        "total_bookings":
            total_bookings,

        "pending_bookings":
            pending_bookings,

        "confirmed_bookings":
            confirmed_bookings,

        "checked_in_bookings":
            checked_in_bookings,

        "checked_out_bookings":
            checked_out_bookings,

        "paid_bookings":
            paid_bookings,

        "search":
            search,

        "selected_status":
            status,

        "selected_payment_status":
            payment_status,

        "status_choices":
            Booking.STATUS_CHOICES,

        "payment_status_choices":
            Booking.PAYMENT_STATUS_CHOICES,

    }

    return render(
        request,
        "dashboard/bookings.html",
        context
    )


# =========================================================
# ADMIN BOOKING DETAIL
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def booking_detail(
    request,
    booking_id
):

    process_expired_bookings()

    booking = get_object_or_404(

        Booking.objects.select_related(
            "user",
            "room",
            "room__category"
        ),

        id=booking_id
    )

    total_nights = (
        booking.check_out
        - booking.check_in
    ).days

    context = {

        "booking":
            booking,

        "total_nights":
            total_nights,

        "status_choices":
            Booking.STATUS_CHOICES,

        "payment_status_choices":
            Booking.PAYMENT_STATUS_CHOICES,

    }

    return render(
        request,
        "dashboard/booking_detail.html",
        context
    )


# =========================================================
# UPDATE BOOKING
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def update_booking(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method != "POST":

        return redirect(
            "dashboard_booking_detail",
            booking_id=booking.id
        )

    new_status = request.POST.get(
        "status",
        ""
    ).strip()

    valid_statuses = dict(
        Booking.STATUS_CHOICES
    )

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid booking status."
        )

        return redirect(
            "dashboard_booking_detail",
            booking_id=booking.id
        )

    new_payment_status = request.POST.get(
        "payment_status",
        ""
    ).strip()

    valid_payment_statuses = dict(
        Booking.PAYMENT_STATUS_CHOICES
    )

    if new_payment_status not in valid_payment_statuses:

        messages.error(
            request,
            "Invalid payment status."
        )

        return redirect(
            "dashboard_booking_detail",
            booking_id=booking.id
        )

    booking.status = new_status

    booking.payment_status = new_payment_status

    booking.save(
        update_fields=[
            "status",
            "payment_status",
            "updated_at"
        ]
    )

    # -----------------------------------------------------
    # PAYMENT SYNCHRONIZATION
    # -----------------------------------------------------

    try:

        payment = booking.payment

    except Payment.DoesNotExist:

        payment = None

    if payment:

        payment_status_mapping = {

            "pending":
                "pending",

            "paid":
                "completed",

            "failed":
                "failed",

            "refunded":
                "refunded",
        }

        payment.status = (
            payment_status_mapping.get(
                new_payment_status,
                "pending"
            )
        )

        payment.save(
            update_fields=[
                "status"
            ]
        )

    # -----------------------------------------------------
    # CUSTOMER NOTIFICATION
    # -----------------------------------------------------

    status_messages = {

        "pending":
            "Your booking is currently pending.",

        "confirmed":
            "Your booking has been confirmed.",

        "checked_in":
            "You have successfully checked in.",

        "checked_out":
            "Your booking has been checked out.",

        "cancelled":
            "Your booking has been cancelled.",
    }

    notification_message = status_messages.get(
        new_status,
        "Your booking status has been updated."
    )

    Notification.objects.create(

        user=booking.user,

        booking=booking,

        title=(
            f"Booking Status: "
            f"{booking.get_status_display()}"
        ),

        message=notification_message,

        notification_type="booking",

        is_read=False
    )

    messages.success(
        request,
        f"Booking #{booking.id} updated successfully."
    )

    return redirect(
        "dashboard_booking_detail",
        booking_id=booking.id
    )


# =========================================================
# DELETE BOOKING
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_booking(
    request,
    booking_id
):

    if request.method != "POST":

        return redirect(
            "manage_bookings"
        )

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    booking_id_value = booking.id

    booking.delete()

    messages.success(
        request,
        f"Booking #{booking_id_value} deleted successfully."
    )

    return redirect(
        "manage_bookings"
    )


# =========================================================
# PAYMENT MANAGEMENT
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_payments(request):

    payments = (
        Payment.objects
        .select_related(
            "booking",
            "booking__user",
            "booking__room",
            "booking__room__category"
        )
        .order_by(
            "-created_at"
        )
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        payments = payments.filter(

            Q(
                booking__user__username__icontains=search
            )

            |

            Q(
                booking__user__first_name__icontains=search
            )

            |

            Q(
                booking__user__last_name__icontains=search
            )

            |

            Q(
                transaction_id__icontains=search
            )

            |

            Q(
                booking__room__room_number__icontains=search
            )

            |

            Q(
                booking__room__name__icontains=search
            )
        )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        valid_statuses = dict(
            Payment.STATUS_CHOICES
        )

        if status in valid_statuses:

            payments = payments.filter(
                status=status
            )

    # -----------------------------------------------------
    # METHOD
    # -----------------------------------------------------

    method = request.GET.get(
        "method",
        ""
    ).strip()

    if method:

        valid_methods = dict(
            Payment.METHOD_CHOICES
        )

        if method in valid_methods:

            payments = payments.filter(
                method=method
            )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    total_payments = Payment.objects.count()

    pending_payments = (
        Payment.objects
        .filter(
            status="pending"
        )
        .count()
    )

    completed_payments = (
        Payment.objects
        .filter(
            status="completed"
        )
        .count()
    )

    failed_payments = (
        Payment.objects
        .filter(
            status="failed"
        )
        .count()
    )

    refunded_payments = (
        Payment.objects
        .filter(
            status="refunded"
        )
        .count()
    )

    total_revenue = (
        Payment.objects
        .filter(
            status="completed"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    context = {

        "payments":
            payments,

        "total_payments":
            total_payments,

        "pending_payments":
            pending_payments,

        "completed_payments":
            completed_payments,

        "failed_payments":
            failed_payments,

        "refunded_payments":
            refunded_payments,

        "total_revenue":
            total_revenue,

        "search":
            search,

        "selected_status":
            status,

        "selected_method":
            method,

        "status_choices":
            Payment.STATUS_CHOICES,

        "method_choices":
            Payment.METHOD_CHOICES,

    }

    return render(
        request,
        "dashboard/payments.html",
        context
    )


# =========================================================
# PAYMENT DETAIL
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def payment_detail(
    request,
    payment_id
):

    payment = get_object_or_404(

        Payment.objects.select_related(
            "booking",
            "booking__user",
            "booking__room",
            "booking__room__category"
        ),

        id=payment_id
    )

    context = {

        "payment":
            payment,

        "status_choices":
            Payment.STATUS_CHOICES,

        "method_choices":
            Payment.METHOD_CHOICES,

    }

    return render(
        request,
        "dashboard/payment_detail.html",
        context
    )


# =========================================================
# UPDATE PAYMENT
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def update_payment(
    request,
    payment_id
):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "booking"
        ),
        id=payment_id
    )

    if request.method != "POST":

        return redirect(
            "payment_detail",
            payment_id=payment.id
        )

    new_status = request.POST.get(
        "status",
        ""
    ).strip()

    new_method = request.POST.get(
        "method",
        ""
    ).strip()

    valid_statuses = dict(
        Payment.STATUS_CHOICES
    )

    valid_methods = dict(
        Payment.METHOD_CHOICES
    )

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid payment status."
        )

        return redirect(
            "payment_detail",
            payment_id=payment.id
        )

    if new_method not in valid_methods:

        messages.error(
            request,
            "Invalid payment method."
        )

        return redirect(
            "payment_detail",
            payment_id=payment.id
        )

    payment.status = new_status

    payment.method = new_method

    payment.save(
        update_fields=[
            "status",
            "method"
        ]
    )

    booking = payment.booking

    booking_payment_mapping = {

        "pending":
            "pending",

        "completed":
            "paid",

        "failed":
            "failed",

        "refunded":
            "refunded",
    }

    booking.payment_status = (
        booking_payment_mapping.get(
            new_status,
            "pending"
        )
    )

    booking.save(
        update_fields=[
            "payment_status",
            "updated_at"
        ]
    )

    messages.success(
        request,
        f"Payment #{payment.id} updated successfully."
    )

    return redirect(
        "payment_detail",
        payment_id=payment.id
    )


# =========================================================
# DELETE PAYMENT
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_payment(
    request,
    payment_id
):

    if request.method != "POST":

        return redirect(
            "manage_payments"
        )

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    payment_id_value = payment.id

    payment.delete()

    messages.success(
        request,
        f"Payment #{payment_id_value} deleted successfully."
    )

    return redirect(
        "manage_payments"
    )


# =========================================================
# REVIEW MANAGEMENT
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_reviews(request):

    reviews = (
        Review.objects
        .select_related(
            "user",
            "room",
            "room__category"
        )
        .order_by(
            "-created_at"
        )
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        reviews = reviews.filter(

            Q(
                user__username__icontains=search
            )

            |

            Q(
                user__first_name__icontains=search
            )

            |

            Q(
                user__last_name__icontains=search
            )

            |

            Q(
                room__room_number__icontains=search
            )

            |

            Q(
                room__name__icontains=search
            )

            |

            Q(
                comment__icontains=search
            )
        )

    approval = request.GET.get(
        "approval",
        ""
    ).strip()

    if approval == "approved":

        reviews = reviews.filter(
            is_approved=True
        )

    elif approval == "pending":

        reviews = reviews.filter(
            is_approved=False
        )

    rating = request.GET.get(
        "rating",
        ""
    ).strip()

    if rating:

        try:

            rating_value = int(
                rating
            )

            if 1 <= rating_value <= 5:

                reviews = reviews.filter(
                    rating=rating_value
                )

        except ValueError:

            pass

    total_reviews = Review.objects.count()

    approved_reviews = (
        Review.objects
        .filter(
            is_approved=True
        )
        .count()
    )

    pending_reviews = (
        Review.objects
        .filter(
            is_approved=False
        )
        .count()
    )

    five_star_reviews = (
        Review.objects
        .filter(
            rating=5
        )
        .count()
    )

    average_rating = (
        Review.objects
        .aggregate(
            average=Avg("rating")
        )["average"]
        or 0
    )

    context = {

        "reviews":
            reviews,

        "total_reviews":
            total_reviews,

        "approved_reviews":
            approved_reviews,

        "pending_reviews":
            pending_reviews,

        "five_star_reviews":
            five_star_reviews,

        "average_rating":
            round(
                float(
                    average_rating
                ),
                1
            ),

        "search":
            search,

        "selected_approval":
            approval,

        "selected_rating":
            rating,

        "rating_choices":
            Review.RATING_CHOICES,
    }

    return render(
        request,
        "dashboard/reviews.html",
        context
    )


# =========================================================
# REVIEW DETAIL
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def review_detail(
    request,
    review_id
):

    review = get_object_or_404(

        Review.objects.select_related(
            "user",
            "room",
            "room__category"
        ),

        id=review_id
    )

    return render(
        request,
        "dashboard/review_detail.html",
        {
            "review":
                review,
        }
    )


# =========================================================
# APPROVE / UNAPPROVE REVIEW
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def toggle_review_approval(
    request,
    review_id
):

    if request.method != "POST":

        return redirect(
            "manage_reviews"
        )

    review = get_object_or_404(
        Review,
        id=review_id
    )

    review.is_approved = (
        not review.is_approved
    )

    review.save(
        update_fields=[
            "is_approved"
        ]
    )

    if review.is_approved:

        messages.success(
            request,
            f"Review #{review.id} approved successfully."
        )

    else:

        messages.success(
            request,
            f"Review #{review.id} unapproved successfully."
        )

    return redirect(
        "manage_reviews"
    )


# =========================================================
# DELETE REVIEW
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_review(
    request,
    review_id
):

    if request.method != "POST":

        return redirect(
            "manage_reviews"
        )

    review = get_object_or_404(
        Review,
        id=review_id
    )

    review_id_value = review.id

    review.delete()

    messages.success(
        request,
        f"Review #{review_id_value} deleted successfully."
    )

    return redirect(
        "manage_reviews"
    )


# =========================================================
# CUSTOMERS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def manage_customers(request):

    customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .select_related(
            "customer_profile"
        )
        .prefetch_related(
            "bookings"
        )
        .order_by(
            "-date_joined"
        )
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        customers = customers.filter(

            Q(
                username__icontains=search
            )

            |

            Q(
                first_name__icontains=search
            )

            |

            Q(
                last_name__icontains=search
            )

            |

            Q(
                email__icontains=search
            )

            |

            Q(
                customer_profile__phone__icontains=search
            )
        )

    return render(
        request,
        "dashboard/customers.html",
        {
            "customers":
                customers,

            "search":
                search,
        }
    )


# =========================================================
# CUSTOMER DETAIL
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def customer_detail(
    request,
    user_id
):

    customer = get_object_or_404(

        User.objects
        .select_related(
            "customer_profile"
        )
        .prefetch_related(
            "bookings__room",
            "bookings__room__category"
        ),

        id=user_id
    )

    bookings = (
        customer.bookings
        .all()
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "dashboard/customer_detail.html",
        {
            "customer":
                customer,

            "bookings":
                bookings,
        }
    )


# =========================================================
# DELETE CUSTOMER
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def delete_customer(
    request,
    user_id
):

    if request.method == "POST":

        customer = get_object_or_404(

            User,

            id=user_id,

            is_staff=False,

            is_superuser=False
        )

        username = customer.username

        customer.delete()

        messages.success(
            request,
            f'Customer "{username}" has been deleted successfully.'
        )

    return redirect(
        "manage_customers"
    )


# =========================================================
# ADMIN NOTIFICATIONS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def admin_notifications(request):

    notifications = (
        Notification.objects
        .filter(
            user=request.user
        )
        .order_by(
            "-created_at"
        )
    )

    unread_count = (
        notifications
        .filter(
            is_read=False
        )
        .count()
    )

    return render(
        request,
        "dashboard/notifications.html",
        {
            "notifications":
                notifications,

            "unread_count":
                unread_count,
        }
    )


# =========================================================
# MARK ADMIN NOTIFICATION AS READ
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def admin_notification_read(
    request,
    notification_id
):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.is_read = True

    notification.save(
        update_fields=[
            "is_read"
        ]
    )

    if notification.booking_id:

        return redirect(
            "dashboard_booking_detail",
            booking_id=notification.booking_id
        )

    return redirect(
        "admin_notifications"
    )


# =========================================================
# MARK ALL ADMIN NOTIFICATIONS AS READ
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def mark_all_admin_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    messages.success(
        request,
        "All notifications marked as read."
    )

    return redirect(
        "admin_notifications"
    )


# =========================================================
# ADMIN SEND NOTIFICATION
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def send_notification(request):

    if request.method == "POST":

        recipient = request.POST.get(
            "recipient",
            ""
        ).strip()

        title = request.POST.get(
            "title",
            ""
        ).strip()

        message = request.POST.get(
            "message",
            ""
        ).strip()

        notification_type = request.POST.get(
            "notification_type",
            "general"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            messages.error(
                request,
                "Please enter a notification title."
            )

            return redirect(
                "send_notification"
            )

        if not message:

            messages.error(
                request,
                "Please enter a notification message."
            )

            return redirect(
                "send_notification"
            )

        if notification_type not in dict(
            Notification.NOTIFICATION_TYPES
        ):

            notification_type = "general"

        # -------------------------------------------------
        # ALL CUSTOMERS
        # -------------------------------------------------

        if recipient == "all":

            customers = User.objects.filter(
                is_active=True,
                is_staff=False,
                is_superuser=False
            )

            notifications = [

                Notification(

                    user=customer,

                    title=title,

                    message=message,

                    notification_type=notification_type,

                    is_read=False

                )

                for customer in customers

            ]

            if notifications:

                Notification.objects.bulk_create(
                    notifications
                )

                messages.success(
                    request,
                    f"Notification sent to "
                    f"{len(notifications)} customer(s)."
                )

            else:

                messages.warning(
                    request,
                    "No active customers found."
                )

            return redirect(
                "admin_notifications"
            )

        # -------------------------------------------------
        # ONE CUSTOMER
        # -------------------------------------------------

        try:

            customer = User.objects.get(

                id=recipient,

                is_active=True,

                is_staff=False,

                is_superuser=False
            )

        except (
            User.DoesNotExist,
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Selected customer was not found."
            )

            return redirect(
                "send_notification"
            )

        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------

        Notification.objects.create(

            user=customer,

            title=title,

            message=message,

            notification_type=notification_type,

            is_read=False
        )

        messages.success(
            request,
            f"Notification sent successfully to "
            f"{customer.get_full_name() or customer.username}."
        )

        return redirect(
            "admin_notifications"
        )

    # -----------------------------------------------------
    # CUSTOMER LIST
    # -----------------------------------------------------

    customers = (
        User.objects
        .filter(
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        .order_by(
            "first_name",
            "last_name",
            "username"
        )
    )

    return render(
        request,
        "dashboard/send_notification.html",
        {
            "customers":
                customers,

            "notification_types":
                Notification.NOTIFICATION_TYPES,
        }
    )


# =========================================================
# REPORTS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def reports(request):

    from django.db.models.functions import TruncMonth

    today = timezone.localdate()

    # -----------------------------------------------------
    # BOOKINGS
    # -----------------------------------------------------

    bookings = (
        Booking.objects
        .select_related(
            "user",
            "room",
            "room__category"
        )
    )

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status="pending"
    ).count()

    confirmed_bookings = bookings.filter(
        status="confirmed"
    ).count()

    checked_in_bookings = bookings.filter(
        status="checked_in"
    ).count()

    checked_out_bookings = bookings.filter(
        status="checked_out"
    ).count()

    cancelled_bookings = bookings.filter(
        status="cancelled"
    ).count()

    # -----------------------------------------------------
    # PAYMENTS
    # -----------------------------------------------------

    total_payments = Payment.objects.count()

    completed_payments = (
        Payment.objects
        .filter(
            status="completed"
        )
        .count()
    )

    pending_payments = (
        Payment.objects
        .filter(
            status="pending"
        )
        .count()
    )

    failed_payments = (
        Payment.objects
        .filter(
            status="failed"
        )
        .count()
    )

    refunded_payments = (
        Payment.objects
        .filter(
            status="refunded"
        )
        .count()
    )

    # -----------------------------------------------------
    # REVENUE
    # -----------------------------------------------------

    total_revenue = (
        Payment.objects
        .filter(
            status="completed"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    pending_revenue = (
        Payment.objects
        .filter(
            status="pending"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    refunded_amount = (
        Payment.objects
        .filter(
            status="refunded"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    today_bookings = bookings.filter(
        check_in=today
    ).count()

    today_checkouts = bookings.filter(
        check_out=today
    ).count()

    today_revenue = (
        Payment.objects
        .filter(
            status="completed",
            paid_at__date=today
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    # -----------------------------------------------------
    # MONTHLY REVENUE
    # -----------------------------------------------------

    monthly_revenue = (
        Payment.objects
        .filter(
            status="completed",
            paid_at__isnull=False
        )
        .annotate(
            month=TruncMonth("paid_at")
        )
        .values(
            "month"
        )
        .annotate(
            revenue=Sum("amount")
        )
        .order_by(
            "month"
        )
    )

    monthly_revenue_data = []

    for item in monthly_revenue:

        monthly_revenue_data.append({

            "month":
                item["month"].strftime(
                    "%b %Y"
                ),

            "revenue":
                float(
                    item["revenue"]
                    or 0
                ),
        })

    # -----------------------------------------------------
    # BOOKING STATUS
    # -----------------------------------------------------

    booking_status_data = [

        {
            "label":
                "Pending",

            "value":
                pending_bookings,
        },

        {
            "label":
                "Confirmed",

            "value":
                confirmed_bookings,
        },

        {
            "label":
                "Checked In",

            "value":
                checked_in_bookings,
        },

        {
            "label":
                "Checked Out",

            "value":
                checked_out_bookings,
        },

        {
            "label":
                "Cancelled",

            "value":
                cancelled_bookings,
        },

    ]

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    payment_status_data = [

        {
            "label":
                "Completed",

            "value":
                completed_payments,
        },

        {
            "label":
                "Pending",

            "value":
                pending_payments,
        },

        {
            "label":
                "Failed",

            "value":
                failed_payments,
        },

        {
            "label":
                "Refunded",

            "value":
                refunded_payments,
        },

    ]

    # -----------------------------------------------------
    # RECENT BOOKINGS
    # -----------------------------------------------------

    recent_bookings = (
        bookings
        .order_by(
            "-created_at"
        )[:10]
    )

    # -----------------------------------------------------
    # ROOMS
    # -----------------------------------------------------

    total_rooms = Room.objects.count()

    available_rooms = (
        Room.objects
        .filter(
            status="available"
        )
        .count()
    )

    occupied_rooms = (
        Room.objects
        .filter(
            status="occupied"
        )
        .count()
    )

    maintenance_rooms = (
        Room.objects
        .filter(
            status="maintenance"
        )
        .count()
    )

    inactive_rooms = (
        Room.objects
        .filter(
            status="inactive"
        )
        .count()
    )

    occupancy_percentage = 0

    if total_rooms > 0:

        occupancy_percentage = round(
            (
                occupied_rooms
                / total_rooms
            ) * 100,
            1
        )

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    total_customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .count()
    )

    context = {

        "today":
            today,

        "total_bookings":
            total_bookings,

        "pending_bookings":
            pending_bookings,

        "confirmed_bookings":
            confirmed_bookings,

        "checked_in_bookings":
            checked_in_bookings,

        "checked_out_bookings":
            checked_out_bookings,

        "cancelled_bookings":
            cancelled_bookings,

        "total_payments":
            total_payments,

        "completed_payments":
            completed_payments,

        "pending_payments":
            pending_payments,

        "failed_payments":
            failed_payments,

        "refunded_payments":
            refunded_payments,

        "total_revenue":
            total_revenue,

        "pending_revenue":
            pending_revenue,

        "refunded_amount":
            refunded_amount,

        "today_revenue":
            today_revenue,

        "today_bookings":
            today_bookings,

        "today_checkouts":
            today_checkouts,

        "monthly_revenue_data":
            monthly_revenue_data,

        "booking_status_data":
            booking_status_data,

        "payment_status_data":
            payment_status_data,

        "total_rooms":
            total_rooms,

        "available_rooms":
            available_rooms,

        "occupied_rooms":
            occupied_rooms,

        "maintenance_rooms":
            maintenance_rooms,

        "inactive_rooms":
            inactive_rooms,

        "occupancy_percentage":
            occupancy_percentage,

        "total_customers":
            total_customers,

        "recent_bookings":
            recent_bookings,
    }

    return render(
        request,
        "dashboard/reports.html",
        context
    )


# =========================================================
# ANALYTICS
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def analytics(request):

    from django.db.models import Count
    from django.db.models.functions import TruncMonth

    today = timezone.localdate()

    # -----------------------------------------------------
    # BOOKINGS
    # -----------------------------------------------------

    bookings = (
        Booking.objects
        .select_related(
            "user",
            "room",
            "room__category"
        )
    )

    total_bookings = bookings.count()

    confirmed_bookings = bookings.filter(
        status="confirmed"
    ).count()

    pending_bookings = bookings.filter(
        status="pending"
    ).count()

    checked_in_bookings = bookings.filter(
        status="checked_in"
    ).count()

    checked_out_bookings = bookings.filter(
        status="checked_out"
    ).count()

    cancelled_bookings = bookings.filter(
        status="cancelled"
    ).count()

    # -----------------------------------------------------
    # PAYMENTS
    # -----------------------------------------------------

    completed_payments = (
        Payment.objects
        .filter(
            status="completed"
        )
    )

    total_revenue = (
        completed_payments
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    total_payments = Payment.objects.count()

    completed_payment_count = (
        completed_payments.count()
    )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    today_bookings = bookings.filter(
        created_at__date=today
    ).count()

    today_revenue = (
        Payment.objects
        .filter(
            status="completed",
            paid_at__date=today
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    today_checkins = bookings.filter(
        check_in=today
    ).count()

    today_checkouts = bookings.filter(
        check_out=today
    ).count()

    # -----------------------------------------------------
    # MONTHLY REVENUE
    # -----------------------------------------------------

    monthly_revenue = (
        Payment.objects
        .filter(
            status="completed",
            paid_at__isnull=False
        )
        .annotate(
            month=TruncMonth(
                "paid_at"
            )
        )
        .values(
            "month"
        )
        .annotate(
            revenue=Sum("amount")
        )
        .order_by(
            "month"
        )
    )

    revenue_chart = []

    for item in monthly_revenue:

        revenue_chart.append({

            "month":
                item["month"].strftime(
                    "%b %Y"
                ),

            "revenue":
                float(
                    item["revenue"]
                    or 0
                ),
        })

    # -----------------------------------------------------
    # MONTHLY BOOKINGS
    # -----------------------------------------------------

    monthly_bookings = (
        Booking.objects
        .annotate(
            month=TruncMonth(
                "created_at"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "month"
        )
    )

    booking_chart = []

    for item in monthly_bookings:

        booking_chart.append({

            "month":
                item["month"].strftime(
                    "%b %Y"
                ),

            "bookings":
                item["total"],
        })

    # -----------------------------------------------------
    # ROOMS
    # -----------------------------------------------------

    total_rooms = Room.objects.count()

    available_rooms = (
        Room.objects
        .filter(
            status="available"
        )
        .count()
    )

    occupied_rooms = (
        Room.objects
        .filter(
            status="occupied"
        )
        .count()
    )

    maintenance_rooms = (
        Room.objects
        .filter(
            status="maintenance"
        )
        .count()
    )

    inactive_rooms = (
        Room.objects
        .filter(
            status="inactive"
        )
        .count()
    )

    occupancy_percentage = 0

    if total_rooms > 0:

        occupancy_percentage = round(
            (
                occupied_rooms
                / total_rooms
            ) * 100,
            1
        )

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    total_customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .count()
    )

    active_customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        .count()
    )

    customers_with_bookings = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False,
            bookings__isnull=False
        )
        .distinct()
        .count()
    )

    # -----------------------------------------------------
    # BOOKING SUCCESS RATE
    # -----------------------------------------------------

    booking_success_rate = 0

    if total_bookings > 0:

        booking_success_rate = round(

            (

                (
                    confirmed_bookings
                    + checked_in_bookings
                    + checked_out_bookings
                )

                / total_bookings

            ) * 100,

            1
        )

    # -----------------------------------------------------
    # PAYMENT SUCCESS RATE
    # -----------------------------------------------------

    payment_success_rate = 0

    if total_payments > 0:

        payment_success_rate = round(

            (
                completed_payment_count
                / total_payments
            ) * 100,

            1
        )

    # -----------------------------------------------------
    # RECENT BOOKINGS
    # -----------------------------------------------------

    recent_bookings = (
        bookings
        .order_by(
            "-created_at"
        )[:10]
    )

    # -----------------------------------------------------
    # TOP ROOMS
    # -----------------------------------------------------

    top_rooms = (
        Room.objects
        .annotate(
            booking_count=Count(
                "bookings"
            )
        )
        .order_by(
            "-booking_count"
        )[:5]
    )

    context = {

        "total_bookings":
            total_bookings,

        "confirmed_bookings":
            confirmed_bookings,

        "pending_bookings":
            pending_bookings,

        "checked_in_bookings":
            checked_in_bookings,

        "checked_out_bookings":
            checked_out_bookings,

        "cancelled_bookings":
            cancelled_bookings,

        "total_revenue":
            total_revenue,

        "today_revenue":
            today_revenue,

        "total_payments":
            total_payments,

        "completed_payment_count":
            completed_payment_count,

        "today_bookings":
            today_bookings,

        "today_checkins":
            today_checkins,

        "today_checkouts":
            today_checkouts,

        "revenue_chart":
            revenue_chart,

        "booking_chart":
            booking_chart,

        "total_rooms":
            total_rooms,

        "available_rooms":
            available_rooms,

        "occupied_rooms":
            occupied_rooms,

        "maintenance_rooms":
            maintenance_rooms,

        "inactive_rooms":
            inactive_rooms,

        "occupancy_percentage":
            occupancy_percentage,

        "total_customers":
            total_customers,

        "active_customers":
            active_customers,

        "customers_with_bookings":
            customers_with_bookings,

        "booking_success_rate":
            booking_success_rate,

        "payment_success_rate":
            payment_success_rate,

        "recent_bookings":
            recent_bookings,

        "top_rooms":
            top_rooms,

        "today":
            today,
    }

    return render(
        request,
        "dashboard/analytics.html",
        context
    )


# =========================================================
# ADMIN PROFILE
# =========================================================

@staff_member_required(
    login_url="dashboard_login"
)
def admin_profile(request):

    return render(
        request,
        "dashboard/profile.html",
        {
            "admin_user":
                request.user,
        }
    )