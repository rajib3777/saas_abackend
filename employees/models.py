from django.db import models
from accounts.models import User


class Employee(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.owner.email})"


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self.entry_time and self.exit_time:
            from datetime import datetime, date
            entry = datetime.combine(date.today(), self.entry_time)
            exit_ = datetime.combine(date.today(), self.exit_time)
            diff = exit_ - entry
            self.working_hours = round(diff.seconds / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"
