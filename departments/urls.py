"""
Department URL routes for HRHub Pro.

This file contains all routes for the Departments module:
- department list
- create department
- department details
- edit department
- delete department
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.department_list, name="department_list"),
    path("add/", views.department_create, name="department_create"),
    path("<int:pk>/", views.department_detail, name="department_detail"),
    path("<int:pk>/edit/", views.department_update, name="department_update"),
    path("<int:pk>/delete/", views.department_delete, name="department_delete"),
]