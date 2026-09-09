"""
Role dashboard URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("hr/", views.hr_dashboard, name="hr_dashboard"),
]