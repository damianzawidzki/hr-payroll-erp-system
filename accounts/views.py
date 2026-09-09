"""
Account views for HRHub Pro.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def role_redirect_view(request):
    """
    Redirect users after login based on account type and role.
    """

    if request.user.is_superuser:
        return redirect("dashboard")

    if request.user.is_staff:
        return redirect("dashboard")

    profile = getattr(request.user, "profile", None)

    if profile:
        if profile.role in ["ADMIN", "MANAGER"]:
            return redirect("dashboard")

        if profile.role == "EMPLOYEE":
            return redirect("employee_self_dashboard")

    return redirect("employee_self_dashboard")