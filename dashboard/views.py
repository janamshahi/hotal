from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum, Avg


from hotel.models import Hotel, Service
from rooms.models import Room, RoomCategory
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review
from django.contrib.auth.models import User


# =========================================================
# DASHBOARD LOGIN
# =========================================================

def dashboard_login(request):

    # -----------------------------------------------------
    # ALREADY LOGGED-IN USER
    # -----------------------------------------------------

    if request.user.is_authenticated:

        if (
            request.user.is_staff
            or request.user.is_superuser
        ):

            return redirect('dashboard')

        logout(request)


    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user is not None:

            # -------------------------------------------------
            # STAFF / SUPERUSER CHECK
            # -------------------------------------------------

            if (
                user.is_staff
                or user.is_superuser
            ):

                login(
                    request,
                    user
                )

                return redirect(
                    'dashboard'
                )


            messages.error(
                request,
                'You do not have permission to access the dashboard.'
            )


        else:

            messages.error(
                request,
                'Invalid username or password.'
            )


    return render(
        request,
        'dashboard/login.html'
    )


# =========================================================
# DASHBOARD LOGOUT
# =========================================================

def dashboard_logout(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect(
        'dashboard_login'
    )


# =========================================================
# DASHBOARD HOME
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
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

    total_rooms = (
        Room.objects.count()
    )

    available_rooms = (
        Room.objects
        .filter(
            status='available'
        )
        .count()
    )

    maintenance_rooms = (
        Room.objects
        .filter(
            status='maintenance'
        )
        .count()
    )

    inactive_rooms = (
        Room.objects
        .filter(
            status='inactive'
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
            status='available'
        )
        .select_related(
            'category'
        )
        .order_by(
            'room_number'
        )[:5]
    )


    # -----------------------------------------------------
    # RECENT ROOMS
    # -----------------------------------------------------

    recent_rooms = (
        Room.objects
        .select_related(
            'category'
        )
        .order_by(
            '-created_at'
        )[:5]
    )


    context = {

        'hotel': hotel,

        'total_rooms':
            total_rooms,

        'available_rooms':
            available_rooms,

        'maintenance_rooms':
            maintenance_rooms,

        'inactive_rooms':
            inactive_rooms,

        'total_categories':
            total_categories,

        'active_categories':
            active_categories,

        'total_services':
            total_services,

        'active_services':
            active_services,

        'featured_rooms':
            featured_rooms,

        'recent_rooms':
            recent_rooms,

    }


    return render(
        request,
        'dashboard/home.html',
        context
    )


# =========================================================
# MANAGE ROOMS
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def manage_rooms(request):

    rooms = (
        Room.objects
        .select_related(
            'category'
        )
        .order_by(
            'room_number'
        )
    )


    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            'name'
        )
    )


    context = {

        'rooms':
            rooms,

        'categories':
            categories,

    }


    return render(
        request,
        'dashboard/rooms.html',
        context
    )


