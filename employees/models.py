"""
Employee models for HRHub Pro.
"""

from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    """
    Stores employee personal, employment and management details.
    """

    EMPLOYMENT_TYPE_CHOICES = [
        ("FULL_TIME", "Full Time"),
        ("PART_TIME", "Part Time"),
        ("CONTRACT", "Contract"),
        ("TEMPORARY", "Temporary"),
        ("AGENCY", "Agency"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("ON_LEAVE", "On Leave"),
        ("TERMINATED", "Terminated"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employee_profile",
    )

    employee_number = models.CharField(
        max_length=30,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField(
        unique=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    job_title = models.CharField(
        max_length=150,
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="team_members",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="FULL_TIME",
    )

    hire_date = models.DateField()

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )

    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    emergency_contact_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
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
        ordering = ["first_name", "last_name"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.full_name} ({self.employee_number})"

    @property
    def full_name(self):
        """
        Return the employee full name.
        """

        return f"{self.first_name} {self.last_name}"