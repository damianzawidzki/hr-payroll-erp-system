"""
Employee portal views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Sum, Value, When
from django.shortcuts import redirect, render
from django.utils import timezone

from attendance.models import Attendance
from employees.models import Employee
from leave_management.forms import EmployeeLeaveRequestForm
from leave_management.models import LeaveRequest
from payroll.models import Payslip
from shifts.models import Shift

from .forms import EmployeeProfileForm


def get_logged_employee(user):
    """
    Return employee record linked with the logged-in user.
    """

    return Employee.objects.filter(user=user).first()


def calculate_holiday_summary(employee):
    """
    Calculate annual leave summary for the employee dashboard.
    """

    annual_entitlement = 33

    approved_annual_leave = LeaveRequest.objects.filter(
        employee=employee,
        leave_type="ANNUAL",
        status="APPROVED",
    )

    pending_annual_leave = LeaveRequest.objects.filter(
        employee=employee,
        leave_type="ANNUAL",
        status="PENDING",
    )

    used_days = sum((leave.total_days for leave in approved_annual_leave), 0)
    pending_days = sum((leave.total_days for leave in pending_annual_leave), 0)

    remaining_days = annual_entitlement - used_days - pending_days

    if remaining_days < 0:
        remaining_days = 0

    used_percent = 0
    pending_percent = 0
    remaining_percent = 100

    if annual_entitlement > 0:
        used_percent = round((used_days / annual_entitlement) * 100, 2)
        pending_percent = round((pending_days / annual_entitlement) * 100, 2)
        remaining_percent = round((remaining_days / annual_entitlement) * 100, 2)

    return {
        "annual_entitlement": annual_entitlement,
        "used_days": used_days,
        "pending_days": pending_days,
        "remaining_days": remaining_days,
        "used_percent": used_percent,
        "pending_percent": pending_percent,
        "remaining_percent": remaining_percent,
    }


@login_required
def employee_self_dashboard(request):
    """
    Display dashboard for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    today = timezone.localdate()

    holiday_summary = calculate_holiday_summary(employee)

    upcoming_shifts = Shift.objects.filter(
        employee=employee,
        shift_date__gte=today,
    ).exclude(
        status="CANCELLED",
    ).order_by(
        "shift_date",
        "start_time",
    )[:5]

    pending_leave_requests = LeaveRequest.objects.filter(
        employee=employee,
        status="PENDING",
    ).order_by(
        "start_date",
    )[:5]

    recent_attendance = Attendance.objects.filter(
        employee=employee,
    ).order_by(
        "-date",
    )[:5]

    sick_records_count = LeaveRequest.objects.filter(
        employee=employee,
        leave_type="SICK",
    ).exclude(
        status="CANCELLED",
    ).count()

    sick_days = sum(
        (
            leave.total_days
            for leave in LeaveRequest.objects.filter(
                employee=employee,
                leave_type="SICK",
            ).exclude(
                status="CANCELLED",
            )
        ),
        0,
    )

    context = {
        "employee": employee,
        "today": today,
        "holiday_summary": holiday_summary,
        "upcoming_shifts": upcoming_shifts,
        "pending_leave_requests": pending_leave_requests,
        "recent_attendance": recent_attendance,
        "sick_records_count": sick_records_count,
        "sick_days": sick_days,
    }

    return render(request, "employee_portal/dashboard.html", context)


@login_required
def my_profile(request):
    """
    Display and update the logged-in employee profile.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    if request.method == "POST":
        form = EmployeeProfileForm(request.POST, instance=employee)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("my_profile")
    else:
        form = EmployeeProfileForm(instance=employee)

    context = {
        "employee": employee,
        "form": form,
    }

    return render(request, "employee_portal/my_profile.html", context)


@login_required
def my_leave_list(request):
    """
    Display leave requests for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    leave_requests = LeaveRequest.objects.filter(
        employee=employee,
    ).order_by(
        "-start_date",
    )

    holiday_summary = calculate_holiday_summary(employee)

    context = {
        "employee": employee,
        "leave_requests": leave_requests,
        "holiday_summary": holiday_summary,
    }

    return render(request, "employee_portal/my_leave.html", context)


@login_required
def my_leave_create(request):
    """
    Allow the logged-in employee to book leave.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    if request.method == "POST":
        form = EmployeeLeaveRequestForm(request.POST)

        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.status = "PENDING"
            leave_request.save()

            messages.success(request, "Leave request submitted.")
            return redirect("my_leave_list")
    else:
        form = EmployeeLeaveRequestForm()

    context = {
        "employee": employee,
        "form": form,
        "page_title": "Book Leave",
        "button_text": "Submit Request",
    }

    return render(request, "employee_portal/my_leave_form.html", context)


@login_required
def my_shifts(request):
    """
    Display monthly shifts for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    today = date.today()

    selected_month = int(request.GET.get("month", today.month))
    selected_year = int(request.GET.get("year", today.year))

    if selected_month == 1:
        previous_month = 12
        previous_year = selected_year - 1
    else:
        previous_month = selected_month - 1
        previous_year = selected_year

    if selected_month == 12:
        next_month = 1
        next_year = selected_year + 1
    else:
        next_month = selected_month + 1
        next_year = selected_year

    shifts = Shift.objects.filter(
        employee=employee,
        shift_date__year=selected_year,
        shift_date__month=selected_month,
    ).exclude(
        status="CANCELLED",
    ).order_by(
        "shift_date",
        "start_time",
    )

    context = {
        "employee": employee,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "month_name": month_name[selected_month],
        "previous_month": previous_month,
        "previous_year": previous_year,
        "next_month": next_month,
        "next_year": next_year,
        "shifts": shifts,
    }

    return render(request, "employee_portal/my_shifts.html", context)