# =========================================================
# ADD ROOM
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def add_room(request):

    categories = (
        RoomCategory.objects
        .filter(
            is_active=True
        )
        .order_by(
            'name'
        )
    )


    if request.method == 'POST':

        category_id = request.POST.get(
            'category'
        )

        room_number = request.POST.get(
            'room_number',
            ''
        ).strip()

        name = request.POST.get(
            'name',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        price = request.POST.get(
            'price'
        )

        capacity = request.POST.get(
            'capacity'
        )

        size = request.POST.get(
            'size'
        )

        bed_type = request.POST.get(
            'bed_type',
            'Double Bed'
        ).strip()

        floor = request.POST.get(
            'floor'
        )

        status = request.POST.get(
            'status',
            'available'
        )


        is_featured = (
            request.POST.get(
                'is_featured'
            ) == 'on'
        )

        has_wifi = (
            request.POST.get(
                'has_wifi'
            ) == 'on'
        )

        has_ac = (
            request.POST.get(
                'has_ac'
            ) == 'on'
        )

        has_tv = (
            request.POST.get(
                'has_tv'
            ) == 'on'
        )

        has_breakfast = (
            request.POST.get(
                'has_breakfast'
            ) == 'on'
        )

        has_balcony = (
            request.POST.get(
                'has_balcony'
            ) == 'on'
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not category_id:

            messages.error(
                request,
                'Please select a room category.'
            )

            return render(
                request,
                'dashboard/room_form.html',
                {
                    'categories': categories,
                    'form_data': request.POST
                }
            )


        if not room_number or not name:

            messages.error(
                request,
                'Room number and room name are required.'
            )

            return render(
                request,
                'dashboard/room_form.html',
                {
                    'categories': categories,
                    'form_data': request.POST
                }
            )


        if Room.objects.filter(
            room_number=room_number
        ).exists():

            messages.error(
                request,
                'This room number already exists.'
            )

            return render(
                request,
                'dashboard/room_form.html',
                {
                    'categories': categories,
                    'form_data': request.POST
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
                'image'
            ):

                room.image = (
                    request.FILES.get(
                        'image'
                    )
                )


            room.save()


            messages.success(
                request,
                f'Room {room.room_number} added successfully.'
            )


            return redirect(
                'manage_rooms'
            )


        except Exception as e:

            messages.error(
                request,
                f'Unable to add room: {e}'
            )


    return render(
        request,
        'dashboard/room_form.html',
        {
            'categories': categories
        }
    )


# =========================================================
# EDIT ROOM
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
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
            'name'
        )
    )


    if request.method == 'POST':

        category_id = request.POST.get(
            'category'
        )

        room_number = request.POST.get(
            'room_number',
            ''
        ).strip()

        name = request.POST.get(
            'name',
            ''
        ).strip()


        if not category_id:

            messages.error(
                request,
                'Please select a room category.'
            )

            return redirect(
                'edit_room',
                room_id=room.id
            )


        if not room_number or not name:

            messages.error(
                request,
                'Room number and room name are required.'
            )

            return redirect(
                'edit_room',
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
                'Another room already uses this room number.'
            )

            return redirect(
                'edit_room',
                room_id=room.id
            )


        room.category_id = (
            category_id
        )

        room.room_number = (
            room_number
        )

        room.name = (
            name
        )

        room.description = (
            request.POST.get(
                'description',
                ''
            ).strip()
        )

        room.price = (
            request.POST.get(
                'price'
            )
        )

        room.capacity = (
            request.POST.get(
                'capacity'
            )
        )

        room.size = (
            request.POST.get(
                'size'
            )
        )

        room.bed_type = (
            request.POST.get(
                'bed_type',
                'Double Bed'
            ).strip()
        )

        room.floor = (
            request.POST.get(
                'floor'
            )
        )

        room.status = (
            request.POST.get(
                'status',
                'available'
            )
        )


        room.is_featured = (
            request.POST.get(
                'is_featured'
            ) == 'on'
        )

        room.has_wifi = (
            request.POST.get(
                'has_wifi'
            ) == 'on'
        )

        room.has_ac = (
            request.POST.get(
                'has_ac'
            ) == 'on'
        )

        room.has_tv = (
            request.POST.get(
                'has_tv'
            ) == 'on'
        )

        room.has_breakfast = (
            request.POST.get(
                'has_breakfast'
            ) == 'on'
        )

        room.has_balcony = (
            request.POST.get(
                'has_balcony'
            ) == 'on'
        )


        if request.FILES.get(
            'image'
        ):

            room.image = (
                request.FILES.get(
                    'image'
                )
            )


        room.save()


        messages.success(
            request,
            f'Room {room.room_number} updated successfully.'
        )


        return redirect(
            'manage_rooms'
        )


    return render(
        request,
        'dashboard/room_form.html',
        {
            'room': room,
            'categories': categories,
            'edit_mode': True
        }
    )


# =========================================================
# DELETE ROOM
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def delete_room(
    request,
    room_id
):

    room = get_object_or_404(
        Room,
        id=room_id
    )


    if request.method == 'POST':

        room_number = (
            room.room_number
        )

        room.delete()


        messages.success(
            request,
            f'Room {room_number} deleted successfully.'
        )


    return redirect(
        'manage_rooms'
    )


# =========================================================
# ROOM CATEGORY MANAGEMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def manage_categories(request):

    categories = (
        RoomCategory.objects
        .prefetch_related(
            'rooms'
        )
        .order_by(
            'name'
        )
    )


    context = {

        'categories':
            categories,

    }


    return render(
        request,
        'dashboard/categories.html',
        context
    )


# =========================================================
# ADD CATEGORY
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def add_category(request):

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        max_guests = request.POST.get(
            'max_guests',
            ''
        ).strip()

        is_active = (
            request.POST.get(
                'is_active'
            ) == 'on'
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:

            messages.error(
                request,
                'Category name is required.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'form_data': request.POST,
                    'page_title':
                        'Add Room Category',
                }
            )


        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        if (
            RoomCategory.objects
            .filter(
                name__iexact=name
            )
            .exists()
        ):

            messages.error(
                request,
                'A room category with this name already exists.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'form_data': request.POST,
                    'page_title':
                        'Add Room Category',
                }
            )


        # -------------------------------------------------
        # MAX GUESTS
        # -------------------------------------------------

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
                'Maximum guests must be a valid number greater than 0.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'form_data': request.POST,
                    'page_title':
                        'Add Room Category',
                }
            )


        # -------------------------------------------------
        # CREATE CATEGORY
        # -------------------------------------------------

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
            'manage_categories'
        )


    return render(
        request,
        'dashboard/category_form.html',
        {
            'page_title':
                'Add Room Category',
        }
    )


