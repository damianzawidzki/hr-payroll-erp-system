"""
Dashboard views for HRHub Pro.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.permissions import (
    can_access_admin_dashboard,
    is_hr_user,
    is_manager_user,
)
from attendance.models import Attendance
from employees.models import Employee
from leave_management.models import LeaveRequest
from payroll.models import Payslip
from shifts.models import Shift


@login_required
def dashboard_view(request):
    """
    Display the main Admin dashboard.
    """

    if not can_access_admin_dashboard(request.user):
        if is_hr_user(request.user):
            return redirect("hr_dashboard")

        if is_manager_user(request.user):
            return redirect("manager_dashboard")

        return redirect("employee_self_dashboard")

    today = timezone.localdate()

    total_employees = Employee.objects.count()

    active_employees = Employee.objects.filter(
        status="ACTIVE",
    ).count()

    pending_leave = LeaveRequest.objects.filter(
        status="PENDING",
    ).count()

    attendance_today = Attendance.objects.filter(
        date=today,
    ).count()

    absent_today = Attendance.objects.filter(
        date=today,
        status="ABSENT",
    ).count()

    upcoming_shifts = Shift.objects.filter(
        shift_date__gte=today,
    ).exclude(
        status="CANCELLED",
    ).order_by(
        "shift_date",
        "start_time",
    )[:8]

    recent_leave_requests = LeaveRequest.objects.select_related(
        "employee",
    ).order_by(
        "-start_date",
    )[:8]

    payroll_total_net = Payslip.objects.exclude(
        status="DRAFT",
    ).aggregate(
        total=Sum("net_pay"),
    )["total"] or 0

    context = {
        "today": today,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "pending_leave": pending_leave,
        "attendance_today": attendance_today,
        "absent_today": absent_today,
        "upcoming_shifts": upcoming_shifts,
        "recent_leave_requests": recent_leave_requests,
        "payroll_total_net": payroll_total_net,
    }

    return render(request, "dashboard/dashboard.html", context)