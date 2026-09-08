"""
Attendance forms for HRHub Pro.
"""

from django import forms

from .models import Attendance


class AttendanceForm(forms.ModelForm):
    """
    Form used to create and update attendance records.
    """

    class Meta:
        model = Attendance

        fields = [
            "employee",
            "date",
            "check_in_time",
            "check_out_time",
            "status",
            "total_hours",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "check_in_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "check_out_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "total_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.25",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }