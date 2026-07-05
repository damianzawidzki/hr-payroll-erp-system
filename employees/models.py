from django.db import models
from django.contrib.auth.models import User
from departments.models import Department


class Employee(models.Model):
    """
    This model stores employee profile information.

    The Django User model is used for login access.
    The Employee model stores HR information such as job title,
    department, salary, employment type and employee status.
    """

    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
        ('TEMPORARY', 'Temporary'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('SICK', 'Sick'),
        ('TERMINATED', 'Terminated'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        blank=True,
        null=True
    )

    employee_number = models.CharField(max_length=20, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)

    job_title = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name='employees',
        blank=True,
        null=True
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='FULL_TIME'
    )

    hire_date = models.DateField()

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Employee base monthly salary.'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.employee_number}'

    @property
    def full_name(self):
        """
        This property returns the full employee name.
        It will be useful later in templates, payroll and reports.
        """
        return f'{self.first_name} {self.last_name}'