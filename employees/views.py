from rest_framework import viewsets, permissions
from .models import Employee, AttendanceRecord
from .serializers import EmployeeSerializer, AttendanceRecordSerializer


from django.contrib.auth import get_user_model
User = get_user_model()

class IsActiveSubscriber(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active_subscriber

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsActiveSubscriber]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', 'admin') == 'moderator':
            return Employee.objects.filter(user_account=user)
        return Employee.objects.filter(owner=user)

    def perform_create(self, serializer):
        is_moderator = serializer.validated_data.pop('is_moderator', False)
        email = serializer.validated_data.pop('email', None)
        password = serializer.validated_data.pop('password', None)
        
        employee = serializer.save(owner=self.request.user)

        if is_moderator and email and password:
            user_account = User.objects.create_user(
                email=email,
                password=password,
                full_name=employee.name,
                business_name=self.request.user.business_name,
                role='moderator',
                parent_admin=self.request.user,
                is_active_subscriber=True,
                subscription_type='shop'
            )
            employee.user_account = user_account
            employee.save()


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsActiveSubscriber]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', 'admin') == 'moderator':
            qs = AttendanceRecord.objects.filter(employee__user_account=user)
        else:
            qs = AttendanceRecord.objects.filter(employee__owner=user)
        employee_id = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', 'admin') == 'moderator':
            serializer.save(employee=user.employee_profile)
        else:
            serializer.save()
