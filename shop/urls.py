from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, StockEntryViewSet, SaleViewSet, ParcelViewSet, AdCampaignViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('stock', StockEntryViewSet, basename='stock')
router.register('sales', SaleViewSet, basename='sale')
router.register('parcels', ParcelViewSet, basename='parcel')
router.register('ads', AdCampaignViewSet, basename='ad')

urlpatterns = [path('', include(router.urls))]
