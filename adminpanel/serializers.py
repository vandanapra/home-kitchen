from rest_framework import serializers
from users.models import User
from sellers.models import SellerProfile
from orders.models import Order

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'mobile', 'email',
            'role', 'is_active', 'is_verified'
        )


class AdminSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = (
            'id', 'kitchen_name', 'is_active', 'avg_rating'
        )


class AdminOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
