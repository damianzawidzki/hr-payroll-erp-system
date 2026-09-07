"""
Main URL configuration for HRHub Pro.

This file connects the main project routes:
- Home redirect
- Django Admin
- Login
- Logout
- Dashboard
- Departments
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path


def home_redirect(request):
    """
    Redirect the root URL to the dashboard.

    If the user is not logged in, Django will redirect them to the login page
    because the dashboard view requires authentication.
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
    path("departments/", include("departments.urls")),
]