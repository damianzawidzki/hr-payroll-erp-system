"""
Payroll views for HRHub Pro.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PayslipForm
from .models import Payslip


def user_can_manage_payroll(user):
    """
    Check whether the logged-in user can manage payroll.
    """

    if user.is_superuser or user.is_staff:
        return True

    profile = getattr(user, "profile", None)

    if profile and profile.role in ["ADMIN", "MANAGER"]:
        return True

    return False


@login_required
def payslip_list(request):
    """
    Display payslips for HR users.
    """

    if not user_can_manage_payroll(request.user):
        return redirect("employee_self_dashboard")

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    payslips = Payslip.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    if search_query:
        payslips = payslips.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    if status_filter:
        payslips = payslips.filter(status=status_filter)

    total_gross = payslips.aggregate(total=Sum("gross_pay"))["total"] or 0
    total_deductions = payslips.aggregate(total=Sum("deductions"))["total"] or 0
    total_net = payslips.aggregate(total=Sum("net_pay"))["total"] or 0

    context = {
        "payslips": payslips.order_by("-pay_period_end"),
        "search_query": search_query,
        "status_filter": status_filter,
        "total_gross": total_gross,
        "total_deductions": total_deductions,
        "total_net": total_net,
    }

    return render(request, "payroll/payslip_list.html", context)


@login_required
def payslip_create(request):
    """
    Create a payslip.
    """

    if not user_can_manage_payroll(request.user):
        return redirect("employee_self_dashboard")

    if request.method == "POST":
        form = PayslipForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Payslip created.")
            return redirect("payslip_list")
    else:
        form = PayslipForm()

    context = {
        "form": form,
        "page_title": "Add Payslip",
        "button_text": "Create Payslip",
    }

    return render(request, "payroll/payslip_form.html", context)


@login_required
def payslip_update(request, pk):
    """
    Update a payslip.
    """

    if not user_can_manage_payroll(request.user):
        return redirect("employee_self_dashboard")

    payslip = get_object_or_404(Payslip, pk=pk)

    if request.method == "POST":
        form = PayslipForm(request.POST, instance=payslip)

        if form.is_valid():
            form.save()
            messages.success(request, "Payslip updated.")
            return redirect("payslip_list")
    else:
        form = PayslipForm(instance=payslip)

    context = {
        "form": form,
        "payslip": payslip,
        "page_title": "Edit Payslip",
        "button_text": "Save Changes",
    }

    return render(request, "payroll/payslip_form.html", context)


@login_required
def payslip_delete(request, pk):
    """
    Delete a payslip.
    """

    if not user_can_manage_payroll(request.user):
        return redirect("employee_self_dashboard")

    payslip = get_object_or_404(Payslip, pk=pk)

    if request.method == "POST":
        payslip.delete()
        messages.success(request, "Payslip deleted.")
        return redirect("payslip_list")

    context = {
        "payslip": payslip,
    }

    return render(request, "payroll/payslip_confirm_delete.html", context)