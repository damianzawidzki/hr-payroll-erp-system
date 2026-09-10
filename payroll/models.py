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

    gross_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    paye_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    national_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_deductions = models.DecimalField(
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

    def calculate_paye_tax(self):
        """
        Calculate simplified weekly PAYE income tax.
        """

        weekly_personal_allowance = Decimal("12570.00") / Decimal("52.00")
        basic_rate_limit_weekly = Decimal("50270.00") / Decimal("52.00")

        taxable_pay = self.gross_pay - weekly_personal_allowance

        if taxable_pay <= Decimal("0.00"):
            return Decimal("0.00")

        basic_band = basic_rate_limit_weekly - weekly_personal_allowance

        if taxable_pay <= basic_band:
            return taxable_pay * Decimal("0.20")

        basic_tax = basic_band * Decimal("0.20")
        higher_tax = (taxable_pay - basic_band) * Decimal("0.40")

        return basic_tax + higher_tax

    def calculate_national_insurance(self):
        """
        Calculate simplified weekly employee National Insurance.
        """

        primary_threshold_weekly = Decimal("242.00")
        upper_earnings_limit_weekly = Decimal("967.00")

        if self.gross_pay <= primary_threshold_weekly:
            return Decimal("0.00")

        main_band = min(self.gross_pay, upper_earnings_limit_weekly) - primary_threshold_weekly
        main_ni = main_band * Decimal("0.08")

        additional_ni = Decimal("0.00")

        if self.gross_pay > upper_earnings_limit_weekly:
            additional_ni = (self.gross_pay - upper_earnings_limit_weekly) * Decimal("0.02")

        return main_ni + additional_ni

    def save(self, *args, **kwargs):
        """
        Calculate weekly gross pay, statutory deductions and net pay before saving.
        """

        standard_pay = self.hours_worked * self.hourly_rate
        overtime_pay = self.overtime_hours * self.overtime_rate

        self.gross_pay = standard_pay + overtime_pay + self.bonus

        self.paye_tax = self.calculate_paye_tax().quantize(Decimal("0.01"))
        self.national_insurance = self.calculate_national_insurance().quantize(
            Decimal("0.01")
        )

        self.total_deductions = (
            self.paye_tax + self.national_insurance + self.other_deductions
        ).quantize(Decimal("0.01"))

        self.net_pay = self.gross_pay - self.total_deductions

        if self.net_pay < Decimal("0.00"):
            self.net_pay = Decimal("0.00")

        self.gross_pay = self.gross_pay.quantize(Decimal("0.01"))
        self.net_pay = self.net_pay.quantize(Decimal("0.01"))

        super().save(*args, **kwargs)