from rest_framework import serializers
from .models import Product, StockEntry, Sale, Parcel, AdCampaign, CourierWithdrawal


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'buying_price', 'selling_price', 'stock', 'created_at']
        read_only_fields = ['stock', 'created_at']


class StockEntrySerializer(serializers.ModelSerializer):
    note = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = StockEntry
        fields = ['id', 'product', 'quantity', 'date', 'note']
        read_only_fields = ['date']


class SaleSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'product', 'product_name', 'quantity', 'selling_price',
                  'buying_price', 'profit', 'date']
        read_only_fields = ['date', 'profit']


class ParcelSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()
    added_by_name = serializers.CharField(source='added_by.full_name', read_only=True)

    class Meta:
        model = Parcel
        fields = ['id', 'courier_name', 'tracking_number', 'customer_name',
                  'cost_price', 'selling_price', 'profit', 'status', 'date', 'added_by', 'added_by_name',
                  'is_auto_tracking', 'next_check', 'last_sync_time', 'last_sync_status']
        read_only_fields = ['date', 'profit', 'added_by_name', 'next_check', 'last_sync_time', 'last_sync_status']


class AdCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCampaign
        fields = ['id', 'name', 'platform', 'start_date', 'end_date', 'total_spend', 'revenue', 'created_at']
        read_only_fields = ['created_at']

class CourierWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierWithdrawal
        fields = ['id', 'courier_name', 'amount', 'date', 'created_at']
        read_only_fields = ['created_at']
