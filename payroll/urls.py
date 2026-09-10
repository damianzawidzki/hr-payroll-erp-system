"""
Payroll URL routes for HRHub Pro.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.payslip_list, name="payslip_list"),
    path("add/", views.payslip_create, name="payslip_create"),
    path("generate/", views.generate_weekly_payslips, name="generate_weekly_payslips"),
    path("<int:pk>/edit/", views.payslip_update, name="payslip_update"),
    path("<int:pk>/delete/", views.payslip_delete, name="payslip_delete"),
    path("<int:pk>/preview/", views.payslip_pdf_preview, name="payslip_pdf_preview"),
    path("<int:pk>/download/", views.payslip_pdf_download, name="payslip_pdf_download"),
]