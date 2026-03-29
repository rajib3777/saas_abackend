from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, AttendanceViewSet, WorkSettingViewSet

router = DefaultRouter()
router.register('list', EmployeeViewSet, basename='employee')
router.register('attendance', AttendanceViewSet, basename='attendance')
router.register('settings', WorkSettingViewSet, basename='work-settings')

urlpatterns = [path('', include(router.urls))]
