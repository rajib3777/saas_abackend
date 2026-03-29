from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Employee, AttendanceRecord, WorkSetting
from .serializers import EmployeeSerializer, AttendanceRecordSerializer, WorkSettingSerializer
import datetime


from django.contrib.auth import get_user_model
User = get_user_model()

class IsActiveSubscriber(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active_subscriber

class WorkSettingViewSet(viewsets.ModelViewSet):
    serializer_class = WorkSettingSerializer
    permission_classes = [IsActiveSubscriber]

    def get_queryset(self):
        return WorkSetting.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        # Ensure a setting object always exists for the admin
        obj, created = WorkSetting.objects.get_or_create(owner=request.user)
        return Response(self.get_serializer(obj).data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
        employee = None
        if getattr(user, 'role', 'admin') == 'moderator':
            employee = user.employee_profile
        else:
            employee = serializer.validated_data.get('employee')
        
        if not employee:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Employee profile not found or not specified.")

        # Calculate is_late
        owner = employee.owner
        settings = WorkSetting.objects.filter(owner=owner).first()
        is_late = False
        if settings and serializer.validated_data.get('entry_time'):
            e_time = serializer.validated_data.get('entry_time')
            if e_time > settings.entry_cutoff_time:
                is_late = True
        
        serializer.save(employee=employee, is_late=is_late)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user
        if getattr(user, 'role', 'admin') != 'moderator':
            return Response({"error": "Only moderators can check out via this endpoint"}, status=403)
        
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            return Response({"error": "Employee profile not found"}, status=404)

        today = datetime.date.today()
        record = AttendanceRecord.objects.filter(employee=employee, date=today).first()
        if not record:
            return Response({"error": "No check-in found for today. Please check-in first."}, status=400)
        
        record.exit_time = datetime.datetime.now().time()
        record.save()
        return Response(AttendanceRecordSerializer(record).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        user = request.user
        employee_id = request.query_params.get('employee')
        month = int(request.query_params.get('month', datetime.date.today().month))
        year = int(request.query_params.get('year', datetime.date.today().year))

        if not employee_id:
            return Response({"error": "Employee ID is required"}, status=400)

        # Admin can view anyone, Moderator only themselves
        if getattr(user, 'role', 'admin') == 'moderator':
             try:
                 employee = Employee.objects.get(pk=employee_id, user_account=user)
             except Employee.DoesNotExist:
                 return Response({"error": "Access Denied"}, status=403)
        else:
             employee = Employee.objects.get(pk=employee_id, owner=user)

        records = AttendanceRecord.objects.filter(employee=employee, date__month=month, date__year=year)
        settings, _ = WorkSetting.objects.get_or_create(owner=employee.owner)
        off_days = settings.off_days
        
        data = []
        import calendar
        _, num_days = calendar.monthrange(year, month)
        
        total_ontime = 0
        total_late = 0
        total_miss = 0
        
        for day in range(1, num_days + 1):
            curr_date = datetime.date(year, month, day)
            date_str = curr_date.strftime('%Y-%m-%d')
            
            record = records.filter(date=curr_date).first()
            status_label = "none"
            is_holiday = date_str in off_days
            
            if record:
                if record.is_late:
                    status_label = "late"
                    total_late += 1
                else:
                    status_label = "ontime"
                    total_ontime += 1
            elif is_holiday:
                status_label = "off-day"
            elif curr_date < datetime.date.today():
                status_label = "miss"
                total_miss += 1
            
            data.append({
                "date": date_str,
                "status": status_label,
                "entry": record.entry_time if record else None,
                "exit": record.exit_time if record else None,
                "hours": record.working_hours if record else 0
            })

        return Response({
            "employee_name": employee.name,
            "period": f"{calendar.month_name[month]} {year}",
            "stats": {
                "ontime": total_ontime,
                "late": total_late,
                "miss": total_miss
            },
            "days": data
        })
