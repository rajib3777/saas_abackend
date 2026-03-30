from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'business_name', 'subscription_type', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    employee_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'business_name', 'subscription_type',
                  'is_active_subscriber', 'date_joined', 'role', 'parent_admin', 'employee_id']

    def get_employee_id(self, obj):
        if hasattr(obj, 'employee_profile'):
            return obj.employee_profile.id
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
