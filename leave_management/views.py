"""
Leave management views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employee
from shifts.models import Shift

from .forms import LeaveDecisionForm, LeaveRequestForm
from .models import LeaveRequest


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def user_can_manage_leave(user):
    """
    Allow Admin, HR and Manager users to access team leave management.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR", "MANAGER"]


def get_visible_employees_for_leave(user):
    """
    Return all employees for Admin, HR and Manager users.
    Managers are placed at the top, then the rest are sorted alphabetically.
    """

    role = get_user_role(user)

    if user.is_superuser or role in ["ADMIN", "HR", "MANAGER"]:
        return Employee.objects.select_related(
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

    return Employee.objects.none()


@login_required
def leave_request_list(request):
    """
    Display leave requests for Admin, HR and Manager users.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to access leave records.")
        return redirect("role_redirect")

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    leave_type_filter = request.GET.get("leave_type", "")

    visible_employees = get_visible_employees_for_leave(request.user)

    leave_requests = LeaveRequest.objects.select_related(
        "employee",
        "employee__department",
        "employee__manager",
    ).filter(
        employee__in=visible_employees,
    )

    if search_query:
        leave_requests = leave_requests.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)

    if leave_type_filter:
        leave_requests = leave_requests.filter(leave_type=leave_type_filter)

    context = {
        "leave_requests": leave_requests.order_by("-start_date"),
        "search_query": search_query,
        "status_filter": status_filter,
        "leave_type_filter": leave_type_filter,
        "status_choices": LeaveRequest.STATUS_CHOICES,
        "leave_type_choices": LeaveRequest.LEAVE_TYPE_CHOICES,
    }

    return render(request, "leave_management/leave_request_list.html", context)


@login_required
def leave_calendar(request):
    """
    Display one team calendar with shifts and leave records.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to access team calendar.")
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

    employees = get_visible_employees_for_leave(request.user)

    month_start = date(selected_year, selected_month, 1)
    month_end = date(selected_year, selected_month, days_in_month)

    leave_requests = LeaveRequest.objects.select_related(
        "employee",
    ).filter(
        employee__in=employees,
        start_date__lte=month_end,
        end_date__gte=month_start,
    ).exclude(
        status="CANCELLED",
    )

    shifts = Shift.objects.select_related(
        "employee",
    ).filter(
        employee__in=employees,
        shift_date__gte=month_start,
        shift_date__lte=month_end,
    ).exclude(
        status="CANCELLED",
    )

    leave_map = {}
    shift_map = {}

    for leave_request in leave_requests:
        current_day = max(leave_request.start_date, month_start)
        final_day = min(leave_request.end_date, month_end)

        while current_day <= final_day:
            key = (leave_request.employee_id, current_day)
            leave_map.setdefault(key, []).append(leave_request)
            current_day += timedelta(days=1)

    for shift in shifts:
        key = (shift.employee_id, shift.shift_date)
        shift_map.setdefault(key, []).append(shift)

    calendar_rows = []

    for employee in employees:
        employee_role = None

        if employee.user:
            profile = getattr(employee.user, "profile", None)

            if profile:
                employee_role = profile.role

        cells = []

        for day in calendar_days:
            key = (employee.id, day["date"])

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
                "employee": employee,
                "employee_role": employee_role,
                "is_manager": employee_role == "MANAGER",
                "cells": cells,
            }
        )

    context = {
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

    return render(request, "leave_management/leave_calendar.html", context)


@login_required
def leave_request_create(request):
    """
    Create a leave request from the management panel.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to create leave records.")
        return redirect("role_redirect")

    employee_queryset = get_visible_employees_for_leave(request.user)

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Leave record created.")
            return redirect("leave_request_list")
    else:
        form = LeaveRequestForm()
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "page_title": "Add Leave",
        "button_text": "Create Leave",
    }

    return render(request, "leave_management/leave_request_form.html", context)


@login_required
def leave_request_update(request, pk):
    """
    Update a leave request.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to update leave records.")
        return redirect("role_redirect")

    employee_queryset = get_visible_employees_for_leave(request.user)

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave_request)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Leave record updated.")
            return redirect("leave_request_list")
    else:
        form = LeaveRequestForm(instance=leave_request)
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "leave_request": leave_request,
        "page_title": "Edit Leave",
        "button_text": "Save Changes",
    }

    return render(request, "leave_management/leave_request_form.html", context)


@login_required
def leave_request_delete(request, pk):
    """
    Delete a leave request.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to delete leave records.")
        return redirect("role_redirect")

    employee_queryset = get_visible_employees_for_leave(request.user)

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        leave_request.delete()
        messages.success(request, "Leave record deleted.")
        return redirect("leave_request_list")

    context = {
        "leave_request": leave_request,
    }

    return render(request, "leave_management/leave_request_confirm_delete.html", context)


@login_required
def leave_request_approve(request, pk):
    """
    Approve a leave request.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to approve leave.")
        return redirect("role_redirect")

    employee_queryset = get_visible_employees_for_leave(request.user)

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = LeaveDecisionForm(request.POST, instance=leave_request)

        if form.is_valid():
            decision = form.save(commit=False)
            decision.status = "APPROVED"
            decision.save()

            messages.success(request, "Leave request approved.")
            return redirect("leave_request_list")
    else:
        form = LeaveDecisionForm(instance=leave_request)

    context = {
        "form": form,
        "leave_request": leave_request,
        "page_title": "Approve Leave",
        "button_text": "Approve Leave",
    }

    return render(request, "leave_management/leave_decision_form.html", context)


@login_required
def leave_request_reject(request, pk):
    """
    Reject a leave request.
    """

    if not user_can_manage_leave(request.user):
        messages.error(request, "You do not have permission to reject leave.")
        return redirect("role_redirect")

    employee_queryset = get_visible_employees_for_leave(request.user)

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = LeaveDecisionForm(request.POST, instance=leave_request)

        if form.is_valid():
            decision = form.save(commit=False)
            decision.status = "REJECTED"
            decision.save()

            messages.success(request, "Leave request rejected.")
            return redirect("leave_request_list")
    else:
        form = LeaveDecisionForm(instance=leave_request)

    context = {
        "form": form,
        "leave_request": leave_request,
        "page_title": "Reject Leave",
        "button_text": "Reject Leave",
    }

    return render(request, "leave_management/leave_decision_form.html", context)