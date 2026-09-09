"""
Leave management models for HRHub Pro.
"""

from decimal import Decimal

from django.db import models

from employees.models import Employee


class LeaveRequest(models.Model):
    """
    Stores employee absence requests.
    """

    LEAVE_TYPE_CHOICES = [
        ("ANNUAL", "Annual Leave"),
        ("SICK", "Sick Leave"),
        ("UNPAID", "Unpaid Leave"),
        ("EMERGENCY", "Emergency Leave"),
        ("MATERNITY", "Maternity Leave"),
        ("PATERNITY", "Paternity Leave"),
    ]

    DURATION_CHOICES = [
        ("FULL_DAY", "Full Day"),
        ("AM", "AM"),
        ("PM", "PM"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
    )

    duration = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default="FULL_DAY",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    manager_comment = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_leave_type_display()}"

    @property
    def total_days(self):
        """
        Returns total leave days.

        Full day counts as 1 day.
        AM and PM count as 0.5 day.
        """

        days = (self.end_date - self.start_date).days + 1

        if self.duration in ["AM", "PM"]:
            return Decimal("0.5")

        return Decimal(days)