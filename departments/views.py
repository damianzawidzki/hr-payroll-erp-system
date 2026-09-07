"""
Department views for HRHub Pro.

This file contains the page logic for managing company departments.
The module works like a real HR system because users can list, create,
view, update and delete departments.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DepartmentForm
from .models import Department


@login_required
def department_list(request):
    """
    Display all departments in the system.

    The page includes a search field that can search by department name
    or manager name.
    """

    search_query = request.GET.get("search", "")

    departments = Department.objects.all()

    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query)
            | Q(manager_name__icontains=search_query)
        )

    context = {
        "departments": departments,
        "search_query": search_query,
    }

    return render(request, "departments/department_list.html", context)


@login_required
def department_detail(request, pk):
    """
    Display detailed information about one department.
    """

    department = get_object_or_404(Department, pk=pk)

    context = {
        "department": department,
    }

    return render(request, "departments/department_detail.html", context)


@login_required
def department_create(request):
    """
    Create a new department.
    """

    if request.method == "POST":
        form = DepartmentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect("department_list")
    else:
        form = DepartmentForm()

    context = {
        "form": form,
        "page_title": "Add Department",
        "button_text": "Create Department",
    }

    return render(request, "departments/department_form.html", context)


@login_required
def department_update(request, pk):
    """
    Update an existing department.
    """

    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)

        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect("department_detail", pk=department.pk)
    else:
        form = DepartmentForm(instance=department)

    context = {
        "form": form,
        "department": department,
        "page_title": "Edit Department",
        "button_text": "Save Changes",
    }

    return render(request, "departments/department_form.html", context)


@login_required
def department_delete(request, pk):
    """
    Delete a department after confirmation.
    """

    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect("department_list")

    context = {
        "department": department,
    }

    return render(request, "departments/department_confirm_delete.html", context)