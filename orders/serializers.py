from rest_framework import serializers
from .models import Order, OrderItem
from sellers.models import MenuItem, SellerProfile
from django.utils import timezone


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(
        source="menu_item.name", read_only=True
    )
    price = serializers.DecimalField(
        source="menu_item.price",
        read_only=True,
        max_digits=6,
        decimal_places=2
    )

    class Meta:
        model = OrderItem
        fields = ["id", "item_name", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        source="orderitem_set",
        read_only=True
    )
    seller_name = serializers.CharField(
        source="seller.kitchen_name",
        read_only=True
    )
    order_date = serializers.DateField()
    day = serializers.CharField()
    customer_name = serializers.CharField(source="customer.name")


    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "day",
            "payment_method",
            "paid_amount",
            "order_date",
            "seller_name",
            "total_amount",
            "status",
            "items",
            "created_at"
        ]
        
class SellerOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    customer_mobile = serializers.CharField(
        source="customer.mobile", read_only=True
    )
    items = OrderItemSerializer(
        many=True, source="orderitem_set"
    )
    order_date = serializers.DateField()
    day = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "customer_mobile",
            "day",           # ✅ ADDED
            "order_date",    # ✅ ADDED
            "status",
            "total_amount",
            "items",
            "created_at",
        ]
