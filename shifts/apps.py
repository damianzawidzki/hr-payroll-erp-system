"""
Shift app configuration for HRHub Pro.
"""

from django.apps import AppConfig


class ShiftsConfig(AppConfig):
    """
    Configuration for the shifts app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "shifts"