"""
Account views for HRHub Pro.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def role_redirect_view(request):
    """
    Redirect users after login based on their assigned role.
    """

    if request.user.is_superuser:
        return redirect("dashboard")

    profile = getattr(request.user, "profile", None)

    if profile:
        if profile.role == "ADMIN":
            return redirect("dashboard")

        if profile.role == "HR":
            return redirect("hr_dashboard")

        if profile.role == "MANAGER":
            return redirect("manager_dashboard")

        if profile.role == "EMPLOYEE":
            return redirect("employee_self_dashboard")

    if request.user.is_staff:
        return redirect("dashboard")

    return redirect("employee_self_dashboard")