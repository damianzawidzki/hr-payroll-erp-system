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
        "check_in_time",
        "check_out_time",
        "status",
        "total_hours",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
        "employee__email",
    )

    ordering = (
        "-date",
        "employee__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )