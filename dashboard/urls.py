from django.urls import path
from .views import DashboardView, SalesChartView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('chart/sales/', SalesChartView.as_view(), name='sales-chart'),
]
