"""
URL routes for the dashboard module.

The dashboard is the main landing page after login.
"""

from django.urls import path
from . import views

urlpattens = [
    path('' , views.dashboard_view, name='dashboard'),
]