# =========================================================
# EDIT CATEGORY
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def edit_category(
    request,
    category_id
):

    category = get_object_or_404(
        RoomCategory,
        id=category_id
    )


    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        max_guests = request.POST.get(
            'max_guests',
            ''
        ).strip()

        is_active = (
            request.POST.get(
                'is_active'
            ) == 'on'
        )


        # -------------------------------------------------
        # NAME VALIDATION
        # -------------------------------------------------

        if not name:

            messages.error(
                request,
                'Category name is required.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'category': category,
                    'form_data': request.POST,
                    'page_title':
                        'Edit Room Category',
                }
            )


        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

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
                'Another room category with this name already exists.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'category': category,
                    'form_data': request.POST,
                    'page_title':
                        'Edit Room Category',
                }
            )


        # -------------------------------------------------
        # MAX GUESTS
        # -------------------------------------------------

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
                'Maximum guests must be a valid number greater than 0.'
            )

            return render(
                request,
                'dashboard/category_form.html',
                {
                    'category': category,
                    'form_data': request.POST,
                    'page_title':
                        'Edit Room Category',
                }
            )


        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        category.name = name

        category.description = (
            description
        )

        category.max_guests = (
            max_guests
        )

        category.is_active = (
            is_active
        )

        category.save()


        messages.success(
            request,
            f'Room category "{name}" updated successfully.'
        )


        return redirect(
            'manage_categories'
        )


    return render(
        request,
        'dashboard/category_form.html',
        {
            'category': category,
            'page_title':
                'Edit Room Category',
        }
    )


# =========================================================
# DELETE CATEGORY
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def delete_category(
    request,
    category_id
):

    if request.method != 'POST':

        return redirect(
            'manage_categories'
        )


    category = get_object_or_404(
        RoomCategory,
        id=category_id
    )


    room_count = (
        category.rooms.count()
    )


    if room_count > 0:

        messages.error(
            request,
            (
                f'Cannot delete "{category.name}" because '
                f'{room_count} room(s) are using this category. '
                f'Please move or remove those rooms first.'
            )
        )

        return redirect(
            'manage_categories'
        )


    category_name = (
        category.name
    )

    category.delete()


    messages.success(
        request,
        f'Room category "{category_name}" deleted successfully.'
    )


    return redirect(
        'manage_categories'
    )


