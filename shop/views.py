from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
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

    def perform_create(self, serializer):
        # Additional check to ensure the product belongs to the user
        product = serializer.validated_data.get('product')
        if product.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this product.")
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Targeted fix: avoid returning serializer.data to prevent serialization crashes
        return Response(
            {"status": "success", "message": "Stock updated successfully"},
            status=status.HTTP_201_CREATED
        )


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Sale recorded successfully"},
            status=status.HTTP_201_CREATED
        )


class ParcelViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        qs = Parcel.objects.filter(owner=self.request.user)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Parcel recorded successfully"},
            status=status.HTTP_201_CREATED
        )


class AdCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = AdCampaignSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        return AdCampaign.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Ad campaign recorded successfully"},
            status=status.HTTP_201_CREATED
        )
