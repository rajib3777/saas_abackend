from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
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
        added_by = user
        owner = user.parent_admin if getattr(user, 'role', 'admin') == 'moderator' else user
        
        # Initiate tracking if it is Steadfast
        courier_name = serializer.validated_data.get('courier_name', '').lower()
        tracking_number = serializer.validated_data.get('tracking_number', '')
        
        is_auto_tracking = False
        next_check = None
        
        if 'steadfast' in courier_name and tracking_number:
            is_auto_tracking = True
            from django.utils import timezone
            from datetime import timedelta
            next_check = timezone.now() + timedelta(minutes=10)
            
        serializer.save(
            owner=owner, 
            added_by=added_by,
            is_auto_tracking=is_auto_tracking,
            next_check=next_check
        )

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


class CronTrackView(APIView):
    """
    Serverless Cron endpoint for Vercel.
    Vercel calls this URL every 1 minute automatically via vercel.json crons config.
    Protected by CRON_SECRET header to prevent unauthorized access.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Security check: validate Authorization header
        cron_secret = getattr(settings, 'CRON_SECRET', '')
        auth_header = request.headers.get('Authorization', '')
        expected = f'Bearer {cron_secret}'

        if cron_secret and auth_header != expected:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Run the tracking logic synchronously
        from .tasks import track_due_parcels
        result = track_due_parcels()
        return Response({'status': 'ok', 'result': result})
