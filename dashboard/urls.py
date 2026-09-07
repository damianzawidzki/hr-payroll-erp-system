"""
Dashboard URL configuration for HRHub Pro.

This file defines the URL route for the dashboard page.
"""

from django.urls import path

from .views import dashboard_view


urlpatterns = [
    path("", dashboard_view, name="dashboard"),
]