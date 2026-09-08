"""
Main URL configuration for HRHub Pro.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path


def home_redirect(request):
    """
    Redirect the root URL to the dashboard.
    """

    return redirect("dashboard")


urlpatterns = [
    path("", home_redirect, name="home"),

    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
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
]