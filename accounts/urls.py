from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # REGISTER
    # =====================================================

    path(
        "register/",
        views.register_view,
        name="register"
    ),


    # =====================================================
    # LOGIN
    # =====================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),


    # =====================================================
    # LOGOUT
    # =====================================================

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "profile/",
        views.profile_view,
        name="profile"
    ),


    # =====================================================
    # EDIT PROFILE
    # =====================================================

    path(
        "profile/edit/",
        views.edit_profile_view,
        name="profile_edit"
    ),


    # =====================================================
    # CHANGE PASSWORD
    # =====================================================

    path(
        "change-password/",
        views.change_password_view,
        name="change_password"
    ),

]