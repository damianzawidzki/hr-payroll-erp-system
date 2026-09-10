"""
Attendance models for HRHub Pro.
"""

from datetime import datetime
from decimal import Decimal

from django.db import models

from employees.models import Employee


class Attendance(models.Model):
    """
    Stores daily employee attendance records.
    """

    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("SICK", "Sick"),
        ("HOLIDAY", "Holiday"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    date = models.DateField()

    clock_in = models.TimeField(
        blank=True,
        null=True,
    )

    clock_out = models.TimeField(
        blank=True,
        null=True,
    )

    break_minutes = models.PositiveIntegerField(
        default=0,
    )

    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
    )

    notes = models.TextField(
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
        ordering = ["-date", "employee__first_name", "employee__last_name"]
        unique_together = ["employee", "date"]
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """
        Calculate worked hours from clock in, clock out and break.
        """

        if self.clock_in and self.clock_out and self.status in ["PRESENT", "LATE"]:
            start_datetime = datetime.combine(self.date, self.clock_in)
            end_datetime = datetime.combine(self.date, self.clock_out)

            worked_seconds = (end_datetime - start_datetime).total_seconds()
            worked_hours = Decimal(str(worked_seconds / 3600))
            break_hours = Decimal(str(self.break_minutes / 60))

            calculated_hours = worked_hours - break_hours

            if calculated_hours < Decimal("0.00"):
                calculated_hours = Decimal("0.00")

            self.total_hours = calculated_hours.quantize(Decimal("0.01"))
        else:
            self.total_hours = Decimal("0.00")

        super().save(*args, **kwargs)