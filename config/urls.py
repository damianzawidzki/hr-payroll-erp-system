"""
Main URL configuration for HRHub Pro.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path


def home_redirect(request):
    """
    Redirect the root URL to the correct area.
    """

    if request.user.is_authenticated:
        return redirect("role_redirect")

    return redirect("login")


urlpatterns = [
    path("", home_redirect, name="home"),
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("dashboard/", include("dashboard.urls")),
    path("employees/", include("employees.urls")),
    path("departments/", include("departments.urls")),
    path("attendance/", include("attendance.urls")),
    path("leave-requests/", include("leave_management.urls")),
    path("shifts/", include("shifts.urls")),
    path("my-dashboard/", include("employee_portal.urls")),
]