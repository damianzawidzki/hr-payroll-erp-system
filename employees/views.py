"""
Employee views for HRHub Pro.

This file contains the page logic for managing employee records.
Users can list, search, filter, create, view, update and delete employees.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from departments.models import Department

from .forms import EmployeeForm
from .models import Employee


@login_required
def employee_list(request):
    """
    Display employee records with search and filters.
    """

    search_query = request.GET.get("search", "")
    department_filter = request.GET.get("department", "")
    status_filter = request.GET.get("status", "")

    employees = Employee.objects.select_related("department", "user").all()
    departments = Department.objects.filter(is_active=True)

    if search_query:
        employees = employees.filter(
            Q(employee_number__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(job_title__icontains=search_query)
        )

    if department_filter:
        employees = employees.filter(department_id=department_filter)

    if status_filter:
        employees = employees.filter(status=status_filter)

    context = {
        "employees": employees,
        "departments": departments,
        "status_choices": Employee.STATUS_CHOICES,
        "search_query": search_query,
        "department_filter": department_filter,
        "status_filter": status_filter,
    }

    return render(request, "employees/employee_list.html", context)


@login_required
def employee_detail(request, pk):
    """
    Display one employee record.
    """

    employee = get_object_or_404(
        Employee.objects.select_related("department", "user"),
        pk=pk,
    )

    context = {
        "employee": employee,
    }

    return render(request, "employees/employee_detail.html", context)


@login_required
def employee_create(request):
    """
    Create a new employee record.
    """

    if request.method == "POST":
        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee created successfully.")
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
    Update an existing employee record.
    """

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect("employee_detail", pk=employee.pk)
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

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect("employee_list")

    context = {
        "employee": employee,
    }

    return render(request, "employees/employee_confirm_delete.html", context)