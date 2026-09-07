"""
Department forms for HRHub Pro.

This file contains forms used to create and update company departments.
Using Django ModelForm helps keep form validation clean and professional.
"""

from django import forms

from .models import Department


class DepartmentForm(forms.ModelForm):
    """
    Form used by admins or HR managers to create and update departments.
    """

    class Meta:
        model = Department

        fields = [
            "name",
            "manager_name",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department name",
                }
            ),
            "manager_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter manager name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department description",
                    "rows": 4,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }