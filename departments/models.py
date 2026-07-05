from django.db import models

# Create your models here.
class Department(models.Model):
    """
    This model stores company departments.
    
    In a real HR system, every employee belongs to a department.
    Examples: Human Resources, Finance, IT, Marketing, Sales, etc.
    """

    name = models.CharField(max_length=100, unique=True)
    manager_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name