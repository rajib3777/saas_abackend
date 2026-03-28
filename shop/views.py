from rest_framework import viewsets, permissions
from .models import Product, StockEntry, Sale, Parcel, AdCampaign
from .serializers import (ProductSerializer, StockEntrySerializer,
                           SaleSerializer, ParcelSerializer, AdCampaignSerializer)


class IsActiveShopUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.is_active_subscriber and
                request.user.subscription_type == 'shop')


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StockEntryViewSet(viewsets.ModelViewSet):
    serializer_class = StockEntrySerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        return StockEntry.objects.filter(product__owner=self.request.user)


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        qs = Sale.objects.filter(product__owner=self.request.user)
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs


class ParcelViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        qs = Parcel.objects.filter(owner=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AdCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = AdCampaignSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        return AdCampaign.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
