"""
Attendance forms for HRHub Pro.
"""

from django import forms

from employees.models import Employee

from .models import Attendance


class AttendanceForm(forms.ModelForm):
    """
    Form used by Admin, HR and Manager users to create attendance records.
    """

    class Meta:
        model = Attendance

        fields = [
            "employee",
            "date",
            "clock_in",
            "clock_out",
            "break_minutes",
            "status",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "clock_in": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "clock_out": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "break_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def clean(self):
        """
        Validate attendance time fields.
        """

        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        clock_in = cleaned_data.get("clock_in")
        clock_out = cleaned_data.get("clock_out")

        if status in ["PRESENT", "LATE"]:
            if not clock_in:
                self.add_error("clock_in", "Clock in time is required.")

            if not clock_out:
                self.add_error("clock_out", "Clock out time is required.")

        return cleaned_data


class GenerateAttendanceForm(forms.Form):
    """
    Form used to generate attendance records from scheduled shifts.
    """

    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        required=True,
    )

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )

    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )

    status = forms.ChoiceField(
        choices=[
            ("PRESENT", "Present"),
            ("LATE", "Late"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="PRESENT",
    )

    break_minutes = forms.IntegerField(
        min_value=0,
        initial=30,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "step": "1",
            }
        ),
    )

    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Update existing attendance if it already exists",
    )

    notes = forms.CharField(
        required=False,
        initial="Generated from scheduled shift.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        employee_queryset = kwargs.pop("employee_queryset", Employee.objects.all())

        super().__init__(*args, **kwargs)

        self.fields["employees"].queryset = employee_queryset

    def clean(self):
        """
        Validate date range.
        """

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")

        return cleaned_data