"""
Attendance admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for attendance records.
    """

    list_display = (
        "employee",
        "date",
        "clock_in",
        "clock_out",
        "break_minutes",
        "total_hours",
        "status",
    )

    list_filter = (
        "status",
        "date",
        "employee__department",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
    )

    ordering = (
        "-date",
        "employee__first_name",
        "employee__last_name",
    )

    readonly_fields = (
        "total_hours",
        "created_at",
        "updated_at",
    )