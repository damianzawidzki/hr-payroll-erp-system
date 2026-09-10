"""
Shift views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employee
from .forms import BulkShiftForm, ShiftForm
from .models import Shift


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def get_logged_employee(user):
    """
    Return employee record linked with the logged-in user.
    """

    return Employee.objects.filter(user=user).first()


def user_can_manage_shifts(user):
    """
    Allow Admin, HR and Manager users to manage shifts.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR", "MANAGER"]


def get_shift_employee_queryset(user):
    """
    Return employees available for shift management.
    """

    role = get_user_role(user)

    if user.is_superuser or role in ["ADMIN", "HR"]:
        return Employee.objects.select_related("department", "manager").all()

    if role == "MANAGER":
        manager_employee = get_logged_employee(user)

        if manager_employee:
            return Employee.objects.select_related("department", "manager").filter(
                Q(manager=manager_employee) | Q(id=manager_employee.id)
            )

    return Employee.objects.none()


@login_required
def shift_list(request):
    """
    Display shift records.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to access shifts.")
        return redirect("role_redirect")

    search_query = request.GET.get("search", "")
    shift_type_filter = request.GET.get("shift_type", "")
    status_filter = request.GET.get("status", "")

    visible_employees = get_shift_employee_queryset(request.user)

    shifts = Shift.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        employee__in=visible_employees,
    )

    if search_query:
        shifts = shifts.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    if shift_type_filter:
        shifts = shifts.filter(shift_type=shift_type_filter)

    if status_filter:
        shifts = shifts.filter(status=status_filter)

    context = {
        "shifts": shifts.order_by("-shift_date", "start_time"),
        "search_query": search_query,
        "shift_type_filter": shift_type_filter,
        "status_filter": status_filter,
        "shift_type_choices": Shift.SHIFT_TYPE_CHOICES,
        "status_choices": Shift.STATUS_CHOICES,
    }

    return render(request, "shifts/shift_list.html", context)


@login_required
def shift_calendar(request):
    """
    Display monthly shift calendar.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to access shifts.")
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

    visible_employees = get_shift_employee_queryset(request.user)

    employees = visible_employees.order_by("first_name", "last_name")

    shifts = Shift.objects.filter(
        employee__in=employees,
        shift_date__year=selected_year,
        shift_date__month=selected_month,
    ).select_related("employee")

    shift_map = {}

    for shift in shifts:
        key = (shift.employee_id, shift.shift_date)
        shift_map.setdefault(key, []).append(shift)

    calendar_rows = []

    for employee in employees:
        cells = []

        for day in calendar_days:
            cells.append(
                {
                    "date": day["date"],
                    "is_weekend": day["is_weekend"],
                    "is_today": day["is_today"],
                    "shifts": shift_map.get((employee.id, day["date"]), []),
                }
            )

        calendar_rows.append(
            {
                "employee": employee,
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

    return render(request, "shifts/shift_calendar.html", context)


@login_required
def shift_create(request):
    """
    Create a single shift.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to create shifts.")
        return redirect("role_redirect")

    employee_queryset = get_shift_employee_queryset(request.user)

    if request.method == "POST":
        form = ShiftForm(request.POST)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Shift created.")
            return redirect("shift_list")
    else:
        form = ShiftForm()
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "page_title": "Add Shift",
        "button_text": "Create Shift",
    }

    return render(request, "shifts/shift_form.html", context)


@login_required
def bulk_shift_create(request):
    """
    Create shifts for multiple employees and multiple days.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to create shifts.")
        return redirect("role_redirect")

    employee_queryset = get_shift_employee_queryset(request.user)

    if request.method == "POST":
        form = BulkShiftForm(
            request.POST,
            employee_queryset=employee_queryset,
        )

        if form.is_valid():
            employees = form.cleaned_data["employees"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            weekdays = [int(day) for day in form.cleaned_data["weekdays"]]
            shift_type = form.cleaned_data["shift_type"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]
            location = form.cleaned_data["location"]
            status = form.cleaned_data["status"]
            notes = form.cleaned_data["notes"]
            overwrite_existing = form.cleaned_data["overwrite_existing"]

            current_date = start_date
            created_count = 0
            updated_count = 0
            skipped_count = 0

            while current_date <= end_date:
                if current_date.weekday() in weekdays:
                    for employee in employees:
                        if overwrite_existing:
                            shift, created = Shift.objects.update_or_create(
                                employee=employee,
                                shift_date=current_date,
                                defaults={
                                    "shift_type": shift_type,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "location": location,
                                    "status": status,
                                    "notes": notes,
                                },
                            )

                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                        else:
                            shift, created = Shift.objects.get_or_create(
                                employee=employee,
                                shift_date=current_date,
                                defaults={
                                    "shift_type": shift_type,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "location": location,
                                    "status": status,
                                    "notes": notes,
                                },
                            )

                            if created:
                                created_count += 1
                            else:
                                skipped_count += 1

                current_date += timedelta(days=1)

            messages.success(
                request,
                f"Bulk shifts completed. Created: {created_count}, updated: {updated_count}, skipped: {skipped_count}.",
            )

            return redirect("shift_calendar")
    else:
        form = BulkShiftForm(employee_queryset=employee_queryset)

    context = {
        "form": form,
        "page_title": "Bulk Add Shifts",
        "button_text": "Create Shifts",
    }

    return render(request, "shifts/bulk_shift_form.html", context)


@login_required
def shift_update(request, pk):
    """
    Update a shift.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to update shifts.")
        return redirect("role_redirect")

    employee_queryset = get_shift_employee_queryset(request.user)

    shift = get_object_or_404(
        Shift,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Shift updated.")
            return redirect("shift_list")
    else:
        form = ShiftForm(instance=shift)
        form.fields["employee"].queryset = employee_queryset

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
    Delete a shift.
    """

    if not user_can_manage_shifts(request.user):
        messages.error(request, "You do not have permission to delete shifts.")
        return redirect("role_redirect")

    employee_queryset = get_shift_employee_queryset(request.user)

    shift = get_object_or_404(
        Shift,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        shift.delete()
        messages.success(request, "Shift deleted.")
        return redirect("shift_list")

    context = {
        "shift": shift,
    }

    return render(request, "shifts/shift_confirm_delete.html", context)