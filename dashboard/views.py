"""
Dashboard views for HRHub Pro.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from attendance.models import Attendance
from departments.models import Department
from employees.models import Employee


@login_required
def dashboard_view(request):
    """
    Display the main dashboard page.
    """

    today = timezone.localdate()

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status="ACTIVE").count()
    total_departments = Department.objects.count()
    present_today = Attendance.objects.filter(date=today, status="PRESENT").count()

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_departments": total_departments,
        "pending_leave_requests": 0,
        "present_today": present_today,
        "monthly_payroll_cost": 0,
    }

    return render(request, "dashboard/dashboard.html", context)