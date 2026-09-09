"""
Employee portal views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from employees.models import Employee
from leave_management.forms import EmployeeLeaveRequestForm
from leave_management.models import LeaveRequest
from payroll.models import Payslip
from shifts.models import Shift
from attendance.models import Attendance

from .forms import EmployeeProfileForm


HOLIDAY_ENTITLEMENT_DAYS = Decimal("33")


def get_logged_employee(user):
    """
    Return the employee profile connected with the logged-in user.
    """

    return Employee.objects.filter(user=user).first()


def calculate_holiday_summary(employee):
    """
    Calculate annual leave, pending leave and sickness summary.
    """

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

    approved_sick_leave = LeaveRequest.objects.filter(
        employee=employee,
        leave_type="SICK",
        status="APPROVED",
    )

    used_days = sum(
        (leave_request.total_days for leave_request in approved_annual_leave),
        Decimal("0"),
    )

    pending_days = sum(
        (leave_request.total_days for leave_request in pending_annual_leave),
        Decimal("0"),
    )

    sick_days = sum(
        (leave_request.total_days for leave_request in approved_sick_leave),
        Decimal("0"),
    )

    remaining_days = HOLIDAY_ENTITLEMENT_DAYS - used_days - pending_days

    if remaining_days < Decimal("0"):
        remaining_days = Decimal("0")

    if HOLIDAY_ENTITLEMENT_DAYS > Decimal("0"):
        used_percent = (used_days / HOLIDAY_ENTITLEMENT_DAYS) * Decimal("100")
        pending_percent = (pending_days / HOLIDAY_ENTITLEMENT_DAYS) * Decimal("100")
    else:
        used_percent = Decimal("0")
        pending_percent = Decimal("0")

    if used_percent > Decimal("100"):
        used_percent = Decimal("100")

    pending_end_percent = used_percent + pending_percent

    if pending_end_percent > Decimal("100"):
        pending_end_percent = Decimal("100")

    return {
        "holiday_entitlement": HOLIDAY_ENTITLEMENT_DAYS,
        "used_days": used_days,
        "pending_days": pending_days,
        "remaining_days": remaining_days,
        "used_percent": round(used_percent, 2),
        "pending_end_percent": round(pending_end_percent, 2),
        "sick_records": approved_sick_leave.count(),
        "sick_days": sick_days,
    }


@login_required
def employee_self_dashboard(request):
    """
    Display the employee self-service dashboard.
    """

    employee = get_logged_employee(request.user)

    holiday_summary = {
        "holiday_entitlement": HOLIDAY_ENTITLEMENT_DAYS,
        "used_days": Decimal("0"),
        "pending_days": Decimal("0"),
        "remaining_days": HOLIDAY_ENTITLEMENT_DAYS,
        "used_percent": Decimal("0"),
        "pending_end_percent": Decimal("0"),
        "sick_records": 0,
        "sick_days": Decimal("0"),
    }

    latest_leave_requests = []
    upcoming_shifts = []

    if employee:
        holiday_summary = calculate_holiday_summary(employee)

        latest_leave_requests = LeaveRequest.objects.filter(
            employee=employee,
        ).order_by("-created_at")[:5]

        upcoming_shifts = Shift.objects.filter(
            employee=employee,
            shift_date__gte=timezone.localdate(),
        ).exclude(
            status="CANCELLED",
        ).order_by("shift_date", "start_time")[:5]

    context = {
        "employee": employee,
        "holiday_summary": holiday_summary,
        "latest_leave_requests": latest_leave_requests,
        "upcoming_shifts": upcoming_shifts,
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
        return redirect("employee_self_dashboard")

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
        context = {
            "employee": employee,
            "leave_requests": [],
            "holiday_summary": {
                "holiday_entitlement": HOLIDAY_ENTITLEMENT_DAYS,
                "used_days": Decimal("0"),
                "pending_days": Decimal("0"),
                "remaining_days": HOLIDAY_ENTITLEMENT_DAYS,
                "used_percent": Decimal("0"),
                "pending_end_percent": Decimal("0"),
                "sick_records": 0,
                "sick_days": Decimal("0"),
            },
        }

        return render(request, "employee_portal/my_leave_list.html", context)

    leave_requests = LeaveRequest.objects.filter(
        employee=employee,
    ).order_by("-created_at")

    holiday_summary = calculate_holiday_summary(employee)

    context = {
        "employee": employee,
        "leave_requests": leave_requests,
        "holiday_summary": holiday_summary,
    }

    return render(request, "employee_portal/my_leave_list.html", context)


@login_required
def my_leave_create(request):
    """
    Allow the logged-in employee to submit a leave request.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("employee_self_dashboard")

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
        "form": form,
        "employee": employee,
    }

    return render(request, "employee_portal/my_leave_form.html", context)


