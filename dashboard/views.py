"""
Dashboard views for HRFlow Pro.

This file contains the main dashboard page logic.
The dashboard show important statistic and give the user 
a professional first screen after login.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from emplyees.models import Employee
from departments.models import Department

@login_required
def dashboard_view(request):
    """
    Display the main HR dashboard page.

    For now, the dashboard users real real data from Employees and Departments.
    Payroll, leave and attendance statistic will be connected later
      when I build those modules.
    """

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status = 'ACTIVE').count()
    total_departments = Department.objects.count()
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_departments': total_departments,
    
        #These are placeholeders for modules that I will build next.
        'pending_leave_requests': 0,
        'present_today': 0,
        'monthly_payroll_cost': 0,
    }

    return render(request, 'dashboard/dashboard.html', context)



 
