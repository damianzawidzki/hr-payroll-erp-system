"""
Shift admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """
    Admin configuration for employee shifts.
    """

    list_display = (
        "employee",
        "shift_type",
        "shift_date",
        "start_time",
        "end_time",
        "status",
    )

    list_filter = (
        "shift_type",
        "status",
        "shift_date",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
        "location",
    )

    ordering = (
        "shift_date",
        "start_time",
    )