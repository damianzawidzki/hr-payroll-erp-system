"""
Leave management views for HRHub Pro.
"""

from calendar import month_name, monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee

from .forms import LeaveRequestForm
from .models import LeaveRequest


def user_can_manage_leave(user):
    """
    Check whether the logged-in user can manage leave requests.
    """

    if user.is_superuser or user.is_staff:
        return True

    profile = getattr(user, "profile", None)

    if profile and profile.role in ["ADMIN", "MANAGER"]:
        return True

    return False


@login_required
def leave_request_list(request):
    """
    Display leave requests for HR users.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    status_filter = request.GET.get("status", "")
    search_query = request.GET.get("search", "")

    leave_requests = LeaveRequest.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)

    if search_query:
        leave_requests = leave_requests.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    pending_count = LeaveRequest.objects.filter(status="PENDING").count()
    approved_count = LeaveRequest.objects.filter(status="APPROVED").count()
    rejected_count = LeaveRequest.objects.filter(status="REJECTED").count()

    context = {
        "leave_requests": leave_requests.order_by("-created_at"),
        "status_filter": status_filter,
        "search_query": search_query,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }

    return render(request, "leave_management/leave_request_list.html", context)


@login_required
def leave_calendar(request):
    """
    Display a monthly leave calendar for managers and administrators.
    """

    if not user_can_manage_leave(request.user):
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

    employees = Employee.objects.select_related("department").all().order_by(
        "first_name",
        "last_name",
    )

    leave_requests = LeaveRequest.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        start_date__lte=last_day,
        end_date__gte=first_day,
    ).exclude(
        status="CANCELLED",
    ).order_by(
        "employee__first_name",
        "start_date",
    )

    calendar_rows = []

    for employee in employees:
        employee_leave_requests = [
            leave_request
            for leave_request in leave_requests
            if leave_request.employee_id == employee.id
        ]

        cells = []

        for day_data in calendar_days:
            current_date = day_data["date"]

            leave_items = [
                leave_request
                for leave_request in employee_leave_requests
                if leave_request.start_date <= current_date <= leave_request.end_date
            ]

            cells.append(
                {
                    "date": current_date,
                    "day_number": day_data["day_number"],
                    "is_weekend": day_data["is_weekend"],
                    "is_today": day_data["is_today"],
                    "leave_items": leave_items,
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

    return render(request, "leave_management/leave_calendar.html", context)


@login_required
def leave_request_create(request):
    """
    Create a leave request from HR panel.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Leave request created.")
            return redirect("leave_request_list")
    else:
        form = LeaveRequestForm()

    context = {
        "form": form,
        "page_title": "Add Leave Request",
        "button_text": "Create Request",
    }

    return render(request, "leave_management/leave_request_form.html", context)


@login_required
def leave_request_update(request, pk):
    """
    Update a leave request from HR panel.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave_request)

        if form.is_valid():
            form.save()
            messages.success(request, "Leave request updated.")
            return redirect("leave_request_list")
    else:
        form = LeaveRequestForm(instance=leave_request)

    context = {
        "form": form,
        "leave_request": leave_request,
        "page_title": "Edit Leave Request",
        "button_text": "Save Changes",
    }

    return render(request, "leave_management/leave_request_form.html", context)


@login_required
def leave_request_delete(request, pk):
    """
    Delete a leave request from HR panel.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == "POST":
        leave_request.delete()
        messages.success(request, "Leave request deleted.")
        return redirect("leave_request_list")

    context = {
        "leave_request": leave_request,
    }

    return render(request, "leave_management/leave_request_confirm_delete.html", context)


@login_required
def leave_request_approve(request, pk):
    """
    Approve a pending leave request.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == "POST":
        leave_request.status = "APPROVED"
        leave_request.manager_comment = request.POST.get("manager_comment", "")
        leave_request.save()

        messages.success(request, "Leave request approved.")

    return redirect("leave_request_list")


@login_required
def leave_request_reject(request, pk):
    """
    Reject a pending leave request.
    """

    if not user_can_manage_leave(request.user):
        return redirect("employee_self_dashboard")

    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == "POST":
        leave_request.status = "REJECTED"
        leave_request.manager_comment = request.POST.get("manager_comment", "")
        leave_request.save()

        messages.success(request, "Leave request rejected.")

    return redirect("leave_request_list")