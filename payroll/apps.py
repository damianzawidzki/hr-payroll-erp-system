"""
Payroll app configuration for HRHub Pro.
"""

from django.apps import AppConfig


class PayrollConfig(AppConfig):
    """
    Configuration for the payroll app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "payroll"