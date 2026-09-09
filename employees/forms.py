"""
Employee forms for HRHub Pro.
"""

from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    Form used by HR users to create and update employee records.
    """

    class Meta:
        model = Employee

        fields = [
            "user",
            "employee_number",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "date_of_birth",
            "job_title",
            "department",
            "manager",
            "employment_type",
            "hire_date",
            "salary",
            "status",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
        ]

        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "employee_number": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "manager": forms.Select(attrs={"class": "form-control"}),
            "employment_type": forms.Select(attrs={"class": "form-control"}),
            "hire_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }