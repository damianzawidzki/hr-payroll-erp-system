"""
Payroll admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import Payslip


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    """
    Admin configuration for payslip records.
    """

    list_display = (
        "employee",
        "pay_period_start",
        "pay_period_end",
        "payment_date",
        "gross_pay",
        "deductions",
        "net_pay",
        "status",
    )

    list_filter = (
        "status",
        "payment_date",
        "pay_period_end",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
    )

    ordering = (
        "-pay_period_end",
    )