"""
Leave management admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for leave requests.
    """

    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "total_days",
        "status",
        "created_at",
    )

    list_filter = (
        "leave_type",
        "status",
        "start_date",
        "created_at",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
        "employee__email",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )