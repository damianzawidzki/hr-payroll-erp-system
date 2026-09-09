"""
Account admin configuration for HRHub Pro.
"""

from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for user profiles.
    """

    list_display = (
        "user",
        "role",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    ordering = (
        "user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )