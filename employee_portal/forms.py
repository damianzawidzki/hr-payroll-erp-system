"""
Employee portal forms for HRHub Pro.
"""

from django import forms

from employees.models import Employee


class EmployeeProfileForm(forms.ModelForm):
    """
    Form used by employees to update their own contact details.
    """

    class Meta:
        model = Employee

        fields = [
            "email",
            "phone",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email address",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone number",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Home address",
                }
            ),
            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency contact name",
                }
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency contact phone",
                }
            ),
        }