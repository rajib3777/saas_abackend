from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, AttendanceViewSet

router = DefaultRouter()
router.register('list', EmployeeViewSet, basename='employee')
router.register('attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [path('', include(router.urls))]
