"""
Attendance views for HRHub Pro.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Sum, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee
from shifts.models import Shift

from .forms import AttendanceForm, GenerateAttendanceForm
from .models import Attendance


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def user_can_manage_attendance(user):
    """
    Allow Admin, HR and Manager users to manage attendance.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR", "MANAGER"]


def get_attendance_employee_queryset(user):
    """
    Return employees available for attendance management.
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
def attendance_list(request):
    """
    Display attendance records.
    """

    if not user_can_manage_attendance(request.user):
        messages.error(request, "You do not have permission to access attendance.")
        return redirect("role_redirect")

    today = timezone.localdate()

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    date_filter = request.GET.get("date", "")

    visible_employees = get_attendance_employee_queryset(request.user)

    attendance_records = Attendance.objects.select_related(
        "employee",
        "employee__department",
    ).filter(
        employee__in=visible_employees,
    )

    if search_query:
        attendance_records = attendance_records.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    if status_filter:
        attendance_records = attendance_records.filter(status=status_filter)

    if date_filter:
        attendance_records = attendance_records.filter(date=date_filter)

    total_hours = attendance_records.aggregate(
        total=Sum("total_hours"),
    )["total"] or 0

    present_today = Attendance.objects.filter(
        employee__in=visible_employees,
        date=today,
        status="PRESENT",
    ).count()

    late_today = Attendance.objects.filter(
        employee__in=visible_employees,
        date=today,
        status="LATE",
    ).count()

    absent_today = Attendance.objects.filter(
        employee__in=visible_employees,
        date=today,
        status="ABSENT",
    ).count()

    context = {
        "attendance_records": attendance_records.order_by("-date", "employee__first_name"),
        "search_query": search_query,
        "status_filter": status_filter,
        "date_filter": date_filter,
        "status_choices": Attendance.STATUS_CHOICES,
        "total_hours": total_hours,
        "present_today": present_today,
        "late_today": late_today,
        "absent_today": absent_today,
    }

    return render(request, "attendance/attendance_list.html", context)


@login_required
def attendance_create(request):
    """
    Create an attendance record.
    """

    if not user_can_manage_attendance(request.user):
        messages.error(request, "You do not have permission to create attendance.")
        return redirect("role_redirect")

    employee_queryset = get_attendance_employee_queryset(request.user)

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record created.")
            return redirect("attendance_list")
    else:
        form = AttendanceForm()
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "page_title": "Add Attendance",
        "button_text": "Create Attendance",
    }

    return render(request, "attendance/attendance_form.html", context)


@login_required
def generate_attendance_from_shifts(request):
    """
    Generate attendance records from scheduled shifts.
    """

    if not user_can_manage_attendance(request.user):
        messages.error(request, "You do not have permission to generate attendance.")
        return redirect("role_redirect")

    employee_queryset = get_attendance_employee_queryset(request.user)

    if request.method == "POST":
        form = GenerateAttendanceForm(
            request.POST,
            employee_queryset=employee_queryset,
        )

        if form.is_valid():
            employees = form.cleaned_data["employees"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            status = form.cleaned_data["status"]
            break_minutes = form.cleaned_data["break_minutes"]
            overwrite_existing = form.cleaned_data["overwrite_existing"]
            notes = form.cleaned_data["notes"]

            shifts = Shift.objects.filter(
                employee__in=employees,
                shift_date__gte=start_date,
                shift_date__lte=end_date,
            ).exclude(
                status="CANCELLED",
            ).select_related(
                "employee",
            ).order_by(
                "shift_date",
                "employee__first_name",
                "employee__last_name",
            )

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for shift in shifts:
                defaults = {
                    "clock_in": shift.start_time,
                    "clock_out": shift.end_time,
                    "break_minutes": break_minutes,
                    "status": status,
                    "notes": notes,
                }

                if overwrite_existing:
                    attendance, created = Attendance.objects.update_or_create(
                        employee=shift.employee,
                        date=shift.shift_date,
                        defaults=defaults,
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    attendance, created = Attendance.objects.get_or_create(
                        employee=shift.employee,
                        date=shift.shift_date,
                        defaults=defaults,
                    )

                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1

            messages.success(
                request,
                f"Attendance generated. Created: {created_count}, updated: {updated_count}, skipped: {skipped_count}.",
            )

            return redirect("attendance_list")
    else:
        form = GenerateAttendanceForm(employee_queryset=employee_queryset)

    context = {
        "form": form,
        "page_title": "Generate Attendance",
        "button_text": "Generate Attendance",
    }

    return render(request, "attendance/generate_attendance.html", context)


@login_required
def attendance_update(request, pk):
    """
    Update an attendance record.
    """

    if not user_can_manage_attendance(request.user):
        messages.error(request, "You do not have permission to update attendance.")
        return redirect("role_redirect")

    employee_queryset = get_attendance_employee_queryset(request.user)

    attendance = get_object_or_404(
        Attendance,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record updated.")
            return redirect("attendance_list")
    else:
        form = AttendanceForm(instance=attendance)
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "attendance": attendance,
        "page_title": "Edit Attendance",
        "button_text": "Save Changes",
    }

    return render(request, "attendance/attendance_form.html", context)


@login_required
def attendance_delete(request, pk):
    """
    Delete an attendance record.
    """

    if not user_can_manage_attendance(request.user):
        messages.error(request, "You do not have permission to delete attendance.")
        return redirect("role_redirect")

    employee_queryset = get_attendance_employee_queryset(request.user)

    attendance = get_object_or_404(
        Attendance,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        attendance.delete()
        messages.success(request, "Attendance record deleted.")
        return redirect("attendance_list")

    context = {
        "attendance": attendance,
    }

    return render(request, "attendance/attendance_confirm_delete.html", context)