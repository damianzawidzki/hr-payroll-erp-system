"""
Leave management URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.leave_request_list, name="leave_request_list"),
    path("calendar/", views.leave_calendar, name="leave_calendar"),
    path("add/", views.leave_request_create, name="leave_request_create"),
    path("<int:pk>/edit/", views.leave_request_update, name="leave_request_update"),
    path("<int:pk>/delete/", views.leave_request_delete, name="leave_request_delete"),
    path("<int:pk>/approve/", views.leave_request_approve, name="leave_request_approve"),
    path("<int:pk>/reject/", views.leave_request_reject, name="leave_request_reject"),
]