@login_required
def my_shift_team(request):
    """
    Display a read-only team calendar for employees.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    today = date.today()

    selected_month = int(request.GET.get("month", today.month))
    selected_year = int(request.GET.get("year", today.year))

    if selected_month == 1:
        previous_month = 12
        previous_year = selected_year - 1
    else:
        previous_month = selected_month - 1
        previous_year = selected_year

    if selected_month == 12:
        next_month = 1
        next_year = selected_year + 1
    else:
        next_month = selected_month + 1
        next_year = selected_year

    days_in_month = monthrange(selected_year, selected_month)[1]

    calendar_days = []

    for day_number in range(1, days_in_month + 1):
        current_day = date(selected_year, selected_month, day_number)

        calendar_days.append(
            {
                "date": current_day,
                "day_number": day_number,
                "day_name": current_day.strftime("%a"),
                "is_weekend": current_day.weekday() >= 5,
                "is_today": current_day == today,
            }
        )

    employees = Employee.objects.select_related(
        "department",
        "manager",
        "user",
        "user__profile",
    ).annotate(
        role_order=Case(
            When(user__profile__role="MANAGER", then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by(
        "role_order",
        "first_name",
        "last_name",
    )

    month_start = date(selected_year, selected_month, 1)
    month_end = date(selected_year, selected_month, days_in_month)

    shifts = Shift.objects.select_related(
        "employee",
    ).filter(
        employee__in=employees,
        shift_date__gte=month_start,
        shift_date__lte=month_end,
    ).exclude(
        status="CANCELLED",
    )

    leave_requests = LeaveRequest.objects.select_related(
        "employee",
    ).filter(
        employee__in=employees,
        start_date__lte=month_end,
        end_date__gte=month_start,
    ).exclude(
        status="CANCELLED",
    )

    shift_map = {}
    leave_map = {}

    for shift in shifts:
        key = (shift.employee_id, shift.shift_date)
        shift_map.setdefault(key, []).append(shift)

    for leave_request in leave_requests:
        current_day = max(leave_request.start_date, month_start)
        final_day = min(leave_request.end_date, month_end)

        while current_day <= final_day:
            key = (leave_request.employee_id, current_day)
            leave_map.setdefault(key, []).append(leave_request)
            current_day += timedelta(days=1)

    calendar_rows = []

    for team_employee in employees:
        employee_role = None

        if team_employee.user:
            profile = getattr(team_employee.user, "profile", None)

            if profile:
                employee_role = profile.role

        cells = []

        for day in calendar_days:
            key = (team_employee.id, day["date"])

            cells.append(
                {
                    "date": day["date"],
                    "is_weekend": day["is_weekend"],
                    "is_today": day["is_today"],
                    "shifts": shift_map.get(key, []),
                    "leave_requests": leave_map.get(key, []),
                }
            )

        calendar_rows.append(
            {
                "employee": team_employee,
                "is_logged_employee": team_employee.id == employee.id,
                "is_manager": employee_role == "MANAGER",
                "cells": cells,
            }
        )

    context = {
        "employee": employee,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "month_name": month_name[selected_month],
        "previous_month": previous_month,
        "previous_year": previous_year,
        "next_month": next_month,
        "next_year": next_year,
        "calendar_days": calendar_days,
        "calendar_rows": calendar_rows,
    }

    return render(request, "employee_portal/my_team.html", context)


@login_required
def my_attendance(request):
    """
    Display attendance records for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    attendance_records = Attendance.objects.filter(
        employee=employee,
    ).order_by(
        "-date",
    )

    total_hours = attendance_records.aggregate(
        total=Sum("total_hours"),
    )["total"] or 0

    context = {
        "employee": employee,
        "attendance_records": attendance_records,
        "total_hours": total_hours,
    }

    return render(request, "employee_portal/my_attendance.html", context)


@login_required
def my_payslips(request):
    """
    Display issued weekly payslips for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("role_redirect")

    payslips = Payslip.objects.filter(
        employee=employee,
    ).exclude(
        status="DRAFT",
    ).order_by(
        "-week_start",
    )

    total_gross = payslips.aggregate(
        total=Sum("gross_pay"),
    )["total"] or 0

    total_paye_tax = payslips.aggregate(
        total=Sum("paye_tax"),
    )["total"] or 0

    total_national_insurance = payslips.aggregate(
        total=Sum("national_insurance"),
    )["total"] or 0

    total_other_deductions = payslips.aggregate(
        total=Sum("other_deductions"),
    )["total"] or 0

    total_deductions = payslips.aggregate(
        total=Sum("total_deductions"),
    )["total"] or 0

    total_net = payslips.aggregate(
        total=Sum("net_pay"),
    )["total"] or 0

    context = {
        "employee": employee,
        "payslips": payslips,
        "total_gross": total_gross,
        "total_paye_tax": total_paye_tax,
        "total_national_insurance": total_national_insurance,
        "total_other_deductions": total_other_deductions,
        "total_deductions": total_deductions,
        "total_net": total_net,
    }

    return render(request, "employee_portal/my_payslips.html", context)