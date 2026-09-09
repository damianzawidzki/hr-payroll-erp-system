"""
Leave management forms for HRHub Pro.
"""

from django import forms

from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    """
    Form used by HR users to create and update leave requests.
    """

    class Meta:
        model = LeaveRequest

        fields = [
            "employee",
            "leave_type",
            "duration",
            "start_date",
            "end_date",
            "reason",
            "status",
            "manager_comment",
        ]

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "leave_type": forms.Select(attrs={"class": "form-control"}),
            "duration": forms.Select(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "manager_comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class EmployeeLeaveRequestForm(forms.ModelForm):
    """
    Form used by employees to submit their own leave requests.
    """

    class Meta:
        model = LeaveRequest

        fields = [
            "leave_type",
            "duration",
            "start_date",
            "end_date",
            "reason",
        ]

        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-control"}),
            "duration": forms.Select(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Reason",
                }
            ),
        }


class LeaveDecisionForm(forms.ModelForm):
    """
    Form used to approve or reject leave requests.
    """

    class Meta:
        model = LeaveRequest

        fields = [
            "manager_comment",
        ]

        widgets = {
            "manager_comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Manager message",
                }
            ),
        }