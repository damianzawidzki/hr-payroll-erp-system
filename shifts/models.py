"""
Shift models for HRHub Pro.
"""

from django.db import models

from employees.models import Employee

class Shift(models.Model):
    """
    Stores planned emplyee work shifts.
    """
    SHIFT_TYPE_CHOICES = [
        ("MORNING", "Morning"),
        ("AFTERNOON", "Afternoon"),
        ("NIGHT", "Night"),
        ("CUSTOM", "Custom"),
    ]

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="shifts",      
    )

    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        default="MORNING",
    )

    shift_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(
        max_length = 150,
        blank=True,
        null=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SCHEDULED",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["shift_date", "start_time"]
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"

    def __str__(self):
        return f"{self.employee.full_name} - {self.shift_date} on {self.start_time}"