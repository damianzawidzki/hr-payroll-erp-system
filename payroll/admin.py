"""
Payroll admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import Payslip


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    """
    Admin configuration for weekly payslip records.
    """

    list_display = (
        "employee",
        "week_start",
        "week_end",
        "payment_date",
        "hours_worked",
        "overtime_hours",
        "gross_pay",
        "deductions",
        "net_pay",
        "status",
    )

    list_filter = (
        "status",
        "payment_date",
        "week_start",
        "week_end",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
    )

    ordering = (
        "-week_start",
    )

    readonly_fields = (
        "gross_pay",
        "net_pay",
        "created_at",
        "updated_at",
    )