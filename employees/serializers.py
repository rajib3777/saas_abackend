from rest_framework import serializers
from .models import Employee, AttendanceRecord


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'phone', 'position', 'monthly_salary', 'join_date', 'is_active']
        read_only_fields = ['join_date']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'employee', 'employee_name', 'date', 'entry_time', 'exit_time', 'working_hours']
        read_only_fields = ['working_hours']
