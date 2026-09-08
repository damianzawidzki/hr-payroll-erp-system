"""
Attendance models for HRHub Pro.
"""

from django.db import models

from employees.models import Employee


class Attendance(models.Model):
    """
    Stores one attendance record for one employee on one date.
    """

    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("REMOTE", "Remote"),
        ("SICK", "Sick"),
        ("ON_LEAVE", "On Leave"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    date = models.DateField()

    check_in_time = models.TimeField(
        blank=True,
        null=True,
    )

    check_out_time = models.TimeField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
    )

    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
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
        ordering = ["-date", "employee__last_name"]
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        unique_together = ["employee", "date"]

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"