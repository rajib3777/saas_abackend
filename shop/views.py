from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Product, StockEntry, Sale, Parcel, AdCampaign, CourierWithdrawal
from .serializers import (ProductSerializer, StockEntrySerializer,
                           SaleSerializer, ParcelSerializer, AdCampaignSerializer, CourierWithdrawalSerializer)


class IsActiveShopUser(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u.is_authenticated or not u.is_active_subscriber:
            return False
        # Moderators are sub-accounts tied to a shop admin
        if getattr(u, 'role', 'admin') == 'moderator':
            return True
        return u.subscription_type == 'shop'


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        return Product.objects.filter(owner=owner)

    def perform_create(self, serializer):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        serializer.save(owner=owner)


class StockEntryViewSet(viewsets.ModelViewSet):
    serializer_class = StockEntrySerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        return StockEntry.objects.filter(product__owner=owner)

    def perform_create(self, serializer):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        # Additional check to ensure the product belongs to the user
        product = serializer.validated_data.get('product')
        if product.owner != owner:
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
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        qs = Sale.objects.filter(product__owner=owner)
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
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        qs = Parcel.objects.filter(owner=owner)
        
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
            
        added_by = self.request.query_params.get('added_by')
        if added_by:
            qs = qs.filter(added_by_id=added_by)
            
        date_param = self.request.query_params.get('date')
        if date_param:
            qs = qs.filter(date=date_param)
            
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', 'admin') == 'moderator':
            serializer.save(owner=user.parent_admin, added_by=user)
        else:
            serializer.save(owner=user, added_by=user)

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
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        return AdCampaign.objects.filter(owner=owner)

    def perform_create(self, serializer):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        serializer.save(owner=owner)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Ad campaign recorded successfully"},
            status=status.HTTP_201_CREATED
        )

class CourierWithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = CourierWithdrawalSerializer
    permission_classes = [IsActiveShopUser]

    def get_queryset(self):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        qs = CourierWithdrawal.objects.filter(owner=owner).order_by('date')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        serializer.save(owner=owner)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Courier withdrawal recorded successfully"},
            status=status.HTTP_201_CREATED
        )
