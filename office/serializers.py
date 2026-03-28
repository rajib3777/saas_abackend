from rest_framework import serializers
from .models import Client, ClientPayment


class ClientPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPayment
        fields = ['id', 'client', 'amount', 'note', 'date']
        read_only_fields = ['date']


class ClientSerializer(serializers.ModelSerializer):
    due_amount = serializers.ReadOnlyField()
    payments = ClientPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'service', 'total_amount',
                  'paid_amount', 'due_amount', 'payments', 'created_at']
        read_only_fields = ['paid_amount', 'created_at']
