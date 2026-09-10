"""
Payroll forms for HRHub Pro.
"""

from django import forms

from employees.models import Employee

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
            "other_deductions",
            "status",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "week_start": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "week_end": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "payment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "hourly_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "overtime_hours": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "overtime_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "bonus": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "other_deductions": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class GenerateWeeklyPayslipsForm(forms.Form):
    """
    Form used by HR users to generate weekly payslips from attendance.
    """

    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        required=True,
    )

    week_start = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    week_end = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    payment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    hourly_rate = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial="11.44",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    standard_weekly_hours = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        initial="40.00",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    overtime_rate = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial="17.16",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    bonus = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial="0.00",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    other_deductions = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial="0.00",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    status = forms.ChoiceField(
        choices=[
            ("DRAFT", "Draft"),
            ("ISSUED", "Issued"),
            ("PAID", "Paid"),
        ],
        initial="ISSUED",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Update existing payslips if they already exist",
    )

    notes = forms.CharField(
        required=False,
        initial="Generated from weekly attendance records.",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        employee_queryset = kwargs.pop("employee_queryset", Employee.objects.all())

        super().__init__(*args, **kwargs)

        self.fields["employees"].queryset = employee_queryset

    def clean(self):
        """
        Validate the selected payroll week.
        """

        cleaned_data = super().clean()

        week_start = cleaned_data.get("week_start")
        week_end = cleaned_data.get("week_end")

        if week_start and week_end and week_end < week_start:
            raise forms.ValidationError("Week end cannot be before week start.")

        return cleaned_data