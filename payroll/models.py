"""
Payroll models for HRHub Pro.
"""

from django.db import models

from employees.models import Employee


class Payslip(models.Model):
    """
    Stores employee payslip records.
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

    pay_period_start = models.DateField()

    pay_period_end = models.DateField()

    payment_date = models.DateField(
        blank=True,
        null=True,
    )

    gross_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    net_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
        ordering = ["-pay_period_end"]
        verbose_name = "Payslip"
        verbose_name_plural = "Payslips"

    def __str__(self):
        return f"{self.employee.full_name} - {self.pay_period_start} to {self.pay_period_end}"