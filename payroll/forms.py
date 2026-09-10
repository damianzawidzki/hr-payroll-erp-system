"""
Payroll forms for HRHub Pro.
"""

from django import forms

from .models import Payslip


class PayslipForm(forms.ModelForm):
    """
    Form used by HR users to create and update weekly payslips.
    """

    class Meta:
        model = Payslip

        fields = [
            "employee",
            "week_start",
            "week_end",
            "payment_date",
            "hourly_rate",
            "hours_worked",
            "overtime_hours",
            "overtime_rate",
            "bonus",
            "deductions",
            "status",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "week_start": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "week_end": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Hourly rate",
                }
            ),
            "hours_worked": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Standard hours",
                }
            ),
            "overtime_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Overtime hours",
                }
            ),
            "overtime_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Overtime rate",
                }
            ),
            "bonus": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Bonus",
                }
            ),
            "deductions": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Deductions",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Payroll notes",
                }
            ),
        }