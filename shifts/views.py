"""
Shift views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ShiftForm
from .models import Shift


def user_can_manage_shifts(user):
    """
    Check whether the logged-in user can manage employee shifts.
    """

    if user.is_superuser or user.is_staff:
        return True

    profile = getattr(user, "profile", None)

    if profile and profile.role in ["ADMIN", "MANAGER"]:
        return True

    return False


@login_required
def shift_list(request):
    """
    Display employee shifts for HR users.
    """

    if not user_can_manage_shifts(request.user):
        return redirect("employee_self_dashboard")

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    shifts = Shift.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    if search_query:
        shifts = shifts.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    if status_filter:
        shifts = shifts.filter(status=status_filter)

    context = {
        "shifts": shifts.order_by("shift_date", "start_time"),
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(request, "shifts/shift_list.html", context)


@login_required
def shift_create(request):
    """
    Create an employee shift.
    """

    if not user_can_manage_shifts(request.user):
        return redirect("employee_self_dashboard")

    if request.method == "POST":
        form = ShiftForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Shift created.")
            return redirect("shift_list")
    else:
        form = ShiftForm()

    context = {
        "form": form,
        "page_title": "Add Shift",
        "button_text": "Create Shift",
    }

    return render(request, "shifts/shift_form.html", context)


@login_required
def shift_update(request, pk):
    """
    Update an employee shift.
    """

    if not user_can_manage_shifts(request.user):
        return redirect("employee_self_dashboard")

    shift = get_object_or_404(Shift, pk=pk)

    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift)

        if form.is_valid():
            form.save()
            messages.success(request, "Shift updated.")
            return redirect("shift_list")
    else:
        form = ShiftForm(instance=shift)

    context = {
        "form": form,
        "shift": shift,
        "page_title": "Edit Shift",
        "button_text": "Save Changes",
    }

    return render(request, "shifts/shift_form.html", context)


@login_required
def shift_delete(request, pk):
    """
    Delete an employee shift.
    """

    if not user_can_manage_shifts(request.user):
        return redirect("employee_self_dashboard")

    shift = get_object_or_404(Shift, pk=pk)

    if request.method == "POST":
        shift.delete()
        messages.success(request, "Shift deleted.")
        return redirect("shift_list")

    context = {
        "shift": shift,
    }

    return render(request, "shifts/shift_confirm_delete.html", context)


@login_required
def shift_calendar(request):
    """
    Display monthly shift calendar for HR users.
    """

    if not user_can_manage_shifts(request.user):
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

    shifts = Shift.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        shift_date__gte=first_day,
        shift_date__lte=last_day,
    ).exclude(
        status="CANCELLED",
    ).order_by(
        "employee__first_name",
        "shift_date",
        "start_time",
    )

    employees = []

    for shift in shifts:
        if shift.employee not in employees:
            employees.append(shift.employee)

    calendar_rows = []

    for employee in employees:
        employee_shifts = [
            shift for shift in shifts if shift.employee_id == employee.id
        ]

        cells = []

        for day_data in calendar_days:
            day_shifts = [
                shift for shift in employee_shifts if shift.shift_date == day_data["date"]
            ]

            cells.append(
                {
                    "date": day_data["date"],
                    "is_weekend": day_data["is_weekend"],
                    "is_today": day_data["is_today"],
                    "shifts": day_shifts,
                }
            )

        calendar_rows.append(
            {
                "employee": employee,
                "cells": cells,
            }
        )

    context = {
        "calendar_days": calendar_days,
        "calendar_rows": calendar_rows,
        "month_name": month_name[selected_month],
        "selected_month": selected_month,
        "selected_year": selected_year,
        "previous_month": previous_month,
        "previous_year": previous_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, "shifts/shift_calendar.html", context)