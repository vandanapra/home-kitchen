from rest_framework import serializers
from .models import Order, OrderItem
from sellers.models import MenuItem, SellerProfile
from django.utils import timezone

# class OrderItemSerializer(serializers.ModelSerializer):
#     item_name = serializers.CharField(
#         source="menu_item.name", read_only=True
#     )
#     price = serializers.DecimalField(
#         source="menu_item.price", read_only=True, max_digits=6, decimal_places=2
#     )
#     # 👇 WRITE-ONLY for create
#     menu_item_id = serializers.PrimaryKeyRelatedField(
#         source="menu_item",
#         queryset=MenuItem.objects.all(),
#         write_only=True
#     )
#     class Meta:
#         model = OrderItem
#         fields = ["id", "item_name","price", "quantity","menu_item_id"]


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
#     # 👇 write-only seller id
#     seller_id = serializers.PrimaryKeyRelatedField(source="seller",queryset=SellerProfile.objects.all(),write_only=True)
#     class Meta:
#         model = Order
#         fields = ('id', 'seller_id', 'total_amount', 'status', 'items','created_at')
#         read_only_fields = ("total_amount", "status")
        
#     def create(self, validated_data):
#         items_data = validated_data.pop("items")
#         request = self.context["request"]
#         today = timezone.now().date()

#         seller = validated_data["seller"]

#         # 🚫 Prevent duplicate order per day
#         if Order.objects.filter(
#             customer=request.user,
#             seller=seller,
#             order_date=today
#         ).exists():
#             raise serializers.ValidationError(
#                 "Order already placed for today"
#             )

#         order = Order.objects.create(
#             customer=request.user,
#             seller=seller,
#             status="PENDING",
#             total_amount=0
#         )

#         total = 0
#         for item in items_data:
#             menu_item = item["menu_item"]
#             qty = item.get("quantity", 1)

#             OrderItem.objects.create(
#                 order=order,
#                 menu_item=menu_item,
#                 quantity=qty
#             )

#             total += menu_item.price * qty

#         order.total_amount = total
#         order.save()

#         return order


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

    class Meta:
        model = Order
        fields = [
            "id",
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

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "customer_mobile",
            "status",
            "total_amount",
            "items",
            "created_at",
        ]
