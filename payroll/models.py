"""
Payroll models for HRHub Pro.
"""

from decimal import Decimal

from django.db import models

from employees.models import Employee


class Payslip(models.Model):
    """
    Stores weekly employee payslip records.
    """

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ISSUED", "Issued"),
        ("PAID", "Paid"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payslips",
    )

    week_start = models.DateField()

    week_end = models.DateField()

    payment_date = models.DateField(
        blank=True,
        null=True,
    )

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    hours_worked = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    overtime_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gross_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    net_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
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
        ordering = ["-week_start"]
        verbose_name = "Weekly Payslip"
        verbose_name_plural = "Weekly Payslips"

    def __str__(self):
        return f"{self.employee.full_name} - {self.week_start} to {self.week_end}"

    def save(self, *args, **kwargs):
        """
        Calculate weekly gross and net pay before saving.
        """

        standard_pay = self.hours_worked * self.hourly_rate
        overtime_pay = self.overtime_hours * self.overtime_rate

        self.gross_pay = standard_pay + overtime_pay + self.bonus
        self.net_pay = self.gross_pay - self.deductions

        if self.net_pay < Decimal("0.00"):
            self.net_pay = Decimal("0.00")

        super().save(*args, **kwargs)