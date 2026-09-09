"""
Template context processors for HRHub Pro.
"""


def user_role_context(request):
    """
    Add the logged-in user role to all templates.
    """

    user_role = None
    is_admin_user = False
    is_hr_user = False
    is_manager_user = False
    is_employee_user = False

    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)

        if request.user.is_superuser:
            user_role = "ADMIN"
            is_admin_user = True
        elif profile:
            user_role = profile.role
            is_admin_user = profile.role == "ADMIN"
            is_hr_user = profile.role == "HR"
            is_manager_user = profile.role == "MANAGER"
            is_employee_user = profile.role == "EMPLOYEE"

    return {
        "user_role": user_role,
        "is_admin_user": is_admin_user,
        "is_hr_user": is_hr_user,
        "is_manager_user": is_manager_user,
        "is_employee_user": is_employee_user,
    }