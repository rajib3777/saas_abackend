from django.contrib import admin
from .models import Employee, AttendanceRecord


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'position', 'monthly_salary', 'is_active', 'join_date']
    list_filter = ['is_active', 'owner__subscription_type']
    search_fields = ['name', 'owner__email']


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'entry_time', 'exit_time', 'working_hours']
    list_filter = ['date']
    search_fields = ['employee__name']