@login_required
def my_shifts(request):
    """
    Display the logged-in employee monthly shift calendar.
    """

    employee = get_logged_employee(request.user)

    today = timezone.localdate()

    selected_year = int(request.GET.get("year", today.year))
    selected_month = int(request.GET.get("month", today.month))

    if selected_month < 1:
        selected_month = 12
        selected_year -= 1

    if selected_month > 12:
        selected_month = 1
        selected_year += 1

    first_day = date(selected_year, selected_month, 1)
    last_day_number = monthrange(selected_year, selected_month)[1]
    last_day = date(selected_year, selected_month, last_day_number)

    previous_month = selected_month - 1
    previous_year = selected_year

    if previous_month < 1:
        previous_month = 12
        previous_year -= 1

    next_month = selected_month + 1
    next_year = selected_year

    if next_month > 12:
        next_month = 1
        next_year += 1

    calendar_days = []

    for day_number in range(1, last_day_number + 1):
        current_date = date(selected_year, selected_month, day_number)

        calendar_days.append(
            {
                "date": current_date,
                "day_number": day_number,
                "day_name": current_date.strftime("%a"),
                "is_weekend": current_date.weekday() >= 5,
                "is_today": current_date == today,
            }
        )

    shifts = []

    if employee:
        shifts = Shift.objects.filter(
            employee=employee,
            shift_date__gte=first_day,
            shift_date__lte=last_day,
        ).exclude(
            status="CANCELLED",
        ).order_by("shift_date", "start_time")

    calendar_cells = []

    for day_data in calendar_days:
        day_shifts = [
            shift for shift in shifts if shift.shift_date == day_data["date"]
        ]

        calendar_cells.append(
            {
                "date": day_data["date"],
                "day_number": day_data["day_number"],
                "day_name": day_data["day_name"],
                "is_weekend": day_data["is_weekend"],
                "is_today": day_data["is_today"],
                "shifts": day_shifts,
            }
        )

    context = {
        "employee": employee,
        "calendar_cells": calendar_cells,
        "month_name": month_name[selected_month],
        "selected_month": selected_month,
        "selected_year": selected_year,
        "previous_month": previous_month,
        "previous_year": previous_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, "employee_portal/my_shifts.html", context)


@login_required
def my_shift_team(request):
    """
    Display colleagues from the logged-in employee shifts and their leave status.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("employee_self_dashboard")

    today = timezone.localdate()

    selected_year = int(request.GET.get("year", today.year))
    selected_month = int(request.GET.get("month", today.month))

    if selected_month < 1:
        selected_month = 12
        selected_year -= 1

    if selected_month > 12:
        selected_month = 1
        selected_year += 1

    first_day = date(selected_year, selected_month, 1)
    last_day_number = monthrange(selected_year, selected_month)[1]
    last_day = date(selected_year, selected_month, last_day_number)

    previous_month = selected_month - 1
    previous_year = selected_year

    if previous_month < 1:
        previous_month = 12
        previous_year -= 1

    next_month = selected_month + 1
    next_year = selected_year

    if next_month > 12:
        next_month = 1
        next_year += 1

    my_month_shifts = Shift.objects.filter(
        employee=employee,
        shift_date__gte=first_day,
        shift_date__lte=last_day,
    ).exclude(
        status="CANCELLED",
    ).order_by("shift_date", "start_time")

    team_rows = []

    for my_shift in my_month_shifts:
        colleagues = Shift.objects.select_related(
            "employee",
            "employee__department",
        ).filter(
            shift_date=my_shift.shift_date,
            shift_type=my_shift.shift_type,
        ).exclude(
            employee=employee,
        ).exclude(
            status="CANCELLED",
        )

        if my_shift.location:
            colleagues = colleagues.filter(
                Q(location=my_shift.location) | Q(location__isnull=True) | Q(location="")
            )

        colleague_items = []

        for colleague_shift in colleagues:
            colleague_leave = LeaveRequest.objects.filter(
                employee=colleague_shift.employee,
                start_date__lte=my_shift.shift_date,
                end_date__gte=my_shift.shift_date,
            ).exclude(
                status="CANCELLED",
            ).order_by("-created_at").first()

            colleague_items.append(
                {
                    "shift": colleague_shift,
                    "leave": colleague_leave,
                }
            )

        department_leave = LeaveRequest.objects.select_related(
            "employee",
            "employee__department",
        ).filter(
            start_date__lte=my_shift.shift_date,
            end_date__gte=my_shift.shift_date,
        ).exclude(
            employee=employee,
        ).exclude(
            status="CANCELLED",
        )

        if employee.department:
            department_leave = department_leave.filter(
                employee__department=employee.department,
            )

        team_rows.append(
            {
                "my_shift": my_shift,
                "colleague_items": colleague_items,
                "department_leave": department_leave,
            }
        )

    context = {
        "employee": employee,
        "team_rows": team_rows,
        "month_name": month_name[selected_month],
        "selected_month": selected_month,
        "selected_year": selected_year,
        "previous_month": previous_month,
        "previous_year": previous_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, "employee_portal/my_shift_team.html", context)

@login_required
def my_attendance(request):
    """
    Display attendance records for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("employee_self_dashboard")

    attendance_records = Attendance.objects.filter(
        employee=employee,
    ).order_by("-date")

    present_count = attendance_records.filter(status="PRESENT").count()
    late_count = attendance_records.filter(status="LATE").count()
    absent_count = attendance_records.filter(status="ABSENT").count()

    context = {
        "employee": employee,
        "attendance_records": attendance_records,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
    }

    return render(request, "employee_portal/my_attendance.html", context)

@login_required
def my_payslips(request):
    """
    Display payslips for the logged-in employee.
    """

    employee = get_logged_employee(request.user)

    if not employee:
        messages.error(request, "Employee profile is not linked.")
        return redirect("employee_self_dashboard")

    payslips = Payslip.objects.filter(
        employee=employee,
    ).exclude(
        status="DRAFT",
    ).order_by("-pay_period_end")

    total_gross = sum((payslip.gross_pay for payslip in payslips), 0)
    total_deductions = sum((payslip.deductions for payslip in payslips), 0)
    total_net = sum((payslip.net_pay for payslip in payslips), 0)

    context = {
        "employee": employee,
        "payslips": payslips,
        "total_gross": total_gross,
        "total_deductions": total_deductions,
        "total_net": total_net,
    }

    return render(request, "employee_portal/my_payslips.html", context)