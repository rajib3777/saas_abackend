from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientPaymentViewSet

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='client')
router.register('payments', ClientPaymentViewSet, basename='client-payment')

urlpatterns = [path('', include(router.urls))]
