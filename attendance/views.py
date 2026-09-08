"""
Attendance views for HRHub Pro.

This file handles attendance record management.
Users can view, filter, create, update and delete attendance records.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AttendanceForm
from .models import Attendance


@login_required
def attendance_list(request):
    """
    Display attendance records with search and status filtering.
    """

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    attendance_records = Attendance.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    if search_query:
        attendance_records = attendance_records.filter(
            Q(employee__employee_number__icontains=search_query)
            | Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__email__icontains=search_query)
        )

    if status_filter:
        attendance_records = attendance_records.filter(status=status_filter)

    context = {
        "attendance_records": attendance_records,
        "status_choices": Attendance.STATUS_CHOICES,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(request, "attendance/attendance_list.html", context)


@login_required
def attendance_create(request):
    """
    Create a new attendance record.
    """

    if request.method == "POST":
        form = AttendanceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record created successfully.")
            return redirect("attendance_list")
    else:
        form = AttendanceForm()

    context = {
        "form": form,
        "page_title": "Add Attendance",
        "button_text": "Create Record",
    }

    return render(request, "attendance/attendance_form.html", context)


@login_required
def attendance_update(request, pk):
    """
    Update an existing attendance record.
    """

    attendance_record = get_object_or_404(Attendance, pk=pk)

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance_record)

        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record updated successfully.")
            return redirect("attendance_list")
    else:
        form = AttendanceForm(instance=attendance_record)

    context = {
        "form": form,
        "attendance_record": attendance_record,
        "page_title": "Edit Attendance",
        "button_text": "Save Changes",
    }

    return render(request, "attendance/attendance_form.html", context)


@login_required
def attendance_delete(request, pk):
    """
    Delete an attendance record.
    """

    attendance_record = get_object_or_404(Attendance, pk=pk)

    if request.method == "POST":
        attendance_record.delete()
        messages.success(request, "Attendance record deleted successfully.")
        return redirect("attendance_list")

    context = {
        "attendance_record": attendance_record,
    }

    return render(request, "attendance/attendance_confirm_delete.html", context)