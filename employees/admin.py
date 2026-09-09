"""
Employee admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin configuration for employee records.
    """

    list_display = (
        "employee_number",
        "full_name",
        "job_title",
        "department",
        "manager",
        "employment_type",
        "status",
        "hire_date",
    )

    list_filter = (
        "department",
        "manager",
        "employment_type",
        "status",
    )

    search_fields = (
        "employee_number",
        "first_name",
        "last_name",
        "email",
        "job_title",
    )

    ordering = (
        "first_name",
        "last_name",
    )