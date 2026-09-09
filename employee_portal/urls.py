"""
Employee portal URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.employee_self_dashboard, name="employee_self_dashboard"),
    path("profile/", views.my_profile, name="my_profile"),
    path("leave/", views.my_leave_list, name="my_leave_list"),
    path("leave/book/", views.my_leave_create, name="my_leave_create"),
    path("shifts/", views.my_shifts, name="my_shifts"),
    path("team/", views.my_shift_team, name="my_shift_team"),
    path("attendance/", views.my_attendance, name="my_attendance"),
    path("payslips/", views.my_payslips, name="my_payslips"),
]