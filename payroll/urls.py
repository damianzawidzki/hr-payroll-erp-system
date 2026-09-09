"""
Payroll URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.payslip_list, name="payslip_list"),
    path("add/", views.payslip_create, name="payslip_create"),
    path("<int:pk>/edit/", views.payslip_update, name="payslip_update"),
    path("<int:pk>/delete/", views.payslip_delete, name="payslip_delete"),
]