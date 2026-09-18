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
    # If already logged in, go to home
    # -----------------------------------------------------

    if request.user.is_authenticated:

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
# LOGIN
# =========================================================

def login_view(request):

    # -----------------------------------------------------
    # Already logged in
    # -----------------------------------------------------

    if request.user.is_authenticated:

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
        # Authenticate
        # -------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )


        # -------------------------------------------------
        # Login successful
        # -------------------------------------------------

        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, "
                f"{user.first_name or user.username}!"
            )


            # ---------------------------------------------
            # Redirect to requested page if available
            # ---------------------------------------------

            next_url = request.GET.get(
                "next"
            )

            if next_url:

                return redirect(
                    next_url
                )


            return redirect(
                "home"
            )


        # -------------------------------------------------
        # Login failed
        # -------------------------------------------------

        messages.error(
            request,
            "Invalid username or password."
        )


    # -----------------------------------------------------
    # Render login page
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

    logout(
        request
    )

    messages.success(
        request,
        "You have been logged out successfully."
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
    # Get existing Customer profile
    # or create one if it doesn't exist
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
            # Return to profile
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
            # Save new password
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