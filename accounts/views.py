from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from django.shortcuts import render, redirect

from .models import Customer

from .forms import (
    RegisterForm,
    ProfileUpdateForm,
    UserUpdateForm,
)


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    # -----------------------------------------------------
    # If already logged in
    # -----------------------------------------------------

    if request.user.is_authenticated:

        # Admin / Staff -> Dashboard
        if (
            request.user.is_staff
            or request.user.is_superuser
        ):
            return redirect("dashboard")

        # Customer -> Home
        return redirect("home")

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        form = RegisterForm(
            request.POST
        )

        # -------------------------------------------------
        # Validate form
        # -------------------------------------------------

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Account created successfully. Please login."
            )

            return redirect("login")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:

        form = RegisterForm()

    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# =========================================================
# CUSTOMER LOGIN
# =========================================================
#
# URL:
# /accounts/login/
#
# Normal customers can login here.
# Admin / Staff accounts cannot login here.
# Admin / Staff must use:
# /dashboard/login/
# =========================================================

def login_view(request):

    # -----------------------------------------------------
    # Already logged in
    # -----------------------------------------------------

    if request.user.is_authenticated:

        # Admin / Staff -> Dashboard
        if (
            request.user.is_staff
            or request.user.is_superuser
        ):
            return redirect("dashboard")

        # Customer -> Home
        return redirect("home")

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # Validate fields
        # -------------------------------------------------

        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "accounts/login.html"
            )

        # -------------------------------------------------
        # Authenticate
        # -------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # -------------------------------------------------
        # Authentication failed
        # -------------------------------------------------

        if user is None:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "accounts/login.html"
            )

        # =================================================
        # BLOCK ADMIN / STAFF FROM CUSTOMER LOGIN
        # =================================================

        if (
            user.is_staff
            or user.is_superuser
        ):

            messages.error(
                request,
                "Administrator accounts cannot use Customer Login. "
                "Please use Admin Dashboard Login."
            )

            return render(
                request,
                "accounts/login.html"
            )

        # =================================================
        # GET CUSTOMER PROFILE
        # =================================================

        try:

            customer = user.customer_profile

        except Customer.DoesNotExist:

            messages.error(
                request,
                "Customer profile not found. "
                "Please contact the administrator."
            )

            return render(
                request,
                "accounts/login.html"
            )

        # =================================================
        # CUSTOMER LOGIN
        # =================================================
        #
        # IMPORTANT:
        # Customer model does NOT have a role field.
        #
        # Therefore we do NOT use:
        #
        #     customer.role
        #
        # Admin accounts are already separated using:
        #
        #     user.is_staff
        #     user.is_superuser
        #
        # =================================================

        login(
            request,
            user
        )

        messages.success(
            request,
            f"Welcome back, "
            f"{user.first_name or user.username}!"
        )

        # -------------------------------------------------
        # Redirect to requested page
        # -------------------------------------------------

        next_url = request.GET.get(
            "next"
        )

        if next_url:

            return redirect(
                next_url
            )

        # -------------------------------------------------
        # Default customer destination
        # -------------------------------------------------

        return redirect(
            "home"
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(
        request,
        "accounts/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url="login")
def logout_view(request):

    # -----------------------------------------------------
    # Check account type before logout
    # -----------------------------------------------------

    is_admin = (
        request.user.is_staff
        or request.user.is_superuser
    )

    # -----------------------------------------------------
    # Logout
    # -----------------------------------------------------

    logout(
        request
    )

    messages.success(
        request,
        "You have been logged out successfully."
    )

    # -----------------------------------------------------
    # Admin -> Dashboard Login
    # Customer -> Customer Login
    # -----------------------------------------------------

    if is_admin:

        return redirect(
            "dashboard_login"
        )

    return redirect(
        "login"
    )


# =========================================================
# PROFILE
# =========================================================

@login_required(login_url="login")
def profile_view(request):

    # -----------------------------------------------------
    # Admin / Staff should use dashboard
    # -----------------------------------------------------

    if (
        request.user.is_staff
        or request.user.is_superuser
    ):

        return redirect(
            "dashboard"
        )

    # -----------------------------------------------------
    # Get customer profile
    # or create one if missing
    # -----------------------------------------------------

    customer, created = (
        Customer.objects.get_or_create(
            user=request.user
        )
    )

    # -----------------------------------------------------
    # Render profile
    # -----------------------------------------------------

    return render(
        request,
        "accounts/profile.html",
        {
            "customer": customer
        }
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@login_required(login_url="login")
def edit_profile_view(request):

    # -----------------------------------------------------
    # Admin / Staff should use dashboard
    # -----------------------------------------------------

    if (
        request.user.is_staff
        or request.user.is_superuser
    ):

        return redirect(
            "dashboard"
        )

    # -----------------------------------------------------
    # Get customer profile
    # -----------------------------------------------------

    customer, created = (
        Customer.objects.get_or_create(
            user=request.user
        )
    )

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # User information form
        # -------------------------------------------------

        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )

        # -------------------------------------------------
        # Customer profile form
        # -------------------------------------------------

        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=customer
        )

        # -------------------------------------------------
        # Validate both forms
        # -------------------------------------------------

        if (
            user_form.is_valid()
            and profile_form.is_valid()
        ):

            # ---------------------------------------------
            # Save User information
            # ---------------------------------------------

            user_form.save()

            # ---------------------------------------------
            # Save Customer information
            # ---------------------------------------------

            profile_form.save()

            # ---------------------------------------------
            # Success message
            # ---------------------------------------------

            messages.success(
                request,
                "Profile updated successfully."
            )

            # ---------------------------------------------
            # Redirect to profile
            # ---------------------------------------------

            return redirect(
                "profile"
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    else:

        user_form = UserUpdateForm(
            instance=request.user
        )

        profile_form = ProfileUpdateForm(
            instance=customer
        )

    # =====================================================
    # RENDER EDIT PROFILE
    # =====================================================

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        }
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@login_required(login_url="login")
def change_password_view(request):

    # -----------------------------------------------------
    # Admin / Staff should use dashboard
    # -----------------------------------------------------

    if (
        request.user.is_staff
        or request.user.is_superuser
    ):

        return redirect(
            "dashboard"
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        if form.is_valid():

            # ---------------------------------------------
            # Save password
            # ---------------------------------------------

            user = form.save()

            # ---------------------------------------------
            # Keep user logged in
            # ---------------------------------------------

            update_session_auth_hash(
                request,
                user
            )

            # ---------------------------------------------
            # Success message
            # ---------------------------------------------

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect(
                "profile"
            )

    # =====================================================
    # GET
    # =====================================================

    else:

        form = PasswordChangeForm(
            request.user
        )

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )