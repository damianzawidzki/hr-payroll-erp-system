"""
Employee views for HRHub Pro.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import can_manage_employees, can_view_employees

from .forms import EmployeeForm
from .models import Employee


def get_employee_queryset():
    """
    Return employees with managers at the top, then the rest alphabetically.
    """

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


@login_required
def employee_list(request):
    """
    Display employee records.
    """

    if not can_view_employees(request.user):
        messages.error(request, "You do not have permission to access employees.")
        return redirect("role_redirect")

    search_query = request.GET.get("search", "")

    employees = get_employee_queryset()

    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(employee_number__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(job_title__icontains=search_query)
        )

    context = {
        "employees": employees,
        "search_query": search_query,
        "can_edit_employees": can_manage_employees(request.user),
    }

    return render(request, "employees/employee_list.html", context)


@login_required
def employee_detail(request, pk):
    """
    Display employee details.
    """

    if not can_view_employees(request.user):
        messages.error(request, "You do not have permission to access employee details.")
        return redirect("role_redirect")

    employee = get_object_or_404(
        Employee.objects.select_related(
            "department",
            "manager",
            "user",
            "user__profile",
        ),
        pk=pk,
    )

    context = {
        "employee": employee,
        "can_edit_employees": can_manage_employees(request.user),
    }

    return render(request, "employees/employee_detail.html", context)


@login_required
def employee_create(request):
    """
    Create an employee record.
    """

    if not can_manage_employees(request.user):
        messages.error(request, "You do not have permission to create employees.")
        return redirect("employee_list")

    if request.method == "POST":
        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee created.")
            return redirect("employee_list")
    else:
        form = EmployeeForm()

    context = {
        "form": form,
        "page_title": "Add Employee",
        "button_text": "Create Employee",
    }

    return render(request, "employees/employee_form.html", context)


@login_required
def employee_update(request, pk):
    """
    Update an employee record.
    """

    if not can_manage_employees(request.user):
        messages.error(request, "You do not have permission to update employees.")
        return redirect("employee_list")

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated.")
            return redirect("employee_list")
    else:
        form = EmployeeForm(instance=employee)

    context = {
        "form": form,
        "employee": employee,
        "page_title": "Edit Employee",
        "button_text": "Save Changes",
    }

    return render(request, "employees/employee_form.html", context)


@login_required
def employee_delete(request, pk):
    """
    Delete an employee record.
    """

    if not can_manage_employees(request.user):
        messages.error(request, "You do not have permission to delete employees.")
        return redirect("employee_list")

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted.")
        return redirect("employee_list")

    context = {
        "employee": employee,
    }

    return render(request, "employees/employee_confirm_delete.html", context)