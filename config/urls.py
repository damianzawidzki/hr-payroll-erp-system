"""
Main URL configuration for HRFlow Pro.

This file connects all main project routes:
-Django Admin
-Login and Logout
-Dashboard module
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    """
    Redirect the root URL to the dashboard.

    If the user is not logged in, Django will redirect them to the login page
    because the dashboard view requires authentication.
    """
    return redirect('dashboard')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
        ),

        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path('dashboard/', include('dashboard.urls')),
]