# =========================================================
# BOOKING MANAGEMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def manage_bookings(request):

    bookings = (
        Booking.objects
        .select_related(
            'user',
            'room',
            'room__category'
        )
        .order_by(
            '-created_at'
        )
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        'search',
        ''
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
    # BOOKING STATUS FILTER
    # -----------------------------------------------------

    status = request.GET.get(
        'status',
        ''
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
    # PAYMENT STATUS FILTER
    # -----------------------------------------------------

    payment_status = request.GET.get(
        'payment_status',
        ''
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

    total_bookings = (
        Booking.objects.count()
    )

    pending_bookings = (
        Booking.objects
        .filter(
            status='pending'
        )
        .count()
    )

    confirmed_bookings = (
        Booking.objects
        .filter(
            status='confirmed'
        )
        .count()
    )

    checked_in_bookings = (
        Booking.objects
        .filter(
            status='checked_in'
        )
        .count()
    )

    paid_bookings = (
        Booking.objects
        .filter(
            payment_status='paid'
        )
        .count()
    )


    context = {

        'bookings':
            bookings,

        'total_bookings':
            total_bookings,

        'pending_bookings':
            pending_bookings,

        'confirmed_bookings':
            confirmed_bookings,

        'checked_in_bookings':
            checked_in_bookings,

        'paid_bookings':
            paid_bookings,

        'search':
            search,

        'selected_status':
            status,

        'selected_payment_status':
            payment_status,

        'status_choices':
            Booking.STATUS_CHOICES,

        'payment_status_choices':
            Booking.PAYMENT_STATUS_CHOICES,

    }


    return render(
        request,
        'dashboard/bookings.html',
        context
    )


# =========================================================
# ADMIN BOOKING DETAIL
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def booking_detail(
    request,
    booking_id
):

    # -----------------------------------------------------
    # GET BOOKING
    # -----------------------------------------------------

    booking = get_object_or_404(

        Booking.objects.select_related(
            'user',
            'room',
            'room__category'
        ),

        id=booking_id

    )


    # -----------------------------------------------------
    # CALCULATE TOTAL NIGHTS
    # -----------------------------------------------------

    total_nights = (
        booking.check_out
        - booking.check_in
    ).days


    # -----------------------------------------------------
    # ADMIN DETAIL CONTEXT
    # -----------------------------------------------------

    context = {

        'booking':
            booking,

        'total_nights':
            total_nights,

        'status_choices':
            Booking.STATUS_CHOICES,

        'payment_status_choices':
            Booking.PAYMENT_STATUS_CHOICES,

    }


    # -----------------------------------------------------
    # IMPORTANT:
    # ADMIN TEMPLATE
    # -----------------------------------------------------

    return render(
        request,
        'dashboard/booking_detail.html',
        context
    )


# =========================================================
# UPDATE BOOKING
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def update_booking(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )


    # -----------------------------------------------------
    # ONLY POST ALLOWED
    # -----------------------------------------------------

    if request.method != 'POST':

        return redirect(
            'dashboard_booking_detail',
            booking_id=booking.id
        )


    # -----------------------------------------------------
    # BOOKING STATUS
    # -----------------------------------------------------

    new_status = request.POST.get(
        'status'
    )


    valid_statuses = dict(
        Booking.STATUS_CHOICES
    )


    if new_status not in valid_statuses:

        messages.error(
            request,
            'Invalid booking status.'
        )

        return redirect(
            'dashboard_booking_detail',
            booking_id=booking.id
        )


    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    new_payment_status = request.POST.get(
        'payment_status'
    )


    valid_payment_statuses = dict(
        Booking.PAYMENT_STATUS_CHOICES
    )


    if (
        new_payment_status
        not in valid_payment_statuses
    ):

        messages.error(
            request,
            'Invalid payment status.'
        )

        return redirect(
            'dashboard_booking_detail',
            booking_id=booking.id
        )


    # -----------------------------------------------------
    # UPDATE BOOKING
    # -----------------------------------------------------

    booking.status = (
        new_status
    )

    booking.payment_status = (
        new_payment_status
    )

    booking.save()


    messages.success(
        request,
        f'Booking #{booking.id} updated successfully.'
    )


    # -----------------------------------------------------
    # IMPORTANT:
    # RETURN TO ADMIN DETAIL PAGE
    # -----------------------------------------------------

    return redirect(
        'dashboard_booking_detail',
        booking_id=booking.id
    )


# =========================================================
# DELETE BOOKING
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def delete_booking(
    request,
    booking_id
):

    if request.method != 'POST':

        return redirect(
            'manage_bookings'
        )


    booking = get_object_or_404(
        Booking,
        id=booking_id
    )


    booking_id_value = (
        booking.id
    )


    booking.delete()


    messages.success(
        request,
        f'Booking #{booking_id_value} deleted successfully.'
    )


    return redirect(
        'manage_bookings'
    )


# =========================================================
# PAYMENT MANAGEMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def manage_payments(request):

    payments = (
        Payment.objects
        .select_related(
            'booking',
            'booking__user',
            'booking__room',
            'booking__room__category'
        )
        .order_by(
            '-created_at'
        )
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        'search',
        ''
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
    # STATUS FILTER
    # -----------------------------------------------------

    status = request.GET.get(
        'status',
        ''
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
    # METHOD FILTER
    # -----------------------------------------------------

    method = request.GET.get(
        'method',
        ''
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

    total_payments = (
        Payment.objects.count()
    )

    pending_payments = (
        Payment.objects
        .filter(
            status='pending'
        )
        .count()
    )

    completed_payments = (
        Payment.objects
        .filter(
            status='completed'
        )
        .count()
    )

    failed_payments = (
        Payment.objects
        .filter(
            status='failed'
        )
        .count()
    )

    refunded_payments = (
        Payment.objects
        .filter(
            status='refunded'
        )
        .count()
    )


    total_revenue = (

        Payment.objects
        .filter(
            status='completed'
        )
        .aggregate(
            total=Sum('amount')
        )['total']

        or 0

    )


    context = {

        'payments':
            payments,

        'total_payments':
            total_payments,

        'pending_payments':
            pending_payments,

        'completed_payments':
            completed_payments,

        'failed_payments':
            failed_payments,

        'refunded_payments':
            refunded_payments,

        'total_revenue':
            total_revenue,

        'search':
            search,

        'selected_status':
            status,

        'selected_method':
            method,

        'status_choices':
            Payment.STATUS_CHOICES,

        'method_choices':
            Payment.METHOD_CHOICES,

    }


    return render(
        request,
        'dashboard/payments.html',
        context
    )


# =========================================================
# PAYMENT DETAIL
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def payment_detail(
    request,
    payment_id
):

    payment = get_object_or_404(

        Payment.objects.select_related(
            'booking',
            'booking__user',
            'booking__room',
            'booking__room__category'
        ),

        id=payment_id

    )


    context = {

        'payment':
            payment,

        'status_choices':
            Payment.STATUS_CHOICES,

        'method_choices':
            Payment.METHOD_CHOICES,

    }


    return render(
        request,
        'dashboard/payment_detail.html',
        context
    )


# =========================================================
# UPDATE PAYMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def update_payment(
    request,
    payment_id
):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )


    if request.method != 'POST':

        return redirect(
            'payment_detail',
            payment_id=payment.id
        )


    # -----------------------------------------------------
    # NEW STATUS
    # -----------------------------------------------------

    new_status = request.POST.get(
        'status'
    )


    # -----------------------------------------------------
    # NEW METHOD
    # -----------------------------------------------------

    new_method = request.POST.get(
        'method'
    )


    valid_statuses = dict(
        Payment.STATUS_CHOICES
    )

    valid_methods = dict(
        Payment.METHOD_CHOICES
    )


    if new_status not in valid_statuses:

        messages.error(
            request,
            'Invalid payment status.'
        )

        return redirect(
            'payment_detail',
            payment_id=payment.id
        )


    if new_method not in valid_methods:

        messages.error(
            request,
            'Invalid payment method.'
        )

        return redirect(
            'payment_detail',
            payment_id=payment.id
        )


    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    payment.status = (
        new_status
    )

    payment.method = (
        new_method
    )

    payment.save()


    messages.success(
        request,
        f'Payment #{payment.id} updated successfully.'
    )


    return redirect(
        'payment_detail',
        payment_id=payment.id
    )


# =========================================================
# DELETE PAYMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def delete_payment(
    request,
    payment_id
):

    if request.method != 'POST':

        return redirect(
            'manage_payments'
        )


    payment = get_object_or_404(
        Payment,
        id=payment_id
    )


    payment_id_value = (
        payment.id
    )


    payment.delete()


    messages.success(
        request,
        f'Payment #{payment_id_value} deleted successfully.'
    )


    return redirect(
        'manage_payments'
    )


# =========================================================
# REVIEW MANAGEMENT
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def manage_reviews(request):

    reviews = (
        Review.objects
        .select_related(
            'user',
            'room',
            'room__category'
        )
        .order_by(
            '-created_at'
        )
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        'search',
        ''
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


    # -----------------------------------------------------
    # APPROVAL FILTER
    # -----------------------------------------------------

    approval = request.GET.get(
        'approval',
        ''
    ).strip()


    if approval == 'approved':

        reviews = reviews.filter(
            is_approved=True
        )


    elif approval == 'pending':

        reviews = reviews.filter(
            is_approved=False
        )


    # -----------------------------------------------------
    # RATING FILTER
    # -----------------------------------------------------

    rating = request.GET.get(
        'rating',
        ''
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


    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    total_reviews = (
        Review.objects.count()
    )

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
            average=Avg('rating')
        )['average']

        or 0

    )


    context = {

        'reviews':
            reviews,

        'total_reviews':
            total_reviews,

        'approved_reviews':
            approved_reviews,

        'pending_reviews':
            pending_reviews,

        'five_star_reviews':
            five_star_reviews,

        'average_rating':
            round(
                float(average_rating),
                1
            ),

        'search':
            search,

        'selected_approval':
            approval,

        'selected_rating':
            rating,

        'rating_choices':
            Review.RATING_CHOICES,

    }


    return render(
        request,
        'dashboard/reviews.html',
        context
    )


# =========================================================
# REVIEW DETAIL
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def review_detail(
    request,
    review_id
):

    review = get_object_or_404(

        Review.objects.select_related(
            'user',
            'room',
            'room__category'
        ),

        id=review_id

    )


    return render(
        request,
        'dashboard/review_detail.html',
        {
            'review': review,
        }
    )


# =========================================================
# APPROVE / UNAPPROVE REVIEW
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def toggle_review_approval(
    request,
    review_id
):

    if request.method != 'POST':

        return redirect(
            'manage_reviews'
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
            'is_approved'
        ]
    )


    if review.is_approved:

        messages.success(
            request,
            f'Review #{review.id} approved successfully.'
        )

    else:

        messages.success(
            request,
            f'Review #{review.id} unapproved successfully.'
        )


    return redirect(
        'manage_reviews'
    )


# =========================================================
# DELETE REVIEW
# =========================================================

@staff_member_required(
    login_url='dashboard_login'
)
def delete_review(
    request,
    review_id
):

    if request.method != 'POST':

        return redirect(
            'manage_reviews'
        )


    review = get_object_or_404(
        Review,
        id=review_id
    )


    review_id_value = (
        review.id
    )


    review.delete()


    messages.success(
        request,
        f'Review #{review_id_value} deleted successfully.'
    )


    return redirect(
        'manage_reviews'
    )

# =========================================================
# CUSTOMERS
# =========================================================

@staff_member_required(login_url='dashboard_login')
def manage_customers(request):

    customers = (
        User.objects
        .filter(is_staff=False, is_superuser=False)
        .select_related('customer_profile')
        .prefetch_related('bookings')
        .order_by('-date_joined')
    )

    search = request.GET.get('search', '').strip()

    if search:

        customers = customers.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(customer_profile__phone__icontains=search)
        )

    context = {
        'customers': customers,
        'search': search,
    }

    return render(
        request,
        'dashboard/customers.html',
        context
    )


# =========================================================
# CUSTOMER DETAIL
# =========================================================

@staff_member_required(login_url='dashboard_login')
def customer_detail(request, user_id):

    customer = get_object_or_404(
        User.objects
        .select_related('customer_profile')
        .prefetch_related(
            'bookings__room',
            'bookings__room__category'
        ),
        id=user_id
    )

    bookings = customer.bookings.all().order_by('-created_at')

    context = {
        'customer': customer,
        'bookings': bookings,
    }

    return render(
        request,
        'dashboard/customer_detail.html',
        context
    )


# =========================================================
# DELETE CUSTOMER
# =========================================================

@staff_member_required(login_url='dashboard_login')
def delete_customer(request, user_id):

    if request.method == 'POST':

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

    return redirect('manage_customers')