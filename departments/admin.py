from django.contrib import admin
from .models import Department

# Register your models here.
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    This admin configuration makes department management easier
    inside the Django Admin panel. It allows for searching, filtering and ordering of departments.
    """
    list_display = (
        'name',
        'manager_name',
        'is_active',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'manager_name',
    )

    ordering = (
        'name',
    )