"""
Attendance URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.attendance_list, name="attendance_list"),
    path("add/", views.attendance_create, name="attendance_create"),
    path("generate/", views.generate_attendance_from_shifts, name="generate_attendance"),
    path("<int:pk>/edit/", views.attendance_update, name="attendance_update"),
    path("<int:pk>/delete/", views.attendance_delete, name="attendance_delete"),
]