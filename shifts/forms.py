"""
Shift forms for HRHub Pro.
"""

from django import forms

from employees.models import Employee
from .models import Shift


class ShiftForm(forms.ModelForm):
    """
    Form used to create and update a single shift.
    """

    class Meta:
        model = Shift

        fields = [
            "employee",
            "shift_type",
            "shift_date",
            "start_time",
            "end_time",
            "location",
            "status",
            "notes",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "shift_type": forms.Select(attrs={"class": "form-control"}),
            "shift_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class BulkShiftForm(forms.Form):
    """
    Form used to create shifts for multiple employees and multiple days.
    """

    WEEKDAY_CHOICES = [
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday"),
    ]

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

    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        required=True,
        initial=["0", "1", "2", "3", "4"],
    )

    shift_type = forms.ChoiceField(
        choices=Shift.SHIFT_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="MORNING",
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
                "type": "time",
            }
        ),
        initial="08:00",
    )

    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
                "type": "time",
            }
        ),
        initial="16:00",
    )

    location = forms.CharField(
        max_length=150,
        required=False,
        initial="Warehouse",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    status = forms.ChoiceField(
        choices=Shift.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="SCHEDULED",
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    overwrite_existing = forms.BooleanField(
        required=False,
        initial=True,
        label="Update existing shifts if they already exist",
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