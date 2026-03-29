from rest_framework import serializers
from .models import Employee, AttendanceRecord


class EmployeeSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    has_account = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'phone', 'position', 'monthly_salary', 'join_date', 'is_active', 'is_moderator', 'email', 'password', 'has_account']
        read_only_fields = ['join_date', 'has_account']

    def get_has_account(self, obj):
        return obj.user_account is not None


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'employee', 'employee_name', 'date', 'entry_time', 'exit_time', 'working_hours', 'location', 'message']
        read_only_fields = ['working_hours']
