"""
Dashboard views for HRHub Pro.

This file contains the main dashboard page logic.
The dashboard displays basic HR statistics from the database.

At this stage, the dashboard uses real data from:
- Employees
- Departments

Other values such as leave requests, attendance and payroll are temporary
placeholders. They will be replaced with real module data later.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from departments.models import Department
from employees.models import Employee


@login_required
def dashboard_view(request):
    """
    Display the main dashboard page.

    This view counts employees and departments from the database.
    It gives the system a professional starting dashboard after login.
    """

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status="ACTIVE").count()
    total_departments = Department.objects.count()

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_departments": total_departments,

        # Temporary dashboard values.
        # These will be connected to real modules later.
        "pending_leave_requests": 0,
        "present_today": 0,
        "monthly_payroll_cost": 0,
    }

    return render(request, "dashboard/dashboard.html", context)