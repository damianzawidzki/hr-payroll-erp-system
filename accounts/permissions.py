"""
Permission helpers for HRHub Pro.
"""


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    if not user.is_authenticated:
        return None

    if user.is_superuser:
        return "ADMIN"

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def is_admin_user(user):
    """
    Check if the user has Admin access.
    """

    return user.is_authenticated and (
        user.is_superuser or get_user_role(user) == "ADMIN"
    )


def is_hr_user(user):
    """
    Check if the user has HR access.
    """

    return user.is_authenticated and get_user_role(user) == "HR"


def is_manager_user(user):
    """
    Check if the user has Manager access.
    """

    return user.is_authenticated and get_user_role(user) == "MANAGER"


def is_employee_user(user):
    """
    Check if the user has Employee access.
    """

    return user.is_authenticated and get_user_role(user) == "EMPLOYEE"


def can_access_admin_dashboard(user):
    """
    Only Admin users should access the main dashboard.
    """

    return is_admin_user(user)


def can_access_hr_area(user):
    """
    Admin and HR can access HR operations.
    """

    return is_admin_user(user) or is_hr_user(user)


def can_access_manager_area(user):
    """
    Admin, HR and Manager can access team operations.
    """

    return is_admin_user(user) or is_hr_user(user) or is_manager_user(user)


def can_manage_employees(user):
    """
    Admin and HR can create, update and delete employees.
    """

    return is_admin_user(user) or is_hr_user(user)


def can_view_employees(user):
    """
    Admin, HR and Manager can view employee records.
    """

    return is_admin_user(user) or is_hr_user(user) or is_manager_user(user)


def can_manage_payroll(user):
    """
    Admin and HR can manage payroll.
    Managers and employees cannot create payslips.
    """

    return is_admin_user(user) or is_hr_user(user)