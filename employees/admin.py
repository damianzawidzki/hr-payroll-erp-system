from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    This admin configuration creates a professional employee management view.

    It allows the HR team to search, filter and manage employees directly
    from the Django Admin panel.
    """

    list_display = (
        'employee_number',
        'first_name',
        'last_name',
        'email',
        'job_title',
        'department',
        'employment_type',
        'salary',
        'status',
        'hire_date',
    )

    list_filter = (
        'department',
        'employment_type',
        'status',
        'hire_date',
    )

    search_fields = (
        'employee_number',
        'first_name',
        'last_name',
        'email',
        'job_title',
    )

    ordering = (
        'last_name',
        'first_name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            'Personal Information',
            {
                'fields': (
                    'user',
                    'employee_number',
                    'first_name',
                    'last_name',
                    'email',
                    'phone',
                    'address',
                    'date_of_birth',
                )
            }
        ),
        (
            'Employment Information',
            {
                'fields': (
                    'job_title',
                    'department',
                    'employment_type',
                    'hire_date',
                    'salary',
                    'status',
                )
            }
        ),
        (
            'Emergency Contact',
            {
                'fields': (
                    'emergency_contact_name',
                    'emergency_contact_phone',
                )
            }
        ),
        (
            'System Information',
            {
                'fields': (
                    'notes',
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )