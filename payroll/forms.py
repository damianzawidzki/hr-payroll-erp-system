"""
Payroll forms for HRHub Pro.
"""

from django import forms

from .models import Payslip


class PayslipForm(forms.ModelForm):
    """
    Form used by HR users to create and update payslips.
    """

    class Meta:
        model = Payslip

        fields = [
            "employee",
            "pay_period_start",
            "pay_period_end",
            "payment_date",
            "gross_pay",
            "deductions",
            "net_pay",
            "status",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "pay_period_start": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "pay_period_end": forms.DateInput(
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
            "gross_pay": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "deductions": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "net_pay": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
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