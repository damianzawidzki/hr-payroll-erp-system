"""
Role dashboard views for HRHub Pro.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from attendance.models import Attendance
from employees.models import Employee
from leave_management.models import LeaveRequest
from payroll.models import Payslip
from shifts.models import Shift


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def user_can_view_manager_dashboard(user):
    """
    Check manager dashboard access.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR", "MANAGER"]


def user_can_view_hr_dashboard(user):
    """
    Check HR dashboard access.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR"]


@login_required
def manager_dashboard(request):
    """
    Display the manager dashboard.
    """

    if not user_can_view_manager_dashboard(request.user):
        return redirect("role_redirect")

    today = timezone.localdate()

    current_manager_employee = Employee.objects.filter(
        user=request.user,
    ).first()

    team_members = Employee.objects.none()

    if current_manager_employee:
        team_members = Employee.objects.filter(
            manager=current_manager_employee,
        )

    if request.user.is_superuser or get_user_role(request.user) in ["ADMIN", "HR"]:
        team_members = Employee.objects.all()

    pending_leave_requests = LeaveRequest.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        employee__in=team_members,
        status="PENDING",
    ).order_by("start_date")[:8]

    upcoming_shifts = Shift.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        employee__in=team_members,
        shift_date__gte=today,
    ).exclude(
        status="CANCELLED",
    ).order_by("shift_date", "start_time")[:8]

    attendance_today = Attendance.objects.filter(
        employee__in=team_members,
        date=today,
    ).count()

    absent_today = Attendance.objects.filter(
        employee__in=team_members,
        date=today,
        status="ABSENT",
    ).count()

    context = {
        "today": today,
        "team_members": team_members,
        "team_count": team_members.count(),
        "pending_leave_count": pending_leave_requests.count(),
        "upcoming_shifts_count": upcoming_shifts.count(),
        "attendance_today": attendance_today,
        "absent_today": absent_today,
        "pending_leave_requests": pending_leave_requests,
        "upcoming_shifts": upcoming_shifts,
    }

    return render(request, "role_dashboards/manager_dashboard.html", context)


@login_required
def hr_dashboard(request):
    """
    Display the HR dashboard.
    """

    if not user_can_view_hr_dashboard(request.user):
        return redirect("role_redirect")

    today = timezone.localdate()

    total_employees = Employee.objects.count()

    attendance_today = Attendance.objects.filter(
        date=today,
    ).count()

    absent_today = Attendance.objects.filter(
        date=today,
        status="ABSENT",
    ).count()

    pending_leave = LeaveRequest.objects.filter(
        status="PENDING",
    ).count()

    payslip_count = Payslip.objects.exclude(
        status="DRAFT",
    ).count()

    payroll_total_net = Payslip.objects.exclude(
        status="DRAFT",
    ).aggregate(
        total=Sum("net_pay"),
    )["total"] or 0

    context = {
        "today": today,
        "total_employees": total_employees,
        "attendance_today": attendance_today,
        "absent_today": absent_today,
        "pending_leave": pending_leave,
        "payslip_count": payslip_count,
        "payroll_total_net": payroll_total_net,
    }

    return render(request, "role_dashboards/hr_dashboard.html", context)