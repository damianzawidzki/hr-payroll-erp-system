"""
Employee URL routes for HRHub Pro.

This file connects all employee pages:
- employee list
- add employee
- employee details
- edit employee
- delete employee
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.employee_create, name="employee_create"),
    path("<int:pk>/", views.employee_detail, name="employee_detail"),
    path("<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),
]