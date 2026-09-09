"""

"""

from django import forms
from .models import Shift

class ShiftForm(forms.ModelForm):
    """
    Form use byHR users to create and update employee shifts.
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
            "notes",
            "status"
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "shift_type": forms.Select(attrs={"class": "form-control"}),
            "shift_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter location"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Shift notes"}),
            "status": forms.Select(attrs={"class": "form-control"}),    

        }